# -*- coding: utf-8 -*-
"""Генератор тренувальних варіантів НМТ з математики за структурою 2023--2026.

22 завдання: 15 тестових (1 бал), 3 на відповідність (до 3 балів), 4 з короткою відповіддю
(по 2 бали), разом 32 бали. Кожне місце у варіанті -- «слот» зі своєю категорією
(див. спільне.СТРУКТУРА_2026 і README). Для слота береться або справжнє завдання НМТ
2023--2026 із каталогу (лише з перевіреною відповіддю й без дефектів), або згенероване
завдання-аналог із бібліотеки scripts/data/варіант_згенеровані.json.

    python3 scripts/варіант_нмт/варіант.py                     # один варіант, лише оригінали
    python3 scripts/варіант_нмт/варіант.py --нових 6 --seed 7  # 6 слотів -- аналоги
    python3 scripts/варіант_нмт/варіант.py --кількість 4       # 4 варіанти без спільних завдань
    python3 scripts/варіант_нмт/варіант.py --роки 2025-2026 --складність складний

Результат: варіанти/Варіант_<номер>.tex (+ «…_без_водяного_знака.tex»), ключ і джерела
завдань -- на останній сторінці. Використані завдання записуються у варіанти/журнал.json,
щоб наступні варіанти їх не повторювали (--дозволити-повтори вимикає це).
"""
import os, re, sys, json, random, argparse, collections, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from спільне import *

ВАРІАНТИ = os.path.join(ROOT, "варіанти")
ЖУРНАЛ = os.path.join(ВАРІАНТИ, "журнал.json")
БАЛИ = {"single": 1, "matching": 3, "input": 2}
ВАГА_РОКУ = {"2026": 3.0, "2025": 2.5, "2024": 2.0, "2023": 1.5, "2022": 0.5}   # імовірність року для слота (незалежно від кількості завдань року)
ВАГА_СКЛАДНОСТІ = {"легкий": {1: 1.6, 2: 1.0, 3: 0.4}, "звичайний": {1: 1.0, 2: 1.0, 3: 1.0}, "складний": {1: 0.4, 2: 1.0, 3: 1.6}}

ІНСТРУКЦІЇ = {
    1: "Завдання 1--15 мають по п'ять варіантів відповіді, з яких лише \\textbf{один правильний}. "
       "Виберіть правильний, на Вашу думку, варіант відповіді й позначте його в бланку відповідей.",
    16: "У завданнях 16--18 до кожного з трьох рядків інформації, позначених цифрами, доберіть "
        "один правильний, на Вашу думку, варіант, позначений буквою.",
    19: "Розв'яжіть завдання 19--22. Одержані числові відповіді запишіть у бланку відповідей. "
        "Відповідь записуйте лише десятковим дробом, урахувавши положення коми. Знак «мінус» записуйте перед першою цифрою числа.",
}


# ---------------------------------------------------------------- дані
def каталог():
    if not os.path.exists(КАТАЛОГ): raise SystemExit("немає каталогу -- спершу python3 scripts/варіант_нмт/каталог.py")
    return json.load(open(КАТАЛОГ, encoding="utf-8"))


def згенеровані():
    return json.load(open(ЗГЕНЕРОВАНІ, encoding="utf-8")) if os.path.exists(ЗГЕНЕРОВАНІ) else []


def журнал():
    return json.load(open(ЖУРНАЛ, encoding="utf-8")) if os.path.exists(ЖУРНАЛ) else []


def придатне(r, роки):
    """оригінал можна брати у варіант: відповідь перевірено, дефектів немає, категорія відома"""
    return (r.get("відповідь") and r.get("дефект") in (None, "немає") and r.get("категорія") not in (None, "інше")
            and (r.get("рік") in роки) and r.get("перевірено", True) is not False
            and (r.get("рисунок_огляд") or {}).get("стан") != "вада")      # рисунок, що заважає розвʼязанню


# найменша кількість кроків міркування (поле «кроки», оцінка двох незалежних рецензентів) для слота:
# №14 НМТ -- обчислювальна планіметрія, одне з найважчих тестових завдань (кілька трикутників,
# тригонометрія + теорема Піфагора, додаткова побудова); завдання в 1--3 кроки туди не беруться
МІН_КРОКИ = {"планіметрія_обчислення": 4}


