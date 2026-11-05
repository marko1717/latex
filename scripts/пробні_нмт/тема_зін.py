# -*- coding: utf-8 -*-
"""Тема «зін» для авторського варіанта -- оформлення дизайн-системи ~/nmt-slides (як обкладинка й «Про мене»): тло-папір,
кожне завдання -- картка з чорнильною рамкою й жорсткою тінню і номером-пігулкою на верхній рамці, варіанти А--Д --
картки з літерою-міткою, відповідність -- мітки 1--3 (темні) й А--Д (світлі) і сітка із заокруглених клітинок, поле
відповіді -- клітинки, інструкції -- помаранчеві картки «ЧАСТИНА N», сторінка відповідей -- картки «правильно» (шавлія).

Перевизначає макроси бази (\\zadtask, \\zadnum, \\answerTable, \\matchingLayout, \\matchItem, \\matchingGrid,
\\nmtAnswerBox, \\instructionBox) -- самі завдання не змінюються. Формули лишаються Schoolbook (mathastext), текст --
Mulish (текст="mulish") або Schoolbook (текст="schoolbook"). Водяний знак -- поверх карток, напівпрозорий.

    import тема_зін
    tex = тема_зін.застосувати(tex, назва, eyebrow, шапка)
    tex = tex.replace("\\end{document}", тема_зін.сторінка_відповідей(завдання) + "\\end{document}")
"""
import os, re

ШРИФТИ = os.path.expanduser("~/nmt-slides/design-system/project/fonts/")

ОСНОВА = r"""
% ===================== ТЕМА «ЗІН» (дизайн-система ~/nmt-slides) =====================
\usetikzlibrary{backgrounds}
\tcbuselibrary{raster}
\definecolor{zinPaper}{HTML}{F5F0EC}
\definecolor{zinSurface}{HTML}{FFFDFB}
\definecolor{zinSurfaceII}{HTML}{F9F6F2}
\definecolor{zinInk}{HTML}{2A2622}
\definecolor{zinInkII}{HTML}{5C544C}
\definecolor{zinMuted}{HTML}{736B62}
\definecolor{zinSage}{HTML}{7C9D85}
\definecolor{zinSageTint}{HTML}{EAF2E3}
\definecolor{zinSageInk}{HTML}{42604B}
\definecolor{zinOrange}{HTML}{EF8748}
\definecolor{zinOrangeTint}{HTML}{FDEEE2}
\definecolor{zinMarker}{HTML}{F7BE93}
\definecolor{zinCream}{HTML}{F5F0EC}
\colorlet{mainGreen}{zinSage}      % заливки рисунків бази -- у палітрі зіну
\colorlet{yearOrange}{zinOrange}
\pagecolor{zinPaper}
\newfontfamily\zinSemi{Mulish-SemiBold.ttf}[Path=<<fonts>>, Ligatures=TeX]
\newfontfamily\zinBold{Mulish-Bold.ttf}[Path=<<fonts>>, Ligatures=TeX]
\newfontfamily\zinXBold{Mulish-ExtraBold.ttf}[Path=<<fonts>>, Ligatures=TeX]
\newfontfamily\zinBlack{Mulish-Black.ttf}[Path=<<fonts>>, Ligatures=TeX]
\newfontfamily\zinCaps{Mulish-ExtraBold.ttf}[Path=<<fonts>>, Ligatures=TeX, LetterSpace=10]
<<textfont>>
% ---- дрібні елементи: мітки, чипи, маркер
\newcommand{\zinMark}[1]{\tikz[baseline=(m.base)]\node[draw=zinInk, line width=0.38mm, fill=zinSurfaceII, rounded corners=1.1mm,
  minimum width=5.4mm, minimum height=5.4mm, inner sep=0pt, font=\zinBlack\fontsize{9}{10}\selectfont, text=zinInk](m){#1};}
\newcommand{\zinMarkDark}[1]{\tikz[baseline=(m.base)]\node[draw=zinInk, line width=0.38mm, fill=zinInk, rounded corners=1.1mm,
  minimum width=5.4mm, minimum height=5.4mm, inner xsep=1mm, inner ysep=0pt, font=\zinBlack\fontsize{9}{10}\selectfont, text=zinCream](m){#1};}
\newcommand{\zinChip}[1]{\tikz[baseline=(n.base)]\node[draw=zinInk, line width=0.4mm, fill=zinSurface, rounded corners=2mm, inner xsep=2.4mm,
  inner ysep=1.1mm, font=\zinBlack\fontsize{8.5}{10}\selectfont, text=zinInk,
  preaction={fill=zinInk, transform canvas={shift={(0.7mm,-0.7mm)}}}](n){#1};}
\newcommand{\zinPlane}{\tikz[baseline=-0.6ex, scale=0.27]{\fill[zinInk] (0,0) -- (1,0.42) -- (0.33,-0.1) -- cycle;
  \fill[zinInk] (0.33,-0.1) -- (0.42,-0.5) -- (0.55,-0.02) -- cycle;}}
\newcommand{\zinPageNum}{\tikz[baseline=(n.base)]\node[fill=zinInk, text=zinCream, rounded corners=1.6mm, inner xsep=2.4mm,
  inner ysep=1.1mm, font=\zinBlack\fontsize{9}{10}\selectfont](n){\thepage};}
\newcommand{\zinMarker}[1]{\tikz[baseline=(t.base)]{\node[inner sep=0pt](t){#1};\begin{scope}[on background layer]
  \fill[zinMarker] ([xshift=-1.2mm,yshift=-1.3mm]t.base west) rectangle ([xshift=1.2mm,yshift=3.4mm]t.base east);\end{scope}}}
\newcommand{\zinEyebrow}[1]{{\zinCaps\fontsize{8.5}{10}\selectfont\color{zinMuted}#1}}
"""

