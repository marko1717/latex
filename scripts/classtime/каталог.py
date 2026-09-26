# -*- coding: utf-8 -*-
"""Каталог завдань-картинок ClassTime (локально): дублікати, тип, тема, слот, збіги з базою й osvita.

Спершу: scripts/classtime/картинки.py (картинки) і розпізнавання тексту:
    ls локальне/classtime/картинки | sed "s|^|$PWD/локальне/classtime/картинки/|" > /tmp/ct.txt
    локальне/classtime/ocr /tmp/ct.txt > локальне/classtime/ocr.jsonl        (swiftc -O scripts/classtime/ocr.swift -o локальне/classtime/ocr)
Потім:
    python3 scripts/classtime/каталог.py
Результат -- локальне/classtime/каталог.json (одна картинка = один запис) і підсумок.
"""
import os, re, sys, json, glob, collections, difflib, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts", "варіант_нмт"))
sys.path.insert(0, os.path.join(ROOT, "scripts", "зно_osvita"))
import спільне as S                                    # noqa: E402
from каталог import rule_category                     # noqa: E402
from класифікувати import одиниця, норм               # noqa: E402

ДАНІ = os.path.join(ROOT, "локальне", "classtime")
# теки «1.1…2.2» (позначка «ЗНО») -- спільна бібліотека ClassTime, не матеріали користувача (підтверджено
# 2026-09-26): лише зразки, у роздаток не йдуть -- навіть якщо картинку скопійовано й у власний набір
СПІЛЬНІ_ТЕКИ = ("1.1.", "1.2.", "1.3.", "1.4.", "2.1.", "2.2.")


def відповідь(a):
    """(тип, нормалізована відповідь) за записом відповіді в ClassTime"""
    a = (a or "").strip().replace("–", "-").replace("—", "-").replace(".", ",")
    if not a or a in ("·", "•", "-"): return None, None            # «·» -- відповідь в експорт не потрапила
    letters = re.findall(r"[АБВГДABCDE]", a.upper())
    lat = dict(zip("ABCDE", "АБВГД"))
    letters = [lat.get(x, x) for x in letters]
    if re.fullmatch(r"[АБВГДABCDEабвгд]", a): return "single", letters[0]
    if len(letters) in (3, 4) and re.fullmatch(r"[\sАБВГДABCDE\d,;:\-]+", a.upper()) and not re.search(r"\d{2,}", a):
        return "matching", "".join(letters)
    parts = [p.strip() for p in re.split(r"\s*[;|]\s*|\s+|,\s+", a) if p.strip()]   # «26;24», «-2,6 3,4», «114, 84»
    if all(re.fullmatch(r"-?\d+(,\d+)?", p) for p in parts):
        return ("input" if len(parts) == 1 else "input2"), ";".join(parts)
    return "відкрита", a                                             # текстова відповідь (параметр, так/ні, проміжок)


