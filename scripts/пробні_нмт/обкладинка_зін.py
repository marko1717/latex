# -*- coding: utf-8 -*-
"""Обкладинка PDF каналу в зін-стилі дизайн-системи ~/nmt-slides (тло-папір, чорнильні рамки з жорсткою тінню, штамп,
маркер, Mulish) -- A4 для збирача оформлення_канал.py. Два режими:

    python3 scripts/пробні_нмт/обкладинка_зін.py ВИХІД.pdf --постер ПОСТЕР.png
    python3 scripts/пробні_нмт/обкладинка_зін.py ВИХІД.pdf --ілюстрація ІЛЮСТРАЦІЯ.png [--варіант 1]

--постер: цілком згенерований постер (scripts/рисунок_api.py, 1024x1536, з написами) -- картка з рамкою й тінню на папері,
щоб відмінність пропорцій 2:3 і A4 не давала обрізаних полів.
--ілюстрація: згенерована ілюстрація БЕЗ написів (1536x1024, на рівному папері) + зверстані написи: штамп «НМТ · МАТЕМАТИКА»,
«ВАРІАНТ N», заголовок із маркером під «НМТ», чипи, канал. Тло сторінки -- колір країв ілюстрації, тож стику не видно.
"""
import os, shutil, tempfile, subprocess, argparse, statistics

ШРИФТИ = os.path.expanduser("~/nmt-slides/design-system/project/fonts/")
КОЛЬОРИ = dict(paper="f5f0ec", surface="fffdfb", ink="2a2622", inkii="5c544c", sage="7c9d85", marker="f7be93", cream="f5f0ec")

ПРЕАМБУЛА = r"""\documentclass{article}
\usepackage[a4paper,margin=0cm]{geometry}
\usepackage{fontspec}
\usepackage[ukrainian]{babel}
\usepackage{xcolor,tikz,graphicx}
\usetikzlibrary{calc,backgrounds}
\setmainfont{Mulish-SemiBold.ttf}[Path=<<fonts>>]
\newfontfamily\mBold{Mulish-Bold.ttf}[Path=<<fonts>>]
\newfontfamily\mXBold{Mulish-ExtraBold.ttf}[Path=<<fonts>>]
\newfontfamily\mBlack{Mulish-Black.ttf}[Path=<<fonts>>]
\newfontfamily\mCaps{Mulish-ExtraBold.ttf}[Path=<<fonts>>, LetterSpace=12]
\newfontfamily\mTitle{Mulish-Black.ttf}[Path=<<fonts>>, LetterSpace=2]
<<colors>>
\pagestyle{empty}
\pagecolor{pagebg}
\tikzset{
  sh/.style={preaction={fill=ink, draw=ink, transform canvas={shift={(1.3mm,-1.3mm)}}}},
  pill/.style={draw=ink, line width=0.8mm, rounded corners=5mm, inner xsep=5mm, inner ysep=2.6mm},
}
\begin{document}
\begin{tikzpicture}[remember picture, overlay, x=1cm, y=1cm]
\coordinate (O) at (current page.south west);
\begin{scope}[shift={(O)}]
"""
КІНЕЦЬ = r"""
\end{scope}
\end{tikzpicture}
\end{document}
"""

# цілком згенерований постер -- картка на папері
ПОСТЕР = r"""
\fill[ink, rounded corners=3.8mm] (<<x0>>+0.16,<<y0>>-0.16) rectangle (<<x1>>+0.16,<<y1>>-0.16);
\begin{scope}
  \clip[rounded corners=3.8mm] (<<x0>>,<<y0>>) rectangle (<<x1>>,<<y1>>);
  \node[anchor=south west, inner sep=0] at (<<x0>>,<<y0>>) {\includegraphics[width=<<w>>cm,height=<<h>>cm]{art.png}};
\end{scope}
\draw[ink, line width=0.85mm, rounded corners=3.8mm] (<<x0>>,<<y0>>) rectangle (<<x1>>,<<y1>>);
"""