ВАРІАНТ = r"""
\geometry{left=1.7cm, right=1.7cm, top=2.2cm, bottom=1.8cm, headheight=20pt, headsep=0.5cm, footskip=0.85cm}
% ---- колонтитули
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\fancyhead[L]{\zinEyebrow{<<header>>}}
\fancyhead[R]{\href{https://t.me/pvtr2525}{\zinChip{\zinPlane\hspace{1.3mm}@pvtr2525}}}
\fancyfoot[L]{{\zinXBold\fontsize{8.5}{10}\selectfont\color{zinMuted}\href{https://t.me/pvtr2525}{t.me/pvtr2525}}}
\fancyfoot[C]{\zinPageNum}
\fancyfoot[R]{{\zinXBold\fontsize{8.5}{10}\selectfont\color{zinMuted}НМТ\,·\,математика}}
% ---- водяний знак: поверх карток (під непрозорими картками фоновий не видно), напівпрозорий
\ifdefined\DraftwatermarkOptions \DraftwatermarkOptions{stamp=false}\fi
\ifdefined\nmtnowatermark\else
\makeatletter
\AddToHook{shipout/foreground}{\ifnum\value{page}>1 \put(\strip@pt\dimexpr0.5\paperwidth\relax,-\strip@pt\dimexpr0.5\paperheight\relax){%
  \makebox(0,0){\tikz\node[rotate=52, text=zinInk, text opacity=0.045, inner sep=0pt, font=\zinBlack\fontsize{92}{92}\selectfont]{@pvtr2525};}}\fi}
\makeatother
\fi
% ---- картки
\tcbset{zinplate/.style={enhanced, colback=zinSurface, colframe=zinInk, boxrule=0.5mm, arc=2.4mm, shadow={1.1mm}{-1.1mm}{0mm}{fill=zinInk}}}
% завдання: номер -- пігулка на верхній рамці (лічильник уже збільшено вмістом картки)
\newtcolorbox{zinTask}{zinplate, left=4mm, right=4mm, top=4.8mm, bottom=3.0mm, before skip=4.4mm, after skip=1.2mm,
  before upper={\setlength{\textwidth}{\linewidth}\setlength{\parindent}{0pt}},
  overlay={\node[fill=zinInk, text=zinCream, rounded corners=1.7mm, minimum height=6.4mm, minimum width=9mm, inner xsep=1.8mm,
    font=\zinBlack\fontsize{11.5}{12}\selectfont] at ([xshift=9.5mm]frame.north west) {\thezad};}}
\renewcommand{\zadtask}[1]{\stepcounter{zad}#1\par\nopagebreak\vspace{0.15cm}}
\renewcommand{\zadnum}{\stepcounter{zad}}
% інструкції частин
\newcounter{zinpart}
\renewcommand{\instructionBox}[1]{\stepcounter{zinpart}%
\par\vspace{0.36cm}\noindent
\begin{tcolorbox}[zinplate, colback=zinOrangeTint, nobeforeafter, left=4mm, right=4mm, top=4.1mm, bottom=2.2mm,
  overlay={\node[fill=zinInk, text=zinCream, rounded corners=1.7mm, inner xsep=2.4mm, inner ysep=1.2mm, anchor=west,
    font=\zinCaps\fontsize{8.5}{10}\selectfont] at ([xshift=4mm]frame.north west) {ЧАСТИНА~\arabic{zinpart}};}]
{\zinBold\fontsize{10}{13.5}\selectfont #1}
\end{tcolorbox}\par\nopagebreak\vspace{0.1cm}\nopagebreak}
% ---- варіанти А--Д: картки з літерою-міткою на верхній рамці
\tcbset{zinopt/.style={enhanced, colback=zinSurface, colframe=zinInk, boxrule=0.4mm, arc=1.8mm,
  shadow={0.7mm}{-0.7mm}{0mm}{fill=zinInk}, halign=center, valign=center, left=1mm, right=1mm, top=3.3mm, bottom=1.6mm,
  attach boxed title to top center={yshift=-2.7mm},
  boxed title style={enhanced, colback=zinSurfaceII, colframe=zinInk, boxrule=0.35mm, arc=1.2mm, left=1.4mm, right=1.4mm,
    top=0.4mm, bottom=0.4mm},
  coltitle=zinInk, fonttitle=\zinBlack\fontsize{9}{10}\selectfont}}
\renewcommand{\answerTable}[5]{%
\par\nopagebreak\vspace{0.36cm}\noindent
\begin{tcbraster}[raster columns=5, raster equal height, raster column skip=2.6mm, raster left skip=0mm, raster right skip=0.8mm,
  raster before skip=0mm, raster after skip=0mm, raster every box/.style={zinopt}]
\begin{tcolorbox}[title=А]#1\end{tcolorbox}\begin{tcolorbox}[title=Б]#2\end{tcolorbox}\begin{tcolorbox}[title=В]#3\end{tcolorbox}%
\begin{tcolorbox}[title=Г]#4\end{tcolorbox}\begin{tcolorbox}[title=Д]#5\end{tcolorbox}
\end{tcbraster}\par}
\renewcommand{\answerTableTall}[5]{\answerTable{#1}{#2}{#3}{#4}{#5}}
\providecommand{\answerTableSmall}{}\renewcommand{\answerTableSmall}[5]{\answerTable{#1}{#2}{#3}{#4}{#5}}
\newcommand{\zinRow}[2]{\par\noindent\makebox[2.3em][l]{\zinMark{#1}}\parbox[t]{\dimexpr\linewidth-2.3em\relax}{\raggedright #2}\par\vspace{0.24cm}}
\providecommand{\answerListVertical}{}\renewcommand{\answerListVertical}[5]{\par\nopagebreak\vspace{0.25cm}%
\zinRow{А}{#1}\zinRow{Б}{#2}\zinRow{В}{#3}\zinRow{Г}{#4}\zinRow{Д}{#5}}
% ---- відповідність: пункти 1--3 -- темні мітки, варіанти А--Д -- світлі; сітка із заокруглених клітинок
\setlength{\nmtMatchLab}{2.2em}
\setlength{\nmtMatchSep}{0.22cm}
\renewcommand{\matchHead}[1]{\par\noindent{\zinCaps\fontsize{7.5}{9}\selectfont\color{zinMuted}\MakeUppercase{#1}}\par\nopagebreak\vspace{0.26cm}}
\renewcommand{\matchItem}[2]{\par\noindent\makebox[\nmtMatchLab][l]{\ifnum`#1<256 \zinMarkDark{#1}\else\zinMark{#1}\fi}%
\parbox[t]{\dimexpr\linewidth-\nmtMatchLab\relax}{\raggedright #2}\par\nopagebreak\vspace{\nmtMatchSep}}
\renewcommand{\matchingGridRaw}{%
\begin{tikzpicture}[x=6mm, y=6mm, baseline=(current bounding box.north)]
\foreach \L [count=\i] in {А,Б,В,Г,Д} \node[font=\zinBlack\fontsize{8}{9}\selectfont, text=zinInk] at (\i,-0.3) {\L};
\foreach \r in {1,2,3} {
  \node[font=\zinBlack\fontsize{8}{9}\selectfont, text=zinInk] at (0.25,-\r-0.32) {\r};
  \foreach \i in {1,...,5} \draw[draw=zinInk, line width=0.35mm, fill=zinSurface, rounded corners=0.9mm]
    (\i-0.38,-\r-0.7) rectangle (\i+0.38,-\r+0.06);}
\end{tikzpicture}}
\providecommand{\matchingLayout}{}\renewcommand{\matchingLayout}[3]{%
    \noindent
    \begin{minipage}[t]{0.37\textwidth}\vspace{0pt}\raggedright #1\end{minipage}%
    \hfill
    \begin{minipage}[t]{0.40\textwidth}\vspace{0pt}\raggedright #2\end{minipage}%
    \hfill
    \begin{minipage}[t]{0.2\textwidth}\vspace{0pt}\begin{flushright}#3\end{flushright}\end{minipage}}
% ---- поле короткої відповіді: 5 клітинок, кома, 3 клітинки
\newcommand{\zinCells}[1]{\tikz[baseline=-1.3mm]{\foreach \i in {1,...,#1} \draw[draw=zinInk, line width=0.4mm, fill=zinSurface,
  rounded corners=1.1mm] ({(\i-1)*8.4mm},-4.3mm) rectangle ++(7.6mm,8.4mm);}}
\renewcommand{\nmtAnswerBox}{%
\par\nopagebreak\vspace{0.26cm}\noindent
\tikz[baseline=(n.base)]\node[fill=zinSageTint, draw=zinInk, line width=0.4mm, rounded corners=1.8mm, inner xsep=2.4mm, inner ysep=1.3mm,
  font=\zinCaps\fontsize{8.5}{10}\selectfont, text=zinSageInk](n){ВІДПОВІДЬ};%
\hspace{3.2mm}\zinCells{5}\hspace{1.1mm}{\zinBlack\fontsize{16}{16}\selectfont ,}\hspace{1.1mm}\zinCells{3}\par}
% ---- чернетка: клітинки на решту останньої сторінки варіанта (якщо лишилося понад 5 см)
\newcommand{\zinScratch}{\par\vspace{0.45cm}%
\ifdim\dimexpr\pagegoal-\pagetotal\relax>5cm
\noindent\begin{tcolorbox}[zinplate, height fill, nobeforeafter,
  underlay={\begin{scope}\clip[rounded corners=2mm] (interior.south west) rectangle (interior.north east);
    \draw[zinInk!9, step=5mm, line width=0.3pt] (interior.south west) grid (interior.north east);\end{scope}},
  overlay={\node[fill=zinInk, text=zinCream, rounded corners=1.7mm, inner xsep=2.4mm, inner ysep=1.2mm, anchor=west,
    font=\zinCaps\fontsize{8.5}{10}\selectfont] at ([xshift=4mm]frame.north west) {ЧЕРНЕТКА};}]
\end{tcolorbox}
\fi}
% ---- заголовок документа
\newcommand{\zinTitle}[3]{%
\par\noindent\zinEyebrow{#1}\par\vspace{0.12cm}
\noindent{\zinBlack\fontsize{30}{36}\selectfont #2}\par\vspace{0.3cm}
\noindent #3\par\vspace{0.15cm}}
% ===================== кінець теми «зін» =====================
"""

