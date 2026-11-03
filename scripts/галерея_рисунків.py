# -*- coding: utf-8 -*-
"""Галерея рисунків бази: усі рисунки TikZ / pgfplots з файлів тем на кількох сторінках -- щоб одним поглядом звірити
оформлення (розмір, товщина ліній, точки, підписи, сітки, кольори) з правилами scripts/дизайн/ПРАВИЛА.md.

    python3 scripts/галерея_рисунків.py [ВИХІД.pdf] [--теми 11 12 ...]

Кожен рисунок -- у клітинці 3 x N у натуральному розмірі (ширші за клітинку зменшено, як \\begin{nmtfit} у завданні),
під ним -- id завдання, рік і тема. Компілюється в тимчасовій теці; шрифти й рисунки-файли -- як у файлах тем."""
import os, re, sys, subprocess, tempfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "варіант_нмт"))
import спільне as SP                      # noqa: E402
import варіант as V                       # noqa: E402

РИС = re.compile(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", re.S)


def рисунки(блок):
    б = re.sub(r"(?<!\\)%[^\n]*", "%", блок)
    return РИС.findall(б)


def main():
    args = [a for a in sys.argv[1:]]
    теми = None
    if "--теми" in args:
        i = args.index("--теми"); теми = set(args[i + 1:]); args = args[:i]
    вихід = os.path.abspath(args[0]) if args else os.path.join(ROOT, "галерея_рисунків.pdf")
    файли = [f for _, f in SP.файли_тем()]
    s = [V.преамбула("Галерея рисунків", "Галерея рисунків"), "\\begin{document}", "\\relpenalty=10000 \\binoppenalty=10000"]
    for f in файли:
        s.append(V.тіло_теми(f))
    s.append("\\setlength{\\parindent}{0pt}\\setlength{\\fboxsep}{3pt}\\setcounter{zad}{0}")
    # рисунок -- аргументом макроса, як у \\zadtask{...} (у джерелах «##» у \\foreach розраховано саме на це)
    s.append("\\newcommand{\\галкл}[3]{\\begin{minipage}[t]{0.32\\textwidth}\\centering\\begin{nmtfit}#1\\end{nmtfit}\\par\\vspace{1mm}"
             "{\\tiny\\color{gray}#2}\\end{minipage}#3}")
    s.append("\\chapterTitle{Галерея рисунків бази}")
    n = 0
    бачені = set()
    for t in SP.завдання_бази():
        if теми and not (set(t.get("теми", [])) & теми): continue
        for k, р in enumerate(рисунки(t["блок"])):
            ключ = re.sub(r"\s+", "", р)
            if ключ in бачені: continue
            бачені.add(ключ)
            n += 1
            підпис = "%s%s · %s · т.~%s" % (t["id"], "" if k == 0 else "/%d" % (k + 1), t.get("рік") or "?", ",".join(t.get("теми", [])))
            s.append("\\галкл{%s}{%s}{%s}" % (р, підпис, "\\par\\vspace{4mm}\n" if n % 3 == 0 else "\\hfill\n"))
    s.append("\\end{document}")
    tmp = tempfile.mkdtemp(prefix="галерея_")
    src = os.path.join(ROOT, "варіанти", "_галерея.tex")       # як варіанти: шрифти ../, теки рисунків тем
    open(src, "w", encoding="utf-8").write(SP.нфк("\n".join(s)))
    try:
        for _ in range(2):
            r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-output-directory=" + tmp, "_галерея.tex"],
                               cwd=os.path.dirname(src), capture_output=True, text=True, timeout=900)
    finally:
        os.remove(src)
    pdf = os.path.join(tmp, "_галерея.pdf")
    if not os.path.exists(pdf):
        print(open(os.path.join(tmp, "_галерея.log"), encoding="utf-8", errors="replace").read()[-3000:]); raise SystemExit("помилка LaTeX")
    log = open(os.path.join(tmp, "_галерея.log"), encoding="utf-8", errors="replace").read()
    print("рисунків:", n, "| помилок LaTeX:", len(re.findall(r"(?m)^! ", log)))
    shutil.copy(pdf, вихід)
    print("готово:", вихід)


if __name__ == "__main__":
    main()