def dhash(path):
    from PIL import Image
    im = Image.open(path).convert("L").resize((9, 8))
    px = list(im.getdata())
    return sum(1 << i for i in range(64) if px[(i // 8) * 9 + i % 8] > px[(i // 8) * 9 + i % 8 + 1])


def кластери(hashes, поріг=4):
    """групи майже однакових картинок (відстань Геммінга dHash <= поріг)"""
    ids = list(hashes)
    parent = {i: i for i in ids}
    def find(x):
        while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
        return x
    buckets = collections.defaultdict(list)          # 4 частини по 16 біт: близькі хеші збігаються хоч в одній
    for i in ids:
        h = hashes[i]
        for k in range(4): buckets[(k, (h >> (16 * k)) & 0xFFFF)].append(i)
    for group in buckets.values():
        if len(group) > 400: continue                # порожні/однотонні картинки
        for a in range(len(group)):
            for b in range(a + 1, len(group)):
                x, y = group[a], group[b]
                if bin(hashes[x] ^ hashes[y]).count("1") <= поріг:
                    parent[find(x)] = find(y)
    return {i: find(i) for i in ids}


def main():
    q = json.load(open(os.path.join(ДАНІ, "питання.json"), encoding="utf-8"))
    files = {os.path.splitext(os.path.basename(p))[0]: p for p in glob.glob(os.path.join(ДАНІ, "картинки", "*"))}
    ocr = {}
    if os.path.exists(os.path.join(ДАНІ, "ocr.jsonl")):
        for ln in open(os.path.join(ДАНІ, "ocr.jsonl"), encoding="utf-8"):
            try: d = json.loads(ln)
            except ValueError: continue
            ocr[os.path.splitext(os.path.basename(d["path"]))[0]] = d["text"]
    by = collections.defaultdict(list)
    for x in q:
        if x.get("imageId"): by[x["imageId"]].append(x)
    hashes = {}
    for i in by:
        if i in files:
            try: hashes[i] = dhash(files[i])
            except Exception: pass
    клас = кластери(hashes)

    # збіги з базою НМТ і osvita за розпізнаним текстом
    база = {t["id"]: норм(re.sub(r"(?<!\\)%[^\n]*", "", t["блок"]))[:400] for t in S.завдання_бази()}
    osv_path = os.path.join(ROOT, "локальне", "osvita", "завдання.json")
    osv = {r["id"]: норм(r.get("умова", ""))[:400] for r in json.load(open(osv_path, encoding="utf-8"))} if os.path.exists(osv_path) else {}
    def індекс(d):
        ix = collections.defaultdict(set)
        for i, n in d.items():
            for k in range(0, max(1, len(n) - 8), 4): ix[n[k:k + 8]].add(i)
        return ix
    ix_b, ix_o = індекс(база), індекс(osv)
    def збіг(n, d, ix):
        if len(n) < 30: return None
        votes = collections.Counter(i for k in range(0, max(1, len(n) - 8), 2) for i in ix.get(n[k:k + 8], ()))
        best = None
        for i, _ in sorted(votes.items(), key=lambda x: (-x[1], x[0]))[:5]:   # рівні -- за id, щоб щоразу однаково
            r = difflib.SequenceMatcher(None, n[:300], d[i][:len(n[:300]) + 40], autojunk=False).ratio()
            if r > 0.7 and (not best or r > best[1]): best = (i, round(r, 2))
        return best

    cat = []
    for i, xs in by.items():
        відп = collections.Counter(відповідь(x.get("answer"))[1] for x in xs if відповідь(x.get("answer"))[1])
        тип, a = (відповідь(відп.most_common(1)[0][0]) if відп else (None, None))
        набори = sorted({x.get("setName", "") for x in xs}); теки = sorted({x.get("folder", "") for x in xs})
        текст = ocr.get(i, "")
        # тема: спершу з назв наборів (там часто прямо тема), потім з розпізнаного тексту
        u = None
        for name in набори:
            uu = одиниця(dict(умова=name))
            if uu not in ("1", "6", "20"): u = uu; break
        if not u: u = одиниця(dict(умова=текст)) if текст else "1"
        т = {"single": "single", "matching": "matching", "input": "input", "input2": "input"}.get(тип or "", None)
        n = норм(текст)[:400]
        б, о = збіг(n, база, ix_b), збіг(n, osv, ix_o)
        cat.append(dict(id="ct-" + i, картинка=os.path.relpath(files[i], ROOT) if i in files else None, url=xs[0].get("imageUrl"),
                        набори=набори, теки=теки, вживань=len(xs), тип=тип, відповідь=a, розбіжні_відповіді=len(відп) > 1,
                        теми=[u], родини=sorted({S.РОДИНИ[u]} if u in S.РОДИНИ else set()),
                        орієнтовна_категорія=rule_category(dict(теми=[u], тип=т, блок=текст)) if т else "без відповіді",
                        кластер=клас.get(i), є_в_базі=б[0] if б else None, є_в_osvita=о[0] if о else None,
                        поширення="ні" if any(t.startswith(СПІЛЬНІ_ТЕКИ) for t in теки) else "так",
                        текст=текст))
    json.dump(cat, open(os.path.join(ДАНІ, "каталог.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)

    # підсумок
    groups = collections.defaultdict(list)
    for r in cat: groups[r["кластер"] or r["id"]].append(r)
    уніки = [g[0] for g in groups.values()]
    print("картинок: %d (із файлом %d, з текстом %d); груп після злиття дублікатів: %d" % (
        len(cat), sum(1 for r in cat if r["картинка"]), sum(1 for r in cat if r["текст"]), len(уніки)))
    print("типи:", dict(collections.Counter(r["тип"] for r in уніки)))
    print("уже в базі НМТ: %d; є в osvita: %d; нових: %d" % (
        sum(1 for r in уніки if r["є_в_базі"]), sum(1 for r in уніки if r["є_в_osvita"] and not r["є_в_базі"]),
        sum(1 for r in уніки if not r["є_в_базі"] and not r["є_в_osvita"])))
    print("поширення:", dict(collections.Counter(r["поширення"] for r in уніки)))
    cats = collections.Counter(r["орієнтовна_категорія"] for r in уніки if not r["є_в_базі"])
    print("нові за орієнтовними категоріями:")
    for c in S.СТРУКТУРА_2026:
        if c in cats: print("   %-28s %5d" % (c, cats.pop(c)))
    for c, k in cats.most_common(): print("   %-28s %5d" % (c, k))


if __name__ == "__main__":
    main()