def пул(cat, gen, роки, used):
    orig, new = collections.defaultdict(list), collections.defaultdict(list)
    за_id = {r["id"]: r for r in cat}
    for r in cat:
        if придатне(r, роки) and r["id"] not in used and (r.get("кроки") or 0) >= МІН_КРОКИ.get(r["категорія"], 0):
            orig[r["категорія"]].append(r)
    for g in gen:
        # складність аналога -- його власна або завдання-зразка
        g.setdefault("складність", (за_id.get(g.get("зразок")) or {}).get("складність") or 2)
        if g.get("перевірено") and g["id"] not in used and (g.get("кроки") or 0) >= МІН_КРОКИ.get(g["категорія"], 0):
            new[g["категорія"]].append(g)
    return orig, new


def вибрати(cands, rnd, складність, used_units, weight_year=True):
    """зважений випадковий вибір: спершу рік (свіжіші ймовірніші, хоч би скільки завдань мав рік),
    потім завдання цього року -- з урахуванням складності й без повтору тем у варіанті"""
    if weight_year:
        years = sorted({r.get("рік") for r in cands})
        y = rnd.choices(years, weights=[ВАГА_РОКУ.get(x or "", 1.0) for x in years], k=1)[0]
        cands = [r for r in cands if r.get("рік") == y]
    ws = []
    for r in cands:
        w = ВАГА_СКЛАДНОСТІ[складність].get(r.get("складність") or 2, 1.0)
        if set(r.get("теми", [])) & used_units: w *= 0.3
        ws.append(w)
    return rnd.choices(cands, weights=ws, k=1)[0]


def скласти(cat, gen, args, rnd, used, спроб=300):
    """слот -> (завдання, 'оригінал'|'аналог'); повертає список із 22 пар.

    Правило: тип завдання (тема: прогресія, тригонометрія, логарифми, призма, трикутник ...)
    у варіанті не повторюється, окрім функцій. Слоти з найвужчим вибором типів заповнюються
    першими; якщо якийсь слот лишився без завдань -- варіант складається наново."""
    роки = розгорнути_роки(args.роки)
    orig, new = пул(cat, gen, роки, used)
    структура = СТРУКТУРА_2026
    можна = [i for i, c in enumerate(структура) if new.get(c)]
    k = min(args.нових, len(можна))
    if args.нових > k:
        print("  ! аналогів вистачає лише на %d слотів із %d запитаних" % (k, args.нових))
    for спроба in range(спроб):
        нові_слоти = set(rnd.sample(можна, k)) if k else set()
        пули = {}
        for i, c in enumerate(структура):
            p = new[c] if i in нові_слоти else orig[c]
            if not p and new.get(c): p = new[c]
            пули[i] = p
        # найобмеженіші слоти першими: менше різних типів -> раніше; далі менший пул
        порядок = sorted(range(len(структура)), key=lambda i: (len({f for r in пули[i] for f in родини(r)} or {""}), len(пули[i]), rnd.random()))
        вибір, used_units, taken, used_fam = {}, set(), set(), set()
        ok = True
        for i in порядок:
            cands = [r for r in пули[i] if r["id"] not in taken and not (родини(r) & used_fam)]
            if not cands: ok = False; break
            kind = "аналог" if (i in нові_слоти or not orig[структура[i]]) else "оригінал"
            t = вибрати(cands, rnd, args.складність, used_units, weight_year=(kind == "оригінал"))
            taken.add(t["id"]); used_units |= set(t.get("теми", [])); used_fam |= родини(t)
            вибір[i] = (t, kind)
        if ok:
            # у завданнях на відповідність 16--18 ключі різні (однакові поспіль виглядають як підказка)
            ключі = [вибір[i][0].get("відповідь") for i in range(len(структура)) if вибір[i][0].get("тип") == "matching"]
            if len(set(ключі)) < len(ключі): continue
            if спроба: print("  (типи без повторів -- зі спроби %d)" % (спроба + 1))
            return [вибір[i] for i in range(len(структура))]
    raise SystemExit("не вдалося скласти варіант без повторів типів за %d спроб -- зменште --кількість чи --нових" % спроб)


def розгорнути_роки(s):
    out = set()
    for part in s.split(","):
        if "-" in part:
            a, b = part.split("-"); out |= {str(y) for y in range(int(a), int(b) + 1)}
        elif part: out.add(part.strip())
    return out


