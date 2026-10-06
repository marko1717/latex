# -*- coding: utf-8 -*-
"""Сторінка «Про мене» для PDF каналу -- зверстана в зін-стилі (дизайн-система ~/nmt-slides/design-system: тло-папір,
картки з чорнильною рамкою й жорсткою тінню, штампи, маркер, Mulish), зі справжнім фото й QR-кодом на канал.
Без згенерованих картинок і декору.

    python3 scripts/пробні_нмт/про_мене.py ФОТО.png ВИХІД.pdf

Тексти -- у константах нижче (звертання на «ти», гендерно нейтрально).
"""
import os, sys, shutil, tempfile, subprocess

ШРИФТИ = os.path.expanduser("~/nmt-slides/design-system/project/fonts/")
КАНАЛ = "t.me/pvtr2525"
# палітра зін-системи (tokens.json, світла тема)
КОЛЬОРИ = dict(paper="f5f0ec", surface="fffdfb", surface2="f9f6f2", ink="2a2622", inkii="5c544c", muted="736b62",
               sage="7c9d85", sagetint="eaf2e3", sageink="42604b", orange="ef8748", orangetint="fdeee2", orangeink="9a4a17",
               marker="f7be93", bossmuted="cfc7bc", cream="f5f0ec")
ЩО_Є = ["Теорію у зрозумілому форматі", "Авторські завдання різних рівнів", "Практику, тести й розбори варіантів",
        "Поради та лайфхаки", "Мотивацію й підтримку на кожному етапі"]

TEX = r"""\documentclass{article}
\usepackage[a4paper,margin=0cm]{geometry}
\usepackage{fontspec}
\usepackage[ukrainian]{babel}
\usepackage{xcolor,tikz,graphicx}
\usetikzlibrary{calc,backgrounds}
\setmainfont{Mulish-SemiBold.ttf}[Path=<<fonts>>]
\newfontfamily\mBold{Mulish-Bold.ttf}[Path=<<fonts>>]
\newfontfamily\mXBold{Mulish-ExtraBold.ttf}[Path=<<fonts>>]
\newfontfamily\mBlack{Mulish-Black.ttf}[Path=<<fonts>>]
\newfontfamily\mCaps{Mulish-ExtraBold.ttf}[Path=<<fonts>>, LetterSpace=14]
<<colors>>
\pagestyle{empty}
\pagecolor{paper}
\setlength{\parindent}{0pt}
\tikzset{
  plate/.style={draw=ink, line width=0.85mm, rounded corners=3.8mm},
  shadowed/.style={preaction={fill=ink, draw=ink, line width=0.85mm, rounded corners=3.8mm, transform canvas={shift={(1.25mm,-1.25mm)}}}},
  stamp/.style={draw=ink, line width=0.75mm, rounded corners=4.5mm, inner xsep=4mm, inner ysep=2mm,
                font=\mCaps\fontsize{11}{13}\selectfont, text=ink},
}
\begin{document}
\hyphenpenalty=10000 \exhyphenpenalty=10000   % без переносів слів
\begin{tikzpicture}[remember picture, overlay, x=1cm, y=1cm]
\coordinate (O) at (current page.south west);
\begin{scope}[shift={(O)}]

% ---- шапка
\node[anchor=west, text=muted, font=\mCaps\fontsize{10.5}{12}\selectfont] at (1.6,27.95) {АВТОР КАНАЛУ · @PVTR2525};
\node[anchor=base west, inner sep=0, font=\mBlack\fontsize{42}{46}\selectfont, text=ink] (hi) at (1.6,26.15) {Привіт! Я};
\node[anchor=base west, inner sep=0, font=\mBlack\fontsize{42}{46}\selectfont, text=ink] (name) at ($(hi.base east)+(0.42,0)$) {Маркіян};
\begin{scope}[on background layer]
  \fill[marker] ($(name.base west)+(-0.12,-0.12)$) rectangle ($(name.base east)+(0.12,0.62)$);
\end{scope}
\node[anchor=north west, text width=17.6cm, align=left, text=inkii, font=\fontsize{13.5}{19}\selectfont] at (1.6,25.35)
  {Готую до НМТ з математики так, щоб на тесті жодне завдання не лякало: пояснюю просто, даю багато практики
   і складаю власні завдання у форматі справжнього НМТ.};

% ---- фото
\begin{scope}
  \fill[ink, rounded corners=3.8mm] (1.6+0.125,10.75-0.125) rectangle (7.6+0.125,22.8-0.125);
  \begin{scope}
    \clip[rounded corners=3.8mm] (1.6,10.75) rectangle (7.6,22.8);
    \node[anchor=south west, inner sep=0] at (1.6,10.75) {\includegraphics[width=6cm,height=12.05cm]{photo.png}};
  \end{scope}
  \draw[plate] (1.6,10.75) rectangle (7.6,22.8);
\end{scope}

% ---- про канал
\draw[plate, fill=surface, shadowed] (8.35,19.15) rectangle (19.4,22.8);
\node[anchor=west, fill=ink, text=cream, rounded corners=2.6mm, inner xsep=3mm, inner ysep=1.4mm,
      font=\mCaps\fontsize{9.5}{11}\selectfont] at (8.95,22.8) {ПРО КАНАЛ};
\node[anchor=north west, text width=10.2cm, align=left, text=ink, font=\fontsize{12.5}{17.5}\selectfont] at (8.85,22.2)
  {{\mBlack @pvtr2525} -- твій помічник на шляху до високого бала НМТ з математики. Тут є все для підготовки:
   зрозумілі пояснення, корисні матеріали, авторські завдання і багато практики.};

% ---- що на каналі
\node[anchor=west, text=ink, font=\mBlack\fontsize{17}{20}\selectfont] at (8.35,18.25) {Що ти знайдеш на каналі};
<<rows>>

% ---- лайфхак: як працювати з варіантом
\draw[plate, fill=orangetint, shadowed] (1.6,6.95) rectangle (19.4,9.75);
\node[anchor=west, fill=surface, draw=ink, line width=0.7mm, rounded corners=2.6mm, inner xsep=3mm, inner ysep=1.3mm,
      text=orangeink, font=\mCaps\fontsize{9.5}{11}\selectfont] at (2.2,9.75) {ЛАЙФХАК};
\node[anchor=north west, text width=16.9cm, align=left, text=ink, font=\fontsize{12.5}{17.5}\selectfont] at (2.1,9.2)
  {Розв'язуй усі 22 завдання поспіль і з таймером -- як на справжньому НМТ. Відповіді -- на останній сторінці:
   {\mBlack звір їх лише тоді, коли закінчиш увесь варіант}.};

% ---- заклик і QR
\fill[orange, rounded corners=4.8mm] (1.6+0.2,1.45-0.2) rectangle (19.4+0.2,5.75-0.2);
\draw[draw=ink, line width=0.85mm, fill=ink, rounded corners=4.8mm] (1.6,1.45) rectangle (19.4,5.75);
\node[anchor=north west, text=cream, font=\mBlack\fontsize{26}{30}\selectfont] at (2.3,5.05) {Підписуйся на канал};
\node[anchor=north west, text width=11.2cm, align=left, text=bossmuted, font=\fontsize{12.5}{17}\selectfont] at (2.3,3.75)
  {Зливи, практика й розбори -- усе для твого успіху на НМТ. Наведи камеру на QR-код або знайди
   {\mBlack\color{cream}@pvtr2525} у Telegram.};
\fill[cream, rounded corners=2.5mm] (14.95,1.85) rectangle (18.95,5.35);
\node[inner sep=0] at (16.95,3.75) {\includegraphics[width=2.75cm]{qr.png}};
\node[text=ink, font=\mXBold\fontsize{9}{10}\selectfont] at (16.95,2.1) {<<channel>>};
\node[stamp, fill=orange, rotate=-4, shadowed] at (10.9,5.75) {БУДЬ НА КРОК ПОПЕРЕДУ};
\node[stamp, fill=sage, rotate=-4, shadowed] at (4.6,11.45) {ГОТУЙСЯ · ПЕРЕМАГАЙ};

\end{scope}
\end{tikzpicture}
\end{document}
"""


