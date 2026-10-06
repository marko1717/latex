# -*- coding: utf-8 -*-
"""Пробний НМТ для каналу в оформленні авторських варіантів (як «4 червня автор 2.pdf»): обкладинка (PNG, згенерована через
OpenAI Images API, scripts/рисунок_api.py, або готова A4 з scripts/пробні_нмт/обкладинка_зін.py -- PDF), сторінка «Про мене» й довідкові матеріали (готові сторінки PDF), авторський
варіант (заголовок «АВТОРСЬКИЙ ВАРІАНТ НМТ», колонтитул «Авторський варіант НМТ», водяний знак @pvtr2525) і наприкінці --
сторінка «ВІДПОВІДІ» (1--15 стовпчиками, 16--18 парами, 19--22 числами).

    python3 scripts/пробні_нмт/оформлення_канал.py пробні/канал_1 ОБКЛАДИНКА.png|.pdf ПРО_МЕНЕ_І_ДОВІДКОВІ.pdf ВИХІД.pdf [--сторінки 2-5]

ПРО_МЕНЕ_І_ДОВІДКОВІ.pdf -- PDF, з якого беруться сторінки «Про мене» й довідкових (за замовчуванням 2--5, як в авторському
варіанті за 4 червня).

--дизайн зін -- варіант у темі «зін» (scripts/пробні_нмт/тема_зін.py: картки, мітки, папір, Mulish -- як обкладинка й «Про мене»);
--текст schoolbook -- у цій темі текст завдань шрифтом бази, а не Mulish.
"""
import os, re, sys, json, shutil, tempfile, subprocess, argparse, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "варіант_нмт"))
import пробний as П                         # noqa: E402
from аналоги import компілювати             # noqa: E402

НАЗВА = "АВТОРСЬКИЙ ВАРІАНТ НМТ"
КОЛОНТИТУЛ = "Авторський варіант НМТ"
ІНСТРУКЦІЇ = {   # як в авторських варіантах каналу (без окремого бланка відповідей)
    1: "Завдання 1--15 мають по п'ять варіантів відповіді, з яких лише один правильний. Виберіть правильний варіант відповіді й позначте його.",
    16: "Завдання 16--18 на встановлення відповідності. До кожного рядка (1--3) доберіть один правильний варіант (А--Д).",
    19: "Завдання 19--22 з короткою числовою відповіддю. Одержану відповідь запишіть у спеціально відведеному місці.",
}


def сторінка_відповідей(завдання):
    в = {z["номер"]: z["відповідь"] for z in завдання}
    рядки = []
    for r in range(3):                                    # 1--15: п'ять стовпчиків по три
        рядки.append(" & ".join("\\textbf{%d.} %s" % (3 * c + r + 1, в[3 * c + r + 1]) for c in range(5)) + " \\\\")
    відп = "\\hspace{1.2cm}".join("\\textbf{%d.} %s" % (n, ", ".join("%d~--~%s" % (i + 1, x) for i, x in enumerate(в[n]))) for n in (16, 17, 18))
    кор = "\\hspace{1.6cm}".join("\\textbf{%d.} $%s$" % (n, re.sub(r"[.,]", "{,}", str(в[n]))) for n in (19, 20, 21, 22))
    return ("\\chapterTitle{ВІДПОВІДІ}\n"
            "\\noindent\\textbf{Завдання 1--15} (вибір однієї правильної відповіді):\\par\\vspace{0.3cm}\n"
            "\\noindent\\begin{tabular}{@{}*{5}{p{0.18\\linewidth}}@{}}\n" + "\n".join(рядки) + "\n\\end{tabular}\\par\\vspace{0.6cm}\n"
            "\\noindent\\textbf{Завдання 16--18} (встановлення відповідності):\\par\\vspace{0.3cm}\n"
            "\\noindent " + відп + "\\par\\vspace{0.6cm}\n"
            "\\noindent\\textbf{Завдання 19--22} (коротка числова відповідь):\\par\\vspace{0.3cm}\n"
            "\\noindent " + кор + "\\par\n")


