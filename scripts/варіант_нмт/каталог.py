# -*- coding: utf-8 -*-
"""Каталог завдань для генератора варіантів: кожне унікальне завдання бази з метаданими.

Для кожного завдання: теми, тип, рік, звідки воно (сесія й номер -- для 2026 з коментаря,
для 2023--2025 зіставленням із PDF «НМТ 2023--2025»), довідкові ключі (офіційний 2026,
таблиця PDF 2024--2025, ключі тематичних збірників) і категорія слота. Відповіді, категорії,
складність і позначки дефектів, які вже є в каталозі, зберігаються при повторному запуску.
LaTeX-код у каталог не пишеться -- його беруть із файлів тем за id.

    python3 scripts/варіант_нмт/каталог.py            # оновити scripts/data/варіант_каталог.json
    python3 scripts/варіант_нмт/каталог.py --пакети DIR 12   # + пакети завдань для розв'язування агентами
"""
import os, re, sys, json, difflib, collections, importlib.util
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from спільне import *

PDF_JSON = os.path.join(DATA, "завдання_з_pdf_2023_2025.json")
PDF_KEYS = os.path.join(DATA, "ключі_pdf_2024_2025.json")
ORIG_2026 = os.path.join(DATA, "originals_2026.json")

# поля, які заповнює розв'язування/перевірка -- при оновленні каталогу не губляться
ЗБЕРІГАТИ = ("відповідь", "джерело_відповіді", "категорія", "складність", "дефект", "примітка", "розвʼязок", "перевірено", "рисунок_огляд")


# ---------------------------------------------------------------- довідкові дані
def refs_2026(b):
    m = re.search(r"%\s*НМТ 2026, сесія ([\d.]+), завдання №(\d+)", b)
    return "2026-%s-%02d" % (m.group(1), int(m.group(2))) if m else None


def pdf_matches(tasks):
    """PDF-завдання -> завдання бази (той самий алгоритм, що й у звірці покриття)"""
    D = os.path.join(ROOT, "scripts", "звірка_pdf_2023_2025")
    sys.path.insert(0, D)
    import final_match
    from compare import sig as csig
    base_list = [dict(topic=t["теми"][0], year=t["рік"] or "?", raw=t["блок"], sig=csig(t["блок"])) for t in tasks]
    final_match.load_base = lambda: [dict(b) for b in base_list]
    base, inv = final_match.prep_base()
    out = collections.defaultdict(list)
    for p in json.load(open(PDF_JSON, encoding="utf-8")):
        b = final_match.evaluate(p["text"], base, inv, p["year"])
        if b and b["ev"]:
            out[b["i"]].append(dict(рік=p["year"], сесія=p["session"], номер=int(float(p["n"])), conf=b["conf"], ev=b["ev"], текст=p["text"]))
    return out


def map_key_single(key_letter, pdf_text, block):
    """літера ключа PDF -> літера в порядку варіантів бази (варіанти могли переставити)"""
    D = os.path.join(ROOT, "scripts", "звірка_pdf_2023_2025"); sys.path.insert(0, D)
    from opts import pdf_options, base_options
    po, bo = pdf_options(pdf_text), base_options(block)
    L = "АБВГД"
    if key_letter not in L: return None, "не літера"
    if len(po) == 5 and len(bo) == 5 and all(po) and all(bo):
        if po == bo: return key_letter, "варіанти в тому самому порядку"
        target = po[L.index(key_letter)]
        hits = [i for i, x in enumerate(bo) if x == target]
        if len(hits) == 1: return L[hits[0]], "за змістом варіанта"
        # нечіткий збіг тут не годиться: «20 см» і «25 см» схожі як рядки, але це різні відповіді
        return None, "варіант ключа не знайдено серед варіантів бази"
    return None, "варіанти не розпізнано"


# ---------------------------------------------------------------- орієнтовна категорія (правила)
UNIT_CAT_SINGLE = {
    "1": "арифметика", "2": "арифметика", "3": "вирази", "4": "вирази", "5": "вирази", "7": "вирази",
    "6": "рівняння", "8": "рівняння", "9": "рівняння", "22": "рівняння", "23": "рівняння",
    "27": "рівняння_трансц", "28a": "рівняння_трансц", "31": "рівняння_трансц",
    "19": "нерівність", "29": "нерівність", "32": "нерівність",
    "20": "функція", "21": "функція", "28b": "функція", "30b": "функція",
    "24": "похідна_прогресія", "25": "похідна_прогресія", "33": "похідна_прогресія", "34": "похідна_прогресія",
    "26": "тригонометрія", "30a": "вирази", "37": "статистика", "35": "комбінаторика_ймовірність", "36": "комбінаторика_ймовірність",
    "10": "планіметрія_проста", "11": "планіметрія_обчислення", "12": "планіметрія_обчислення", "13": "планіметрія_обчислення",
    "14": "планіметрія_обчислення", "15": "планіметрія_обчислення", "16": "планіметрія_обчислення", "17": "планіметрія_обчислення",
    "18": "координати_вектори", "38": "стерео_тест", "39": "стерео_тест", "40": "стерео_тест", "41": "стерео_тест", "42": "стерео_тест",
    "43": "кв_параметр",
}
PLAN = {"10", "11", "12", "13", "14", "15", "16", "17"}
FUNC = {"20", "21", "28b", "30b", "33", "34", "24", "25"}
STEREO = {"18", "38", "39", "40", "41", "42"}


