# -*- coding: utf-8 -*-
"""Перевірка набраних завдань ЗНО: компіляція з макросами бази, кожне завдання -- окрема сторінка
з оригінальним номером, рендер у PNG для порівняння з оригінальною сторінкою зошита.

    python3 scripts/зно_офіційні/перевірити.py ЗАВДАННЯ.json ТЕКА_PNG
ЗАВДАННЯ.json -- список {"номер": 5, "latex": "..."}; у ТЕКА_PNG з'являються зно_05.png тощо.
Друкує стан компіляції кожного завдання; якщо спільна компіляція падає, шукає винні завдання поодинці.
"""
import os, re, sys, json, glob, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts", "варіант_нмт"))
import варіант as V                                    # noqa: E402
from спільне import як_у_базі, файли_тем, нфк          # noqa: E402
from аналоги import компілювати                        # noqa: E402

МАКРОСИ = open(os.path.join(HERE, "макроси.tex"), encoding="utf-8").read()


def документ(tasks):
    out = [V.преамбула("Перевірка ЗНО", "Перевірка ЗНО") + МАКРОСИ, "\\begin{document}",
           V.тіло_теми(файли_тем()[0][1]) + "\n"]
    for t in tasks:
        out.append("\\setcounter{zad}{%d}\n\\begin{samepage}\n%s\n\\end{samepage}\n\\clearpage\n" % (int(t["номер"]) - 1, як_у_базі(t["latex"])))
    out.append("\\end{document}\n")
    return нфк("\n".join(out))


def main():
    tasks = json.load(open(sys.argv[1], encoding="utf-8"))
    tasks = tasks.get("tasks", tasks) if isinstance(tasks, dict) else tasks
    for t in tasks:                                   # номер може бути записано як «n»
        if "номер" not in t and "n" in t: t["номер"] = t["n"]
    out_dir = sys.argv[2]; os.makedirs(out_dir, exist_ok=True)
    work = tempfile.mkdtemp(prefix="зно_")
    ok, err, pdf, over = компілювати(документ(tasks), work, "зно")
    if not ok:
        print("СПІЛЬНА КОМПІЛЯЦІЯ ПАДАЄ:", err.splitlines()[0] if err else "?")
        for t in tasks:
            ok1, err1, _, _ = компілювати(документ([t]), work, "зно1")
            print("  №%s: %s" % (t["номер"], "ok" if ok1 else "ПОМИЛКА " + (err1.splitlines()[0] if err1 else "")))
        return
    for f in glob.glob(os.path.join(out_dir, "зно_*.png")): os.remove(f)
    subprocess.run(["pdftoppm", "-r", "100", "-png", pdf, os.path.join(work, "p")], check=True)
    pages = sorted(glob.glob(os.path.join(work, "p-*.png")))
    if len(pages) != len(tasks):
        print("! сторінок %d, завдань %d -- якесь завдання не вмістилося на одну сторінку" % (len(pages), len(tasks)))
    for t, p in zip(tasks, pages):
        os.replace(p, os.path.join(out_dir, "зно_%02d.png" % int(t["номер"])))
    print("компіляція ok; завдань %d; рядків, що вилазять за поле: %d; PNG у %s" % (len(tasks), over, out_dir))


if __name__ == "__main__":
    main()