def обкладинка_pdf(png, куди):
    """A4: готовий PDF (обкладинка_зін.py) -- як є; PNG вписано за висотою, по центру, поля кольору країв зображення"""
    if png.lower().endswith(".pdf"):
        subprocess.run(["pdfseparate", "-f", "1", "-l", "1", png, куди], check=True); return
    from PIL import Image
    from обкладинка_зін import колір_краю
    W, H = 2480, 3508                                     # A4 при 300 dpi
    im = Image.open(png).convert("RGB")
    k = min(W / im.width, H / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.LANCZOS)
    стор = Image.new("RGB", (W, H), "#" + колір_краю(png))
    стор.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
    стор.save(куди, "PDF", resolution=300.0, quality=92)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("тека"); ap.add_argument("обкладинка"); ap.add_argument("про_мене"); ap.add_argument("вихід")
    ap.add_argument("--сторінки", default="2-5", help="сторінки «Про мене» й довідкових із ПРО_МЕНЕ_І_ДОВІДКОВІ.pdf")
    ap.add_argument("--дизайн", choices=["класичний", "зін"], default="класичний")
    ap.add_argument("--текст", choices=["mulish", "schoolbook"], default="mulish", help="шрифт тексту в темі «зін»")
    ap.add_argument("--про-мене", dest="про_мене_pdf", default=None,
                    help="окрема сторінка «Про мене» (scripts/пробні_нмт/про_мене.py); тоді з ПРО_МЕНЕ_І_ДОВІДКОВІ.pdf беруться лише довідкові 3--5")
    a = ap.parse_args()
    тека = os.path.abspath(a.тека)
    spec = importlib.util.spec_from_file_location("спец_канал", os.path.join(тека, "спец.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    завдання = json.load(open(os.path.join(тека, "завдання.json"), encoding="utf-8"))
    К = dict(m.КОНФІГ, назва=НАЗВА, колонтитул=КОЛОНТИТУЛ, вступ="")
    стара = dict(П.V.ІНСТРУКЦІЇ); П.V.ІНСТРУКЦІЇ.clear(); П.V.ІНСТРУКЦІЇ.update(ІНСТРУКЦІЇ)
    try:
        tex = П.документ(К, завдання)
    finally:
        П.V.ІНСТРУКЦІЇ.clear(); П.V.ІНСТРУКЦІЇ.update(стара)
    tex = tex.replace("\\noindent{\\small }\\par\\vspace{0.4cm}\n", "")                 # порожній вступ
    if a.дизайн == "зін":
        import тема_зін
        номер = (re.findall(r"(\d+)$", os.path.basename(тека)) or ["1"])[0]
        tex = тема_зін.застосувати(tex, НАЗВА, "НМТ · МАТЕМАТИКА · ВАРІАНТ %s" % номер, КОЛОНТИТУЛ.upper(),
                                   заголовок="Авторський \\zinMarker{варіант НМТ}", текст=a.текст)
        tex = tex.replace("\\end{document}", тема_зін.сторінка_відповідей(завдання) + "\\end{document}")
    else:
        tex = tex.replace("\\end{document}", сторінка_відповідей(завдання) + "\\end{document}")
    tmp = tempfile.mkdtemp(prefix="канал_")
    компілювати(tex, tmp, "канал_оформлення")
    ok, err, pdf, over = компілювати(tex, tmp, "канал_оформлення")
    if not ok: raise SystemExit("помилка LaTeX\n" + err)
    print("варіант: рядків за полем", over)
    обкладинка_pdf(a.обкладинка, os.path.join(tmp, "0_обкладинка.pdf"))
    f, l = ("3", "5") if a.про_мене_pdf and a.сторінки == "2-5" else a.сторінки.split("-")
    subprocess.run(["pdfseparate", "-f", f, "-l", l, a.про_мене, os.path.join(tmp, "1_стор_%d.pdf")], check=True)
    сторінки = [os.path.join(tmp, "1_стор_%d.pdf" % i) for i in range(int(f), int(l) + 1)]
    if a.про_мене_pdf: сторінки = [a.про_мене_pdf] + сторінки
    subprocess.run(["pdfunite", os.path.join(tmp, "0_обкладинка.pdf")] + сторінки + [pdf, a.вихід], check=True)
    open(os.path.splitext(a.вихід)[0] + ".tex", "w", encoding="utf-8").write(tex)
    print("готово:", a.вихід)


if __name__ == "__main__":
    main()