# ---------------------------------------------------------------- LaTeX
def тіло_теми(path):
    """макроси, які тема оголошує на початку документа (для завдань цієї теми)"""
    s = open(os.path.join(ROOT, path), encoding="utf-8").read()
    a = s.index("\\begin{document}") + len("\\begin{document}")
    b = s.index("\\chapterTitle{", a)
    seg = s[a:b]
    seg = re.sub(r"^\s*\\begingroup\\setcounter\{zad\}\{0\}", "", seg)
    seg = re.sub(r"(?m)^\\graphicspath\{.*\}\s*$", "", seg)   # шляхи тем -- від кореня; у варіанті є власний список тек
    # у варіанті макрос уже може бути визначений (іншою темою чи загальним блоком): оголосити або перевизначити
    seg = re.sub(r"\\newcommand\s*\{(\\[A-Za-z@]+)\}", lambda m: "\\providecommand{%s}{}\\renewcommand{%s}" % (m.group(1), m.group(1)), seg)
    return seg.strip("\n")


def чистий_блок(b, роки_видно):
    b = re.sub(r"\\ifshowsolutions.*?\\fi\b", "", b, flags=re.S)
    b = re.sub(r"(?<!\\)%[^\n]*", "%", b)             # коментарі (там бувають ключі); сам «%» лишаємо -- він гасить пробіл у кінці рядка
    b = re.sub(r"(?m)^%\n", "", b)
    if not роки_видно: b = re.sub(r"\s*\\nmtyear\{\d{4}\}", "", b)
    return b.strip()


def преамбула(title, header):
    s = open(os.path.join(ROOT, файли_тем()[0][1]), encoding="utf-8").read()
    pre = s[:s.index("\\begin{document}")]
    pre = re.sub(r"\\fancyhead\[C\]\{[^\n]*\}", lambda m: "\\fancyhead[C]{\\small\\color{gray!80} %s}" % header, pre, count=1)
    pre = re.sub(r"\\fancyfoot\[R\]\{[^\n]*\}", lambda m: "\\fancyfoot[R]{\\small\\color{gray!80}НМТ з математики}", pre, count=1)
    # рисунки-файли лежать у теках тем; варіант -- у теці «варіанти»
    folders = sorted({нфк(os.path.dirname(f)) for _, f in файли_тем()})
    pre += "\\graphicspath{%s}\n" % "".join("{../%s/}" % d for d in folders)
    return pre + ВАРІАНТ_МАКРОСИ


# інструкція не відривається від першого завдання свого блоку (розриву сторінки між ними немає);
# у полі короткої відповіді 5 клітинок до коми (є відповіді на кшталт 21000)
ВАРІАНТ_МАКРОСИ = r"""\renewcommand{\instructionBox}[1]{%
\par\vspace{0.3cm}\noindent
\begin{tcolorbox}[nobeforeafter, width=\linewidth, colback=instrBg, colframe=instrBorder, boxrule=0.6pt, arc=2pt,
    left=8pt, right=8pt, top=4pt, bottom=4pt]
\centering\small\bfseries #1
\end{tcolorbox}
\par\nopagebreak\vspace{0.15cm}\nopagebreak
}
\renewcommand{\nmtAnswerBox}{%
\par\nopagebreak\vspace{0.2cm}\noindent
Відповідь:\ \
\begin{tabular}{@{}*{5}{|>{\centering\arraybackslash}p{0.8cm}}|@{\hspace{0.1cm}\textbf{,}\hspace{0.1cm}}*{3}{|>{\centering\arraybackslash}p{0.8cm}}|@{}}
\hline
\rule[-0.2cm]{0pt}{0.7cm} & & & & & & & \\
\hline
\end{tabular}
\par\vspace{0.3cm}
}
"""


def відповідь_латех(a, тип_завдання):
    if тип_завдання == "matching" and len(a) == 3: return "1~--~%s, 2~--~%s, 3~--~%s" % tuple(a)
    if тип_завдання == "input": return "$%s$" % a.replace(",", "{,}")
    return a


