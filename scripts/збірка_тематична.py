# -*- coding: utf-8 -*-
"""Тематичні збірники з бази НМТ: показникові, логарифмічні тощо.

Завдання на відповідність перетворюються на тестові: з трьох пунктів лишається
той, що стосується теми збірника, а п'ять варіантів А--Д друкуються окремими
рядками. Якщо тема стоїть лише серед варіантів -- пункт обирається за ключем
(таблиця OVERRIDE); якщо завдання насправді не за темою -- воно відкидається.
На початку -- анотація, наприкінці -- ключ відповідей. Поруч записується
файл «…_без_водяного_знака.tex» (версія для вчителів).

    python3 scripts/збірка_тематична.py показникові
    python3 scripts/збірка_тематична.py логарифмічні
    python3 scripts/збірка_тематична.py призма
    python3 scripts/збірка_тематична.py піраміда
"""
import os, re, sys, json, hashlib, unicodedata, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIGS = {
    "показникові": dict(
        title="Показникові вирази, функція, рівняння і нерівності",
        out="Показникові_рівняння_нерівності_функція.tex",
        src=[("Показникові вирази і функція", "28. Показникова функція. Показникові рівняння/Показникові функція і вирази/завдання.tex"),
             ("Показникові рівняння",          "28. Показникова функція. Показникові рівняння/Показникові рівняння/завдання.tex"),
             ("Показникові нерівності",        "29. Показникові нерівності/завдання.tex")],
        detect=r"\^\s*\{[^{}]*[A-Za-zА-Яа-я\\][^{}]*\}|\^\s*\\?[A-Za-z]",
        about="показникові вирази, показникову функцію, показникові рівняння та нерівності",
        topics="тем 28 і 29", relevant="показникових",
        answers="відповіді_показникові.json",
        override=[
            ("2023", "Установіть відповідність між твердженням", "2"),    # (0;1) -> y=4^x
            ("2024", "Установіть відповідність між твердженням", "3"),    # найменше значення 0,5 -> y=2^x
            ("2024", "На кожному з рисунків", "drop"),                    # про рисунки, показникова лише в тексті варіанта
            ("2025", "На рисунку зображено графік функції", "drop"),      # 2^x -- дистрактор
            ("2026", "На рисунку зображено графік функції", "drop"),      # відповідь 1--В, 2--Д, 3--Г: 2^x не використано
            ("2025", "Установіть відповідність між твердженням", "drop"),  # пункти логарифмічні
        ]),
    "логарифмічні": dict(
        title="Логарифмічні вирази, функція, рівняння і нерівності",
        out="Логарифмічні_рівняння_нерівності_функція.tex",
        src=[("Логарифмічні вирази",     "30. Логарифм. Логарифмічна функція/завдання вирази.tex"),
             ("Логарифмічна функція",    "30. Логарифм. Логарифмічна функція/завдання функція.tex"),
             ("Логарифмічні рівняння",   "31. Логарифмічні рівняння/завдання.tex"),
             ("Логарифмічні нерівності", "32. Логарифмічні нерівності/завдання.tex")],
        detect=r"\\log|\\lg(?![a-zA-Z])|\\ln(?![a-zA-Z])",
        about="логарифмічні вирази, логарифмічну функцію, логарифмічні рівняння та нерівності",
        topics="тем 30, 31 і 32", relevant="логарифмів",
        answers="відповіді_логарифмічні.json",
        override=[
            ("2023", "Установіть відповідність між твердженням", "3"),    # найменше значення на [1; 4] у точці 4 -> y=log_0,5 x
            ("2024", "Установіть відповідність між функцією (1--3) та властивістю її графіка", "drop"),  # log_0,5 x лише в дистракторі В
            ("2023", "Установіть відповідність між функцією (1--3) та властивістю (А--Д) її графіка", "drop!"),  # для log_2 x правильні і Б, і В
        ]),
    # третій елемент джерела -- параметри відбору: kinds (типи завдань), need (обов'язковий текст),
    # drop (фрагменти умов завдань не за темою), file_order (порядок як у файлі теми)
    "призма": dict(
        title="Призма. Прямокутний паралелепіпед. Куб",
        out="Призма_паралелепіпед_куб.tex",
        src=[("Завдання з вибором однієї відповіді", "38. Призма. Паралелепіпед. Куб/завдання.tex",
              dict(kinds=("single", "?"), file_order=True, drop=["ромба $ABCD$ проведено перпендикуляр"])),
             ("Завдання з короткою відповіддю", "38. Призма. Паралелепіпед. Куб/завдання.tex",
              dict(kinds=("input",), file_order=True))],
        # задачі з призмою з тем 18 і 39--42 уже є в темі 38; єдина нова (тема 18, M(-3; 2; 0)) не звірена
        # з оригіналом і має відповідь 164√82, неможливу на НМТ, тому не береться
        strict_dups=True,   # одна задача з різних сесій (інші лапки, порядок варіантів) -- друкуємо один раз
        detect=r"призм|паралелепіпед|куб(?![іи]чн)",
        about="призму, прямокутний паралелепіпед і куб",
        topics="теми 38", relevant="призми",
        src_phrase="з теми 38 бази НМТ (серед них є задачі на призму й куб у системі координат і задачі, де призма поєднана з циліндром, конусом, пірамідою чи кулею)",
        answers="відповіді_призма.json",
        override=[]),
    "піраміда": dict(
        title="Піраміда",
        out="Піраміда.tex",
        src=[("Завдання з вибором однієї відповіді", "39. Піраміда/завдання.tex", dict(kinds=("single", "?"), file_order=True)),
             ("Завдання з короткою відповіддю", "39. Піраміда/завдання.tex", dict(kinds=("input",), file_order=True))],
        strict_dups=True,
        detect=r"пірамід|тетраедр",
        about="піраміду",
        topics="теми 39", relevant="піраміди",
        src_phrase="з теми 39 бази НМТ (серед них є задачі на піраміду в системі координат і задачі, де піраміда поєднана з призмою)",
        # відповіді -- з каталогу генератора варіантів (перевірені двома розв'язками); три завдання 2024, яких немає в каталозі
        # (дубль задачі з ромбом і дві задачі з координатами), розв'язано окремо: 600 см³ (Г), 300, 1152
        answers="відповіді_піраміда.json",
        override=[]),
}