def rule_category(t):
    u, k, b = t["теми"][0], t["тип"], re.sub(r"%[^\n]*", "", t["блок"])
    if k == "matching":
        if u in PLAN: return "відп_планіметрія"
        if u in FUNC or re.search(r"функці|графік", b): return "відп_функції"
        return "відп_вирази"
    if k == "input":
        if u == "43" or "параметр" in b: return "кв_параметр"
        if u in STEREO: return "кв_стерео"
        if u in FUNC | {"20", "21"}: return "кв_функціональне"
        if u in {"35", "36", "37", "2"}: return "кв_ймовірність_статистика"
        return "інше"
    c = UNIT_CAT_SINGLE.get(u, "інше")
    if u in PLAN and re.search(r"тверджен|правильн\w* є|неправильн", b): return "планіметрія_твердження"
    return c


# ---------------------------------------------------------------- каталог
def зібрати(verbose=True):
    tasks = завдання_бази()
    orig = {t["id"]: t for t in json.load(open(ORIG_2026, encoding="utf-8"))}
    pkeys = json.load(open(PDF_KEYS, encoding="utf-8")) if os.path.exists(PDF_KEYS) else {}
    ckeys = {}
    for f in os.listdir(DATA):
        if f.startswith("відповіді_") and f.endswith(".json"):
            for k, v in json.load(open(os.path.join(DATA, f), encoding="utf-8")).items(): ckeys[k] = (v, f)
    pm = pdf_matches(tasks) if os.path.exists(PDF_JSON) else {}
    cat = []
    for i, t in enumerate(tasks):
        rec = dict(id=t["id"], теми=t["теми"], тип=t["тип"], рік=t["рік"], ключ=t["ключ"][:60],
                   рисунок=bool(re.search(r"tikzpicture|includegraphics|\\begin\{axis\}", t["блок"])), орієнтовна_категорія=rule_category(t))
        refs = []
        o = refs_2026(t["блок"])
        if o:
            rec["сесія_2026"] = o
            a = orig.get(o, {}).get("answer")
            if a: refs.append(dict(джерело="офіційний ключ 2026", відповідь=норм_відповідь(a, t["тип"]), сире=a))
        for p in sorted(pm.get(i, []), key=lambda x: -x["conf"]):
            r = dict(джерело="PDF %s" % p["сесія"], сесія=p["сесія"], номер=p["номер"], рік_pdf=p["рік"])
            kk = pkeys.get(p["сесія"], {}).get(str(p["номер"]))
            if kk:
                r["сире"] = kk
                if t["тип"] == "single":
                    lt, how = map_key_single(норм_відповідь(kk, "single") or "", p["текст"], t["блок"])
                    r["відповідь"], r["як"] = lt, how
                else:
                    r["відповідь"] = норм_відповідь(kk, t["тип"]); r["як"] = "як у PDF (порядок пунктів не звірено)" if t["тип"] == "matching" else "число"
            refs.append(r)
        if t["старий_id"] in ckeys:                       # ключі збірників записано за підписом sig()
            v, f = ckeys[t["старий_id"]]
            refs.append(dict(джерело="збірник " + f, відповідь=норм_відповідь(v, t["тип"]), сире=v))
        rec["довідки"] = refs
        cat.append(rec)
    # злиття з наявним каталогом
    old = json.load(open(КАТАЛОГ, encoding="utf-8")) if os.path.exists(КАТАЛОГ) else []
    by_id = {r["id"]: r for r in old}
    by_key = {(r.get("ключ") or "")[:60]: r for r in old}
    kept = relinked = 0
    for r in cat:
        o = by_id.get(r["id"]) or by_key.get(r["ключ"])
        if o is None:
            cands = difflib.get_close_matches(r["ключ"], [x for x in by_key if x], n=1, cutoff=0.93)
            o = by_key.get(cands[0]) if cands else None
            if o: relinked += 1
        if o:
            for f in ЗБЕРІГАТИ:
                if f in o: r[f] = o[f]
            kept += 1
    lost = len(old) - kept
    if verbose:
        print("завдань у каталозі:", len(cat), "| з даними попереднього каталогу:", kept, "(перелінковано: %d)" % relinked,
              "| зникло з бази:", max(0, lost))
    return cat, tasks


def записати(cat):
    зберегти_json(КАТАЛОГ, cat)


def пакети(cat, tasks, out_dir, size):
    """завдання для розв'язування: пакети по size, згруповані за темою; довідкові ключі в пакет НЕ пишуться"""
    os.makedirs(out_dir, exist_ok=True)
    blocks = {t["id"]: t["блок"] for t in tasks}
    groups = collections.defaultdict(list)
    for r in cat: groups[r["теми"][0]].append(r)
    files = []
    for u, rs in groups.items():
        for j in range(0, len(rs), size):
            part = rs[j:j + size]
            name = "пакет_%s_%02d.json" % (re.sub(r"\W", "", u), j // size + 1)
            json.dump([dict(id=r["id"], тема=u, тип=r["тип"], рік=r["рік"], latex=без_відповідей(blocks[r["id"]])) for r in part],
                      open(os.path.join(out_dir, name), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            files.append(name)
    return files


if __name__ == "__main__":
    cat, tasks = зібрати()
    записати(cat)
    c = collections.Counter(r["тип"] for r in cat); print("типи:", dict(c))
    print("з довідковою відповіддю:", sum(1 for r in cat if any(x.get("відповідь") for x in r["довідки"])))
    if "--пакети" in sys.argv:
        i = sys.argv.index("--пакети")
        fs = пакети(cat, tasks, sys.argv[i + 1], int(sys.argv[i + 2]) if len(sys.argv) > i + 2 else 12)
        print("пакетів:", len(fs))