def зібрати_латех(номер, вибір, blocks, args):
    title = "Тренувальний варіант НМТ з математики № %s" % номер
    out = [преамбула(title, "Варіант № %s" % номер), "\\begin{document}"]
    # загальні макроси (\matchingLayout тощо) -- для аналогів, у яких немає своєї теми
    out.append("% макроси бази, потрібні аналогам\n" + тіло_теми(файли_тем()[0][1]) + "\n\\setcounter{zad}{0}\n")
    out.append("\\chapterTitle{%s}\n" % title)
    роки = collections.Counter(t.get("рік") for t, k in вибір if k == "оригінал")
    n_new = sum(1 for _, k in вибір if k == "аналог")
    out.append("\\noindent{\\small Варіант складено за структурою НМТ 2023--2026: 15 завдань з вибором однієї відповіді, "
               "3 на встановлення відповідності й 4 з короткою відповіддю (максимум 32 бали). "
               + ("Усі завдання -- справжні завдання НМТ %s." % років_рядок(роки) if not n_new else
                  "Усі 22 завдання -- авторські, складені за зразком справжніх завдань НМТ 2023--2026 "
                  "(такі самі за змістом і дистракторами)." if n_new == 22 else
                  "%d %s -- справжні завдання НМТ %s, %d -- авторські аналоги таких самих завдань." %
                  (22 - n_new, завдань(22 - n_new), років_рядок(роки), n_new))
               + " Відповіді -- на останній сторінці.}\\par\\vspace{0.4cm}\n")
    seg_cache = {}
    for i, (t, kind) in enumerate(вибір, 1):
        if i in ІНСТРУКЦІЇ:
            out.append("\\instructionBox{%s}\n" % ІНСТРУКЦІЇ[i])
        if kind == "оригінал":
            f = файл_теми(t["теми"][0])
            if f not in seg_cache: seg_cache[f] = тіло_теми(f)
            body = чистий_блок(blocks[t["id"]], args.показати_роки)
            out.append("\\begingroup\n%s\n\\begin{samepage}\n%s\n\\end{samepage}\n\\endgroup\n" % (seg_cache[f], body))
        else:
            out.append("\\begin{samepage}\n%s\n\\end{samepage}\n" % як_у_базі(чистий_блок(t["latex"], False)))
    # ключ
    out.append("\\clearpage\n\\sectionTitle{Відповіді}\n")
    rows = []
    for i, (t, kind) in enumerate(вибір, 1):
        тип_з = t["тип"]
        src = джерело(t, kind)
        rows.append("%d & %s & %s \\\\ \\hline" % (i, відповідь_латех(t["відповідь"], тип_з), src))
    out.append("\\begin{center}\\small\\renewcommand{\\arraystretch}{1.25}\n"
               "\\begin{tabular}{|c|c|p{0.62\\textwidth}|}\\hline\n\\textbf{№} & \\textbf{Відповідь} & \\textbf{Джерело завдання} \\\\ \\hline\n"
               + "\n".join(rows) + "\n\\end{tabular}\\end{center}\n")
    out.append("\\noindent{\\small\\color{gray!80!black}Оцінювання: завдання 1--15 -- по 1 балу; 16--18 -- по 1 балу за кожну правильно "
               "встановлену відповідність (до 3 балів); 19--22 -- по 2 бали. Разом 32 бали.}\n")
    out.append("\\end{document}\n")
    return нфк("\n".join(out))


def завдань(n):
    return "завдання" if n % 10 in (1, 2, 3, 4) and n % 100 not in (11, 12, 13, 14) else "завдань"


def років_рядок(c):
    ys = sorted(y for y in c if y)
    return (ys[0] + "--" + ys[-1] + " років") if len(ys) > 1 else ((ys[0] + " року") if ys else "")


def джерело(t, kind):
    if kind == "аналог":
        return "аналог (авторське завдання за зразком НМТ)"
    s = t.get("сесія_2026")
    if s:
        _, d, n = s.split("-"); dd, mm = d.split(".")
        return "НМТ 2026, сесія %02d.%s.2026, № %d" % (int(dd), mm, int(n))
    pdf = [x for x in t.get("довідки", []) if x.get("сесія") and x.get("рік_pdf") == t.get("рік")]
    if pdf:
        x = pdf[0]
        m = re.match(r"(\d{2})\.(\d{2})\.(\d{2})(?:-(\d))?$", x["сесія"])
        if m:
            date = "%s.%s.20%s" % m.group(1, 2, 3) + (", %s зміна" % m.group(4) if m.group(4) else "")
            return "НМТ %s, сесія %s, № %d" % (t["рік"], date, x["номер"])
        return "НМТ %s, сесія %s, № %d" % (t["рік"], x["сесія"], x["номер"])
    return "НМТ %s" % (t.get("рік") or "")