def src_paths(entry):
    p = entry[1]
    return p if isinstance(p, list) else [p]

CFG = None   # активна конфігурація (задається в main)

def balanced(s, i):
    d = 0; j = i
    while j < len(s):
        c = s[j]
        if c == "\\": j += 2; continue
        if c == "{": d += 1
        elif c == "}":
            d -= 1
            if d == 0: return j
        j += 1
    raise ValueError("незбалансовані дужки")

def arg_at(s, i):
    """s[i] == '{' -> (вміст, індекс після)"""
    j = balanced(s, i)
    return s[i+1:j], j + 1

def blocks(path):
    s = open(os.path.join(ROOT, path), encoding="utf-8").read()
    return re.findall(r"\\begin\{samepage\}(.*?)\\end\{samepage\}", s[s.index("\\begin{document}"):], re.S)

def kind(b):
    nb = re.sub(r"%[^\n]*", "", b)
    if "\\matchingGrid" in nb: return "matching"
    if re.search(r"\\answerTable", nb): return "single"
    if "\\nmtAnswerBox" in nb: return "input"
    return "?"

def _minipages(t):
    """зовнішні minipage: (початок, кінець, тіло)"""
    res, i = [], 0
    while True:
        i = t.find("\\begin{minipage}", i)
        if i < 0: return res
        j = i + len("\\begin{minipage}")
        while j < len(t) and t[j] in " \n\t": j += 1
        if j < len(t) and t[j] == "[": j = t.find("]", j) + 1
        while j < len(t) and t[j] in " \n\t": j += 1
        if j < len(t) and t[j] == "{": j = balanced(t, j) + 1
        depth, p, k = 1, j, -1
        while p < len(t):
            nb, ne = t.find("\\begin{minipage}", p), t.find("\\end{minipage}", p)
            if ne < 0: break
            if 0 <= nb < ne: depth += 1; p = nb + 16
            else:
                depth -= 1; k = ne
                if depth == 0: break
                p = ne + 14
        if k < 0 or depth != 0: i = j; continue
        res.append((i, k + len("\\end{minipage}"), t[j:k]))
        i = k + len("\\end{minipage}")

def items_of(col):
    """[(мітка, текст)] із послідовності \\matchItem"""
    res, i = [], 0
    while True:
        i = col.find("\\matchItem", i)
        if i < 0: return res
        lab, j = arg_at(col, col.index("{", i))
        txt, j = arg_at(col, j)
        res.append((lab.strip(), txt.strip()))
        i = j

def topical(txt):
    """чи стосується текст теми збірника"""
    return re.search(CFG["detect"], txt) is not None


