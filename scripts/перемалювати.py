# -*- coding: utf-8 -*-
"""Перемальовування рисунка завдання за оригіналом НМТ: показати оригінал і перевірити новий TikZ у контексті завдання.

    python3 scripts/перемалювати.py оригінал ID ВИХІД.png              # обріз оригіналу (150 dpi) + чинний TikZ завдання
    python3 scripts/перемалювати.py перевірити ID НОВИЙ.tex ВИХІД.png [--рисунок K]
        # завдання з НОВИМ рисунком (номер K у завданні, від 0) поруч з оригіналом; помилки LaTeX -- у консоль

Готовий рисунок додають у scripts/data/рисунки_за_оригіналом.json: {"id", "рисунок", "tikz", "джерело", "що"} --
будівник підставляє його у файли тем (perемалювати_за_оригіналом). Рисунок пишемо одразу за правилами
scripts/ПРАВИЛА_ОФОРМЛЕННЯ.md: \\node[nmt dot], підписи без розміру (\\normalsize), основні лінії thick, допоміжні thin,
сітка nmt grid з клітинкою 0,5 см (scale=0.5 при step=1), висота ~4,8 см, ширина не більша за місце (minipage)."""
import os, re, sys, json, subprocess, tempfile, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "варіант_нмт"))
import звірка_рисунків as З               # noqa: E402
import спільне as SP                      # noqa: E402
import варіант as V                       # noqa: E402

РИС = re.compile(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", re.S)


def місце_в_оригіналі(i):
    кат = {c["id"]: c for c in json.load(open(os.path.join(HERE, "data", "варіант_каталог.json"), encoding="utf-8"))}
    t = {t["id"]: t for t in SP.завдання_бази()}[i]
    k = кат.get(i, {})
    с2325 = З.сторінки_сесій_2023_25()
    if k.get("сесія_2026"):
        m = re.match(r"2026-(\d+)\.(\d+)-(\d+)", k["сесія_2026"])
        с2026 = З.сторінки_сесій_2026()
        сторінки = с2026.get("%d.%s" % (int(m.group(1)), m.group(2)), []) or list(range(1, З.сторінок(З.PDF_2026) + 1))
        return t, З.PDF_2026, З.знайти_за_текстом(З.PDF_2026, сторінки, З.текст_завдання(t["блок"]), int(m.group(3)))
    д = next((x for x in k.get("довідки", []) if x.get("сесія") in с2325 and x.get("номер")), None)
    if д:
        a, b = с2325[д["сесія"]]
        return t, З.PDF_23_25, З.знайти_за_текстом(З.PDF_23_25, list(range(a, b + 1)), З.текст_завдання(t["блок"]), int(д["номер"]))
    рік = str(t.get("рік"))
    if рік == "2026":
        return t, З.PDF_2026, З.знайти_за_текстом(З.PDF_2026, list(range(1, З.сторінок(З.PDF_2026) + 1)), З.текст_завдання(t["блок"]))
    a, b = {"2023": (5, 85), "2024": (95, 205), "2025": (214, 317)}[рік]
    return t, З.PDF_23_25, З.знайти_за_текстом(З.PDF_23_25, list(range(a, b + 1)), З.текст_завдання(t["блок"]))


def обріз(i, куди, dpi=150):
    t, pdf, знайдено = місце_в_оригіналі(i)
    p, y0, y1 = знайдено[0], знайдено[1], знайдено[2]
    З.DPI = dpi
    З.обрізати_оригінал(pdf, p, y0, y1, куди)
    return t, (os.path.basename(pdf), p)


def скомпілювати(блок, i):
    s = [V.преамбула("Перевірка", "Перевірка"), "\\begin{document}"] + [V.тіло_теми(f) for _, f in SP.файли_тем()]
    s += ["\\pagestyle{empty}\\setcounter{zad}{0}", "\\begin{minipage}{\\textwidth}\n%s\n\\end{minipage}" % V.чистий_блок(блок, True), "\\end{document}"]
    назва = "_перемалювати_%s" % i
    src = os.path.join(ROOT, "варіанти", назва + ".tex")
    open(src, "w", encoding="utf-8").write(SP.нфк("\n".join(s)))
    tmp = tempfile.mkdtemp(prefix="перемал_")
    try:
        r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "-output-directory=" + tmp, назва + ".tex"],
                           cwd=os.path.dirname(src), capture_output=True, text=True, timeout=600)
    finally:
        os.remove(src)
    log = open(os.path.join(tmp, назва + ".log"), encoding="utf-8", errors="replace").read()
    помилки = re.findall(r"(?m)^! .*(?:\n.*){0,2}", log)
    return os.path.join(tmp, назва + ".pdf"), помилки


def скласти(ліве, праве, підписи, куди):
    from PIL import Image, ImageDraw, ImageFont
    шрифт = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 18)
    a, b = Image.open(ліве).convert("RGB"), З.зміст(Image.open(праве).convert("RGB"))
    o = Image.new("RGB", (a.width + b.width + 24, max(a.height, b.height) + 34), "white"); d = ImageDraw.Draw(o)
    d.text((6, 6), підписи[0], fill="#05a", font=шрифт); d.text((a.width + 30, 6), підписи[1], fill="#070", font=шрифт)
    o.paste(a, (0, 30)); o.paste(b, (a.width + 24, 30)); o.save(куди)


def main():
    дія, i = sys.argv[1], sys.argv[2]
    tmp = tempfile.mkdtemp(prefix="перемал_")
    if дія == "оригінал":
        куди = sys.argv[3]
        t, (pdf, p) = обріз(i, куди)
        print("оригінал: %s, с. %d -> %s" % (pdf, p, куди))
        for k, р in enumerate(РИС.findall(t["блок"])):
            print("---- рисунок %d (чинний TikZ) ----\n%s" % (k, р))
        return
    новий, куди = open(sys.argv[3], encoding="utf-8").read().strip(), sys.argv[4]
    k = int(sys.argv[sys.argv.index("--рисунок") + 1]) if "--рисунок" in sys.argv else 0
    t, (pdf, p) = обріз(i, os.path.join(tmp, "ориг.png"))
    лічильник = [-1]
    def заміна(m):
        лічильник[0] += 1
        return новий if лічильник[0] == k else m.group(0)
    блок = РИС.sub(заміна, t["блок"])
    pdf_новий, помилки = скомпілювати(блок, i)
    if помилки:
        print("ПОМИЛКИ LaTeX:\n" + "\n".join(помилки[:5])); sys.exit(1)
    subprocess.run(["pdftoppm", "-f", "1", "-l", "1", "-r", "150", "-singlefile", "-png", pdf_новий, os.path.join(tmp, "нове")], check=True)
    скласти(os.path.join(tmp, "ориг.png"), os.path.join(tmp, "нове.png"), ("ОРИГІНАЛ: %s, с. %d" % (pdf, p), "НОВИЙ РИСУНОК: %s" % i), куди)
    print("готово:", куди)


if __name__ == "__main__":
    main()
