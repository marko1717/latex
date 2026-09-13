# -*- coding: utf-8 -*-
"""Окремий файл: показникові вирази, функція, рівняння і нерівності.

Завдання на відповідність перетворюються на тестові: з трьох пунктів лишається
той, що стосується показникових виразів (показник містить змінну), а п'ять
варіантів А--Д друкуються окремими рядками, а не в таблиці.

    python3 scripts/збірка_показникові.py
"""
import os, re, sys, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = [("Показникові вирази і функція", "28. Показникова функція. Показникові рівняння/Показникові функція і вирази/завдання.tex"),
       ("Показникові рівняння",          "28. Показникова функція. Показникові рівняння/Показникові рівняння/завдання.tex"),
       ("Показникові нерівності",        "29. Показникові нерівності/завдання.tex")]
OUT = "Показникові_рівняння_нерівності_функція.tex"

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

EXPO = re.compile(r"\^\s*\{[^{}]*[A-Za-zА-Яа-я\\][^{}]*\}|\^\s*\\?[A-Za-z]")
def pick_item(items):
    """пункт, що стосується показникових: у показнику є змінна; інакше перший"""
    for lab, txt in items:
        if EXPO.search(txt): return lab, txt
    return items[0]

def statement_of(b):
    """текст умови (без \\par і далі) + рік"""
    m = re.search(r"\\zadtask\{", b)
    if m:
        body, _ = arg_at(b, m.end() - 1)
    else:
        m = re.search(r"\\noindent\\zadnum\s*", b)
        body = b[m.end():]
    body = body.split("\\par")[0]
    body = re.sub(r"\s+", " ", body).strip()
    yr = re.search(r"\\nmtyear\{(\d{4})\}", body)
    body = re.sub(r"\s*\\nmtyear\{\d{4}\}", "", body).strip()
    return body, (yr.group(1) if yr else None)

def to_single(b):
    """завдання на відповідність -> тестове з одним пунктом і п'ятьма варіантами"""
    i = b.find("\\matchingLayout")
    if i < 0: return None
    c1, j = arg_at(b, b.index("{", i))
    c2, j = arg_at(b, j)
    items, opts = items_of(c1), items_of(c2)
    if len(items) < 2 or len(opts) != 5: return None
    lab, item = pick_item(items)
    stmt, year = statement_of(b)
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
    if letter: out.append("% Відповідь: %s" % letter)
    out.append("\\zadtask{%s%s}" % (stmt, (" \\nmtyear{%s}" % year) if year else ""))
    out.append("\\answerRows{%s}" % "}{".join(t for _, t in opts))
    out.append("\\par\\penalty-20")
    out.append("\\end{samepage}\n")
    return "\n".join(out)

def preamble():
    p = os.path.join(ROOT, "29. Показникові нерівності/завдання.tex")
    s = open(p, encoding="utf-8").read()
    pre = s[:s.index("\\begin{document}")]
    pre = re.sub(r"\\fancyhead\[C\]\{[^\n]*\}",
                 "\\\\fancyhead[C]{\\\\small\\\\color{gray!80} Показникові вирази, функція, рівняння і нерівності}", pre, count=1)
    pre += ("% варіанти відповіді окремими рядками (довгі вирази не влазять у клітинки таблиці)\n"
            "\\newcommand{\\answerRows}[5]{\\par\\nopagebreak\\vspace{0.15cm}%\n"
            "\\matchItem{А}{#1}\\matchItem{Б}{#2}\\matchItem{В}{#3}\\matchItem{Г}{#4}\\matchItem{Д}{#5}}\n")
    return pre

def carried_macros():
    """макроси, які теми означують після \\begin{document} (matchingLayout тощо)"""
    src = open(os.path.join(ROOT, SRC[0][1]), encoding="utf-8").read()
    a = src.index("\\begin{document}") + len("\\begin{document}")
    b = src.index("\\chapterTitle{", a)
    return src[a:b].strip("\n")

def main():
    out = [preamble(), "\\begin{document}\n" + carried_macros() + "\n\\setcounter{zad}{0}\n"]
    out.append("\\chapterTitle{Показникові вирази, функція, рівняння і нерівності}\n")
    stat = []
    for title, path in SRC:
        bs = blocks(path)
        matched = [(b, to_single(b)) for b in bs if kind(b) == "matching"]
        conv = [c for _, c in matched if c]
        kept = [b for b, c in matched if not c]
        singles = [b for b in bs if kind(b) == "single"]
        other = [b for b in bs if kind(b) not in ("single", "matching")] + kept
        out.append("\\typeTitle{%s}\n" % title)
        for b in singles: out.append("\\begin{samepage}\n" + b.strip() + "\n\\end{samepage}\n")
        for c in conv: out.append(c)
        for b in other: out.append("\\begin{samepage}\n" + b.strip() + "\n\\end{samepage}\n")
        stat.append("%s: %d (з них %d зроблено з завдань на відповідність)" % (title, len(singles) + len(conv) + len(other), len(conv)))
    out.append("\\end{document}\n")
    txt = unicodedata.normalize("NFC", "\n".join(out))
    open(os.path.join(ROOT, OUT), "w", encoding="utf-8").write(txt)
    print("записано", OUT)
    for s in stat: print("   ", s)

if __name__ == "__main__":
    main()