# ---------------------------------------------------------------- головне
def записати(номер, вибір, blocks, args):
    tex = зібрати_латех(номер, вибір, blocks, args)
    name = "Варіант_%s" % номер
    open(os.path.join(ВАРІАНТИ, name + ".tex"), "w", encoding="utf-8").write(tex)
    open(os.path.join(ВАРІАНТИ, name + "_без_водяного_знака.tex"), "w", encoding="utf-8").write(нфк(
        "%% Варіант № %s без водяного знака @pvtr2525 -- версія для вчителів.\n\\def\\nmtnowatermark{}\n\\input{%s}\n" % (номер, name)))
    return name


def перезібрати(args, cat, gen, blocks, log):
    """той самий склад із журналу -- новий LaTeX (виправлені рисунки, умови, макроси бази)"""
    за_id = {r["id"]: (r, "оригінал") for r in cat}
    за_id.update({g["id"]: (g, "аналог") for g in gen})
    for n in args.перезібрати:
        v = next((v for v in log if str(v["номер"]) == str(n)), None)
        if v is None: raise SystemExit("у журналі немає варіанта %s" % n)
        brak = [i for i in v["завдання"] if i not in за_id]
        if brak: raise SystemExit("варіант %s: завдань %s уже немає в каталозі (оновіть каталог.py)" % (n, ", ".join(brak)))
        print("перезібрано варіанти/%s.tex" % записати(str(n), [за_id[i] for i in v["завдання"]], blocks, args))


def main():
    ap = argparse.ArgumentParser(description="тренувальні варіанти НМТ з математики")
    ap.add_argument("--кількість", type=int, default=1)
    ap.add_argument("--нових", type=int, default=0, help="скільки слотів заповнити аналогами")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--роки", default="2023-2026")
    ap.add_argument("--складність", choices=list(ВАГА_СКЛАДНОСТІ), default="звичайний")
    ap.add_argument("--номер", default=None, help="номер першого варіанта (за замовчуванням -- наступний після журналу)")
    ap.add_argument("--показати-роки", dest="показати_роки", action="store_true", help="лишити біля завдань позначку року")
    ap.add_argument("--дозволити-повтори", dest="повтори", action="store_true")
    ap.add_argument("--без-журналу", dest="без_журналу", action="store_true", help="не записувати використані завдання")
    ap.add_argument("--перезібрати", nargs="+", metavar="N", help="лише перезаписати .tex варіантів N ... з тими самими "
                    "завданнями, що в журналі (після виправлень у базі); нічого не вибирає наново")
    args = ap.parse_args()

    cat, gen = каталог(), згенеровані()
    blocks = {t["id"]: t["блок"] for t in завдання_бази()}
    missing = [r["id"] for r in cat if r["id"] not in blocks]
    if missing: print("  ! у каталозі %d завдань, яких уже немає в базі (оновіть: каталог.py)" % len(missing))
    cat = [r for r in cat if r["id"] in blocks]
    log = журнал()
    if args.перезібрати:
        return перезібрати(args, cat, gen, blocks, log)
    if args.номер:   # перескласти варіант із тим самим номером: старий запис журналу замінюється
        нові = {str(int(args.номер) + j) for j in range(args.кількість)}
        log = [v for v in log if str(v["номер"]) not in нові]
    used = set() if args.повтори else {i for v in log for i in v["завдання"]}
    seed = args.seed if args.seed is not None else random.SystemRandom().randrange(10 ** 6)
    rnd = random.Random(seed)
    перший = int(args.номер) if args.номер else (max([int(v["номер"]) for v in log if str(v["номер"]).isdigit()] or [0]) + 1)
    os.makedirs(ВАРІАНТИ, exist_ok=True)
    for j in range(args.кількість):
        номер = str(перший + j)
        вибір = скласти(cat, gen, args, rnd, used)
        name = записати(номер, вибір, blocks, args)
        ids = [t["id"] for t, _ in вибір]
        used |= set(ids)
        log.append(dict(номер=номер, seed=seed, нових=sum(1 for _, k in вибір if k == "аналог"), завдання=ids,
                        слоти=[t.get("категорія") for t, _ in вибір]))
        print("записано варіанти/%s.tex (seed %d): %s" % (name, seed, ", ".join(
            "%d:%s%s" % (i, t.get("рік") or "ан", "*" if k == "аналог" else "") for i, (t, k) in enumerate(вибір, 1))))
    if not args.без_журналу:
        json.dump(log, open(ЖУРНАЛ, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