def override_for(year, stmt):
    plain = re.sub(r"\\[a-zA-Z]+|[${}\\]", " ", stmt)
    plain = re.sub(r"\s+", " ", plain).strip()
    for y, head, val in CFG["override"]:
        if y == (year or "") and plain.startswith(head): return val
    return None

def statement_of(b):
    """текст умови (без \\par і далі) + рік"""
    m = re.search(r"\\zadtask\{", b)
    if m:
        body, _ = arg_at(b, m.end() - 1)
    else:
        m = re.search(r"(?:\\noindent)?\\zadnum\s*", b)
        body = b[m.end():]
    for cut in ("\\par", "\\vspace", "\\nbvspace", "\\nmtnobreak", "\\matchingLayout", "\\begin{minipage}", "\\noindent\n"):
        k = body.find(cut)
        if k > 0: body = body[:k]
    body = re.sub(r"\s+", " ", body).strip()
    yr = re.search(r"\\nmtyear\{(\d{4})\}", body)
    body = re.sub(r"\s*\\nmtyear\{\d{4}\}", "", body).strip()
    return body, (yr.group(1) if yr else None)

def to_single(b):
    """завдання на відповідність -> тестове з одним пунктом і п'ятьма варіантами"""
    i = b.find("\\matchingLayout")
    if i < 0:
        its = items_of(b)
        expo = [(l, t) for l, t in its if topical(t)]
        if not expo: return "DROP"
        lab, item = expo[0]
        out = b
        # прибираємо колонку з пунктами і сітку: лишається умова + варіанти-рисунки
        for a, e, body_mp in reversed(_minipages(out)):
            if "\\matchItem" in body_mp or re.fullmatch(r"[\s%]*(?:\\(?:nopagebreak|nmtnobreak|n?bvspace\{[^}]*\}|matchingGrid|matchHead\{[^}]*\})[\s%]*)*", body_mp or ""):
                out = out[:a] + out[e:]
        out = re.sub(r"[ \t]*\\matchingGrid[ \t]*\n?", "", out)
        out = re.sub(r"[ \t]*\\matchHead\{[^{}]*\}[ \t]*\n?", "", out)
        # пункти 1--3, що стоять поза minipage
        while True:
            k = re.search(r"[ \t]*\\matchItem\{[1-3]\}", out)
            if not k: break
            _, e = arg_at(out, out.index("{", k.end()))
            out = out[:k.start()] + out[e:].lstrip(" \t").lstrip("\n")
        quoted = item if item.lstrip().startswith("$") else "<<%s>>" % item
        out = re.sub(r"\\mbox\{\(1--3\)\}|\(1\s*[–-]+\s*3\)", lambda mm: quoted, out, count=1)
        out = re.sub(r"\n{3,}", "\n\n", out)
        return "\\begin{samepage}\n" + out.strip() + "\n\\end{samepage}\n"
    c1, j = arg_at(b, b.index("{", i))
    c2, j = arg_at(b, j)
    items, opts = items_of(c1), items_of(c2)
    if len(items) < 2 or len(opts) != 5: return None
    stmt, year = statement_of(b)
    if override_for(year, stmt) == "drop!": return "DROP"     # тестове вийшло б із кількома правильними відповідями
    items = [(l, re.sub(r"\s*\\\\\s*", " ", t)) for l, t in items]   # розриви рядків усередині пункту
    expo = [(l, t) for l, t in items if topical(t)]
    if expo:
        lab, item = expo[0]
    else:
        ov = override_for(year, stmt)
        if ov in (None, "drop", "drop!"): return "DROP"
        lab, item = next(((l, t) for l, t in items if l == ov), items[0])
    quoted0 = item if item.lstrip().startswith("$") else "<<%s>>" % item
    if re.search(r"\\begin\{|includegraphics|tikzpicture", stmt):
        # умова з рисунком: лишаємо її як є, підставляємо пункт і додаємо варіанти рядками
        pre = b[:i].rstrip()
        pre = re.sub(r"\\mbox\{\(1--3\)\}|\(1\s*[–-]+\s*3\)", lambda m: quoted0, pre, count=1)
        pre = re.sub(r"^\s*", "", pre)
        opts5 = "}{".join(t for _, t in opts)
        out = ["\\begin{samepage}", pre, "\\par\\nopagebreak\\vspace{0.15cm}",
               "\\answerRows{%s}" % opts5, "\\par\\penalty-20", "\\end{samepage}\n"]
        return "\n".join(out)
    if stmt.replace("\\{", "").replace("\\}", "").count("{") != stmt.replace("\\{", "").replace("\\}", "").count("}"): return None
    # підставляємо сам пункт замість «(1--3)»
    quoted = item if item.lstrip().startswith("$") else "<<%s>>" % item
    if re.search(r"почат(ку|ок) речення", stmt) and "акінчення" in stmt:
        # «До кожного початку речення (1--3) доберіть його закінчення (А--Д) так, щоб ...»
        tail = ""
        mt = re.search(r"(так,\s*щоб[^.]*\.?)(.*)$", stmt, re.S)
        cond = re.search(r"(,\s*якщо .*)$", stmt, re.S)
        stmt = "Доберіть закінчення @@ABCD@@ до початку речення %s так, щоб утворилося правильне твердження%s" % (
            quoted, (cond.group(1).rstrip(". ") if cond else ""))
        stmt = stmt.rstrip(". ") + "."
    else:
        stmt = re.sub(r"\\mbox\{\(1--3\)\}|\(1\s*[–-]+\s*3\)", lambda m: quoted, stmt, count=1)
        stmt = re.sub(r"^До кожного ", "До ", stmt)
        stmt = re.sub(r"^Доберіть до кожного ", "Доберіть до ", stmt)
        stmt = re.sub(r"^Установіть відповідність між ", "Доберіть відповідність: ", stmt) if False else stmt
    stmt = re.sub(r"\\mbox\{\(А--Д\)\}", lambda m: "@@ABCD@@", stmt)
    stmt = re.sub(r"\(А\s*[–-]+\s*Д\)", lambda m: "@@ABCD@@", stmt)
    stmt = stmt.replace("@@ABCD@@", "\\mbox{(А--Д)}")
    ans = re.search(r"%\s*Відповідь:\s*([^\n]*)", b)
    letter = None
    if ans:
        mm = re.search(r"\b" + re.escape(lab) + r"\s*~?--~?\s*([А-Д])", ans.group(1))
        if mm: letter = mm.group(1)
    out = ["\\begin{samepage}"]
    if letter: out.append("%% Відповідь: %s" % letter)
    out.append("\\zadtask{%s%s}" % (stmt, (" \\nmtyear{%s}" % year) if year else ""))
    # рисунок між умовою і таблицею (координатна пряма тощо) переносимо разом з умовою
    fig = re.search(r"\\begin\{center\}(?:(?!\\end\{center\}).)*?(?:tikzpicture|includegraphics).*?\\end\{center\}", b[:i], re.S)
    if fig:
        out.append("\\par\\nopagebreak\\vspace{0.1cm}")
        out.append(fig.group(0))
    out.append("\\answerRows{%s}" % "}{".join(t for _, t in opts))
    out.append("\\par\\penalty-20")
    out.append("\\end{samepage}\n")
    return "\n".join(out)