# зверстані написи + згенерована ілюстрація
ІЛЮСТРАЦІЯ = r"""
% ---- штамп і пігулка
\node[pill, sh, fill=sage, rotate=-4, anchor=west, font=\mCaps\fontsize{17}{20}\selectfont, text=ink] at (1.7,27.45) {НМТ · МАТЕМАТИКА};
\node[anchor=west, fill=ink, text=cream, rounded corners=5mm, inner xsep=5mm, inner ysep=2.6mm,
      font=\mCaps\fontsize{15}{18}\selectfont] at (1.8,25.55) {ВАРІАНТ <<variant>>};

% ---- заголовок, «НМТ» на маркері
\node[anchor=base west, inner sep=0, text=ink, font=\mTitle\fontsize{62}{64}\selectfont] at (1.55,22.45) {АВТОРСЬКИЙ};
\node[anchor=base west, inner sep=0, text=ink, font=\mTitle\fontsize{62}{64}\selectfont] (p) at (1.55,20.15) {ПРОБНИЙ};
\node[anchor=base west, inner sep=0, text=ink, font=\mTitle\fontsize{62}{64}\selectfont] (n) at ($(p.base east)+(0.62,0)$) {НМТ};
\begin{scope}[on background layer]
  \fill[marker] ($(n.base west)+(-0.2,-0.22)$) rectangle ($(n.base east)+(0.2,0.95)$);
\end{scope}

% ---- чипи
\node[pill, sh, fill=surface, anchor=west, font=\mXBold\fontsize{14}{16}\selectfont, text=ink] (c1) at (1.8,18.35) {22 завдання};
\node[pill, sh, fill=surface, anchor=west, font=\mXBold\fontsize{14}{16}\selectfont, text=ink] (c2) at ($(c1.east)+(0.55,0)$) {32 бали};
\node[pill, sh, fill=surface, anchor=west, font=\mXBold\fontsize{14}{16}\selectfont, text=ink] (c3) at ($(c2.east)+(0.55,0)$) {усі теми};

% ---- ілюстрація на всю ширину (поля -- того ж паперу, що й сторінка)
\node[anchor=north, inner sep=0] at (10.5,17.35) {\includegraphics[width=22cm]{art.png}};

% ---- канал і зміст
\node[pill, sh, fill=surface, anchor=west, font=\mBlack\fontsize{16}{18}\selectfont, text=ink] (tg) at (1.8,1.6)
  {\tikz[baseline=-0.7ex, scale=0.5]{\fill[ink] (0,0) -- (1,0.42) -- (0.33,-0.1) -- cycle; \fill[ink] (0.33,-0.1) -- (0.42,-0.5) -- (0.55,-0.02) -- cycle;}\ \ @pvtr2525};
\node[anchor=west, text width=11.6cm, align=left, text=inkii, font=\mBold\fontsize{12}{15}\selectfont] at ($(tg.east)+(0.6,0)$)
  {Усередині: про автора, довідкові матеріали,\\ варіант і відповіді на останній сторінці};
"""


def колір_краю(png):
    """медіанний колір смуги вздовж країв зображення (тло згенерованої ілюстрації)"""
    from PIL import Image
    im = Image.open(png).convert("RGB"); W, H = im.size
    px = [im.getpixel((x, y)) for x in range(0, W, 5) for y in (2, 6, H - 3, H - 7)]
    px += [im.getpixel((x, y)) for y in range(0, H, 5) for x in (2, 6, W - 3, W - 7)]
    return "%02X%02X%02X" % tuple(int(statistics.median(c)) for c in zip(*px))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("вихід")
    г = ap.add_mutually_exclusive_group(required=True)
    г.add_argument("--постер"); г.add_argument("--ілюстрація")
    ap.add_argument("--варіант", default="1")
    a = ap.parse_args()
    from PIL import Image
    tmp = tempfile.mkdtemp(prefix="обкладинка_")
    малюнок = a.постер or a.ілюстрація
    shutil.copy(малюнок, os.path.join(tmp, "art.png"))
    кольори = dict(КОЛЬОРИ)
    if a.постер:
        кольори["pagebg"] = КОЛЬОРИ["paper"]
        w0, h0 = Image.open(малюнок).size
        h = 29.7 - 2 * 0.95; w = h * w0 / h0                 # вписати у висоту з полями 0,95 см
        if w > 21 - 2 * 0.95: w = 21 - 2 * 0.95; h = w * h0 / w0
        x0, y0 = (21 - w) / 2 - 0.08, (29.7 - h) / 2 + 0.08  # тінь праворуч-униз -- зсув на її половину
        тіло = ПОСТЕР
        for k, v in dict(x0=x0, y0=y0, x1=x0 + w, y1=y0 + h, w=w, h=h).items():
            тіло = тіло.replace("<<%s>>" % k, "%.3f" % v)
    else:
        кольори["pagebg"] = колір_краю(малюнок)
        тіло = ІЛЮСТРАЦІЯ.replace("<<variant>>", a.варіант)
    визн = "\n".join(r"\definecolor{%s}{HTML}{%s}" % (k, v.upper()) for k, v in кольори.items())
    tex = ПРЕАМБУЛА.replace("<<fonts>>", ШРИФТИ).replace("<<colors>>", визн) + тіло + КІНЕЦЬ
    open(os.path.join(tmp, "обкладинка.tex"), "w", encoding="utf-8").write(tex)
    for _ in range(2):
        r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "обкладинка.tex"], cwd=tmp, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-2500:]); raise SystemExit("помилка LaTeX")
    shutil.copy(os.path.join(tmp, "обкладинка.pdf"), a.вихід)
    print("готово:", a.вихід, "| тло", кольори["pagebg"])


if __name__ == "__main__":
    main()