def рядки():
    out, y = [], 17.35
    for i, t in enumerate(ЩО_Є, 1):
        y0, y1 = y - 1.12, y
        out.append(r"\draw[plate, fill=surface, line width=0.8mm, rounded corners=3.4mm, shadowed] (8.35,%.2f) rectangle (19.4,%.2f);" % (y0, y1))
        out.append(r"\draw[fill=surface2, draw=ink, line width=0.7mm, rounded corners=2mm] (8.65,%.2f) rectangle (9.45,%.2f);" % (y0 + 0.16, y1 - 0.16))
        out.append(r"\node[text=ink, font=\mBlack\fontsize{14}{16}\selectfont] at (9.05,%.2f) {%d};" % ((y0 + y1) / 2, i))
        out.append(r"\node[anchor=west, text=ink, font=\mBold\fontsize{12.5}{15}\selectfont] at (9.8,%.2f) {%s};" % ((y0 + y1) / 2, t))
        y = y0 - 0.32
    return "\n".join(out)


def main(фото, вихід):
    import qrcode
    tmp = tempfile.mkdtemp(prefix="про_мене_")
    shutil.copy(фото, os.path.join(tmp, "photo.png"))
    qr = qrcode.QRCode(border=0, box_size=20, error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data("https://" + КАНАЛ); qr.make(fit=True)
    qr.make_image(fill_color="#" + КОЛЬОРИ["ink"], back_color="#" + КОЛЬОРИ["cream"]).save(os.path.join(tmp, "qr.png"))
    кольори = "\n".join(r"\definecolor{%s}{HTML}{%s}" % (k, v.upper()) for k, v in КОЛЬОРИ.items())
    tex = TEX.replace("<<fonts>>", ШРИФТИ).replace("<<colors>>", кольори).replace("<<rows>>", рядки()).replace("<<channel>>", КАНАЛ)
    open(os.path.join(tmp, "про_мене.tex"), "w", encoding="utf-8").write(tex)
    for _ in range(2):
        r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "про_мене.tex"], cwd=tmp, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-2500:]); raise SystemExit("помилка LaTeX")
    shutil.copy(os.path.join(tmp, "про_мене.pdf"), вихід)
    print("готово:", вихід)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