ПРЕАМБУЛА = ОСНОВА + ВАРІАНТ

ТЕКСТ = {
    "mulish": r"""\setmainfont{Mulish-SemiBold.ttf}[Path=<<fonts>>, Ligatures=TeX, Scale=0.93, BoldFont=Mulish-ExtraBold.ttf,
  ItalicFont=Mulish-SemiBold.ttf, ItalicFeatures={FakeSlant=0.16}, BoldItalicFont=Mulish-ExtraBold.ttf, BoldItalicFeatures={FakeSlant=0.16}]
\linespread{1.05}""",
    "schoolbook": "% текст -- Schoolbook (як у базі)",
}


def основа(текст="mulish"):
    """кольори, шрифти й дрібні елементи теми (для інших сторінок у тому ж стилі: довідкові тощо); потребує fontspec, tikz,
    tcolorbox і mathastext, завантаженого зі Schoolbook ДО цього блоку (тоді формули лишаються Schoolbook)"""
    return ОСНОВА.replace("<<textfont>>", ТЕКСТ[текст]).replace("<<fonts>>", ШРИФТИ)


def застосувати(tex, назва, eyebrow, шапка, заголовок=None, чипи=("22 завдання", "32 бали", "відповіді~-- наприкінці"), текст="mulish"):
    """tex від пробний.документ(): тема в преамбулу, завдання (samepage) -> картки, заголовок -> \\zinTitle"""
    тема = (ПРЕАМБУЛА.replace("<<textfont>>", ТЕКСТ[текст]).replace("<<fonts>>", ШРИФТИ).replace("<<header>>", шапка))
    assert tex.count("\\begin{document}") == 1
    tex = tex.replace("\\begin{document}", тема + "\\begin{document}", 1)
    n = tex.count("\\begin{samepage}\n")
    tex = tex.replace("\\begin{samepage}\n", "\\begin{zinTask}\n").replace("\n\\end{samepage}\n", "\n\\end{zinTask}\n")
    assert n == 22 and tex.count("\\end{zinTask}") == 22, n
    старий = "\\chapterTitle{%s}\n" % назва
    assert старий in tex
    чип = "\\hspace{2.6mm}".join("\\zinChip{%s}" % c for c in чипи)
    return tex.replace(старий, "\\zinTitle{%s}{%s}{%s}\n" % (eyebrow, заголовок or назва, чип), 1)