def preamble():
    p = os.path.join(ROOT, src_paths(CFG["src"][-1])[0])
    s = open(p, encoding="utf-8").read()
    pre = s[:s.index("\\begin{document}")]
    pre = re.sub(r"\\fancyhead\[C\]\{[^\n]*\}",
                 lambda m: "\\fancyhead[C]{\\small\\color{gray!80} %s}" % CFG["title"], pre, count=1)
    pre += ("% варіанти відповіді окремими рядками (довгі вирази не влазять у клітинки таблиці)\n"
            "\\newcommand{\\answerRows}[5]{\\par\\nopagebreak\\vspace{0.15cm}%\n"
            "\\matchItem{А}{#1}\\matchItem{Б}{#2}\\matchItem{В}{#3}\\matchItem{Г}{#4}\\matchItem{Д}{#5}}\n")
    return pre


def sig(block):
    """стабільний підпис завдання: нормалізований текст без року й службових команд"""
    t = re.sub(r"%[^\n]*", " ", block)
    t = re.sub(r"(?s)\\begin\{(tikzpicture|axis)\}.*?\\end\{\1\}", " ", t)
    t = re.sub(r"\\nmtyear\{\d+\}|\\(?:begin|end)\{samepage\}", " ", t)
    t = re.sub(r"[^0-9A-Za-zА-Яа-яІіЇїЄєҐґ]+", "", t)
    # початок тексту для читабельності + хеш усього тексту (у схожих задач початок однаковий)
    return t[:80] + "#" + hashlib.sha1(t.encode("utf-8")).hexdigest()[:10]