def сторінка_відповідей(завдання):
    """картки «правильно» (шавлія): 1--15 сіткою 5 x 3, 16--18 парами, 19--22 числами; поле «Мій результат»"""
    в = {z["номер"]: z["відповідь"] for z in завдання}
    кор = lambda n: re.sub(r"[.,]", "{,}", str(в[n]))
    def картки(стовпців, вміст):
        return ("\\begin{tcbraster}[raster columns=%d, raster equal height, raster column skip=2.6mm, raster row skip=2.6mm, "
                "raster left skip=0mm, raster right skip=1.1mm, raster every box/.style={zinans}]\n%s\n\\end{tcbraster}\n"
                % (стовпців, "\n".join("\\begin{tcolorbox}%s\\end{tcolorbox}" % x for x in вміст)))
    одна = ["\\zinMarkDark{%d}\\hspace{2.4mm}{\\zinBlack\\fontsize{15}{15}\\selectfont %s}" % (n, в[n]) for n in range(1, 16)]
    відп = ["\\zinMarkDark{%d}\\hspace{2.6mm}{\\zinBlack\\fontsize{12}{14}\\selectfont %s}"
            % (n, "\\hspace{2.4mm}".join("%d\\,--\\,%s" % (i + 1, x) for i, x in enumerate(в[n]))) for n in (16, 17, 18)]
    числа = ["\\zinMarkDark{%d}\\hspace{2.6mm}{\\fontsize{15}{15}\\selectfont $\\mathbf{%s}$}" % (n, кор(n)) for n in (19, 20, 21, 22)]
    розділ = lambda t: "\\par\\vspace{0.45cm}\\noindent\\zinEyebrow{%s}\\par\\vspace{0.25cm}\n" % t
    return ("\\zinScratch\n\\clearpage\n"
            "\\tcbset{zinans/.style={zinplate, colback=zinSageTint, boxrule=0.45mm, arc=2mm, shadow={0.8mm}{-0.8mm}{0mm}{fill=zinInk}, "
            "left=2.6mm, right=2mm, top=2.2mm, bottom=2.2mm, valign=center}}\n"
            "\\zinTitle{ПЕРЕВІР СЕБЕ}{\\zinMarker{Відповіді}}{\\zinChip{1--15: по 1 балу}\\hspace{2.6mm}\\zinChip{16--18: до 3 балів}"
            "\\hspace{2.6mm}\\zinChip{19--22: по 2 бали}}\n"
            + розділ("Завдання 1--15 · одна правильна відповідь") + картки(5, одна)
            + розділ("Завдання 16--18 · відповідність") + картки(3, відп)
            + розділ("Завдання 19--22 · коротка відповідь") + картки(4, числа)
            + "\\par\\vspace{0.75cm}\\noindent\n"
              "\\begin{tcolorbox}[zinplate, left=4.4mm, right=4.4mm, top=3.6mm, bottom=3.6mm, nobeforeafter]\n"
              "{\\zinBlack\\fontsize{15}{18}\\selectfont Мій результат}\\hfill"
              "\\tikz[baseline=-1.3mm]\\draw[draw=zinInk, line width=0.4mm, fill=zinSurface, rounded corners=1.2mm] (0,-4.3mm) rectangle (2.2cm,4.6mm);"
              "\\ {\\zinBlack\\fontsize{13}{15}\\selectfont / 32 бали}\\hspace{9mm}"
              "{\\zinBold\\fontsize{11}{13}\\selectfont час}\\ "
              "\\tikz[baseline=-1.3mm]\\draw[draw=zinInk, line width=0.4mm, fill=zinSurface, rounded corners=1.2mm] (0,-4.3mm) rectangle (1.8cm,4.6mm);"
              "\\ {\\zinBold\\fontsize{11}{13}\\selectfont хв}\n"
              "\\end{tcolorbox}\\par\n"
              "\\vspace{0.4cm}\\noindent{\\zinSemi\\fontsize{10}{14}\\selectfont\\color{zinInkII}Звір відповіді лише після того, як розв'яжеш увесь "
              "варіант. Завдання з помилками розв'яжи ще раз.}\\par\n")