def same_key(block):
    """ключ для пошуку повторів: без рисунків, коментарів, року та оформлення"""
    t = re.sub(r"%[^\n]*", " ", block)
    t = re.sub(r"(?s)\\begin\{(tikzpicture|axis)\}.*?\\end\{\1\}", " ", t)
    t = re.sub(r"\\nmtyear\{\d+\}|\\(?:mbox|textit|matchHead|noindent|zadnum|zadtask|par|nmtnobreak|nopagebreak)\b", " ", t)
    return re.sub(r"[^0-9A-Za-zА-Яа-яІіЇїЄєҐґ]+", "", t)

def task_key(block):
    """ключ повтору, стійкий до оформлення: умова без команд LaTeX + відсортовані варіанти
    (у базі одна задача трапляється з іншими лапками, «\\text{см}» чи порядком варіантів)"""
    t = re.sub(r"%[^\n]*", " ", block)
    t = re.sub(r"(?s)\\begin\{(tikzpicture|axis)\}.*?\\end\{\1\}", " ", t)
    t = re.sub(r"\\nmtyear\{\d+\}|\\begin\{minipage\}(?:\[[^\]]*\])?\{[^{}]*\}", " ", t)
    norm = lambda x: re.sub(r"[^0-9A-Za-zА-Яа-яІіЇїЄєҐґ]+", "", re.sub(r"\\[a-zA-Z]+\*?", " ",
                            re.sub(r"\\(?:begin|end)\{[^{}]*\}|\\(?:n?b?vspace|hspace)\*?\{[^{}]*\}|\(див\. рисунок\)", " ", x)))
    m = re.search(r"\\answer(?:Table|TableTall|Rows)\s*\{", t)
    if m:
        opts, j = [], m.end() - 1
        while j < len(t) and len(opts) < 5:
            while j < len(t) and t[j] in " \n\t": j += 1
            if j >= len(t) or t[j] != "{": break
            a, j = arg_at(t, j); opts.append(norm(a))
        return norm(t[:m.start()]) + "|" + "|".join(sorted(opts))
    parts = re.split(r"\\textbf\{[А-Д]\}|\\item\b", t)
    if len(parts) >= 6:
        return norm(parts[0]) + "|" + "|".join(sorted(norm(x) for x in parts[1:]))
    return norm(t)

def answers():
    p = os.path.join(ROOT, "scripts", "data", CFG["answers"])
    if not os.path.exists(p): return {}
    return json.load(open(p, encoding="utf-8"))

def carried_macros():
    """макроси, які теми означують після \\begin{document} (matchingLayout тощо)"""
    src = open(os.path.join(ROOT, src_paths(CFG["src"][0])[0]), encoding="utf-8").read()
    a = src.index("\\begin{document}") + len("\\begin{document}")
    b = src.index("\\chapterTitle{", a)
    return src[a:b].strip("\n")

def main():
    global CFG
    name = sys.argv[1] if len(sys.argv) > 1 else "показникові"
    if name not in CONFIGS: raise SystemExit("невідомий збірник: %s (є: %s)" % (name, ", ".join(CONFIGS)))
    CFG = CONFIGS[name]
    out = [preamble(), "\\begin{document}\n" + carried_macros() + "\n\\setcounter{zad}{0}\n"]
    out.append("\\chapterTitle{%s}\n" % CFG["title"])
    stat, order = [], []
    seen, dups = set(), 0     # у базі трапляються однакові завдання з різних сесій -- друкуємо один раз
    ann = len(out)          # місце під анотацію -- підставимо, коли будуть підрахунки
    out.append("")
    for entry in CFG["src"]:
        title, opt = entry[0], (entry[2] if len(entry) > 2 else {})
        bs = [b for path in src_paths(entry) for b in blocks(path)]
        if "kinds" in opt: bs = [b for b in bs if kind(b) in opt["kinds"]]
        if "need" in opt: bs = [b for b in bs if re.search(opt["need"], re.sub(r"%[^\n]*", "", b), re.I)]
        if "drop" in opt: bs = [b for b in bs if not any(d in b for d in opt["drop"])]
        matched = [(b, to_single(b)) for b in bs if kind(b) == "matching"]
        conv = [c for _, c in matched if c and c != "DROP"]
        kept = [b for b, c in matched if c is None]
        dropped = sum(1 for _, c in matched if c == "DROP")
        singles = [b for b in bs if kind(b) == "single"]
        other = [b for b in bs if kind(b) not in ("single", "matching")] + kept
        out.append("\\typeTitle{%s}\n" % title)
        n0, dup0, nconv = len(order), dups, 0
        seq = singles + conv + other
        if opt.get("file_order"):
            conv_of = dict(matched)
            seq = [conv_of.get(b) or b if kind(b) == "matching" else b for b in bs]
            seq = [b for b in seq if b != "DROP"]
        for b in seq:
            k = same_key(b)
            k2 = task_key(b) if CFG.get("strict_dups") else k
            if k in seen or k2 in seen: dups += 1; continue
            seen.update((k, k2))
            is_conv = b in conv
            b = b.replace("координатою якою", "координатою якої")   # описка в умові джерела
            if is_conv: out.append(b); nconv += 1
            else: out.append("\\begin{samepage}\n" + b.strip() + "\n\\end{samepage}\n")
            order.append(b)
        stat.append("%s: %d завдань (з відповідностей %d, відкинуто не за темою %d, повторів %d)" % (
            title.lower(), len(order) - n0, nconv, dropped, dups - dup0))
    years = collections.Counter()
    for b in order:
        y = re.search(r"\\nmtyear\{(\d{4})\}", b)
        if y: years[y.group(1)] += 1
    conv_total = sum(1 for b in order if "\\answerRows" in b)
    parts = ", ".join(re.sub(r":.*", "", x) for x in stat)
    nparts = {1: "одну частину", 2: "дві частини", 3: "три частини", 4: "чотири частини"}.get(len(stat), "%d частин" % len(stat))
    src_phrase = CFG.get("src_phrase") or ("з " + CFG["topics"] + " бази НМТ")
    conv_note = ("Завдання \\textit{на встановлення відповідності} перероблено на тестові: із трьох пунктів залишено той, "
                 "що стосується " + CFG["relevant"] + ", а п'ять варіантів відповіді надруковано окремими рядками, бо вирази "
                 "задовгі для клітинок таблиці; таких завдань %d. " % conv_total) if conv_total else ""
    out[ann] = ("\\noindent{\\small Збірник містить \\textbf{%d завдань} НМТ %s--%s років про " + CFG["about"] + ". "
                "Завдання зібрано " + src_phrase + " і згруповано у " + nparts + ": %s. Біля кожного завдання вказано рік.\\par\\vspace{0.15cm}\n"
                + conv_note + "Відповіді до всіх завдань~--- на останній сторінці.\\par\\vspace{0.15cm}\n"
                "За роками: %s.}\\par\\vspace{0.45cm}\n") % (
                len(order), min(years), max(years), parts,
                ", ".join("\\mbox{%s~--- %d}" % (y, n) for y, n in sorted(years.items())))
    key = answers()
    rows, missing = [], 0
    for n, b in enumerate(order, 1):
        a = key.get(sig(b))
        if a: rows.append("\\mbox{%d~--- %s}" % (n, a))
        else: rows.append("\\mbox{%d~--- ?}" % n); missing += 1
    out.append("\\clearpage\n\\sectionTitle{Відповіді}\n")
    out.append("\\noindent{\\small\\color{gray!80!black}Відповіді до завдань цього збірника. "
               "Відповіді обчислено й звірено з офіційними ключами там, де вони є.}"
               "\\par\\vspace{0.3cm}\n")
    out.append("\\begin{multicols}{5}\\noindent\n" + "\\par\n".join(rows) + "\n\\end{multicols}\n")
    if missing: print("   УВАГА: без відповіді", missing, "завдань")
    out.append("\\end{document}\n")
    txt = unicodedata.normalize("NFC", "\n".join(out))
    open(os.path.join(ROOT, CFG["out"]), "w", encoding="utf-8").write(txt)
    # та сама збірка без водяного знака (для вчителів): тонкий файл-обгортка, сам збірник не дублюється
    stem = CFG["out"][:-4]
    clean = unicodedata.normalize("NFC", stem + "_без_водяного_знака.tex")
    open(os.path.join(ROOT, clean), "w", encoding="utf-8").write(unicodedata.normalize("NFC",
        "%% Збірник «%s» без водяного знака @pvtr2525 -- версія для вчителів.\n"
        "%% Компілюйте цей файл (XeLaTeX); завдання беруться з %s.tex.\n"
        "\\def\\nmtnowatermark{}\n\\input{%s}\n" % (CFG["title"], stem, stem)))
    print("записано", CFG["out"], "і", clean)
    for s in stat: print("   ", s)

if __name__ == "__main__":
    main()
