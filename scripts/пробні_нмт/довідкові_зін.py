# -*- coding: utf-8 -*-
"""Довідкові матеріали НМТ з математики (той самий зміст, що в офіційних: таблиця квадратів, алгебра й початки аналізу,
тригонометрія, геометрія) -- три сторінки A4 у темі «зін» (scripts/пробні_нмт/тема_зін.py): картки з вкладками, мітки,
Mulish для тексту, Schoolbook для формул, рисунки -- TikZ.

    python3 scripts/пробні_нмт/довідкові_зін.py ВИХІД.pdf

Готовий PDF передається збирачу: оформлення_канал.py ... --довідкові ВИХІД.pdf
"""
import os, sys, shutil, tempfile, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import тема_зін as Т                       # noqa: E402

ПРЕАМБУЛА = r"""\documentclass[11pt]{article}
\usepackage[ukrainian,shorthands=off]{babel}
\usepackage{fontspec}
\setmainfont{Schoolbook-Regular.otf}[Path=<<fonts>>, BoldFont=Schoolbook-Bold.otf, ItalicFont=Schoolbook-Italic.otf,
  BoldItalicFont=Schoolbook-BoldItalic.otf]
\usepackage[italic]{mathastext}
\usepackage[a4paper, left=1.5cm, right=1.5cm, top=1.95cm, bottom=1.5cm, headheight=20pt, headsep=0.4cm, footskip=0.75cm]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{tikz}
\usetikzlibrary{calc,angles,arrows.meta}
\usepackage{xcolor,array,colortbl,fancyhdr}
\usepackage{tcolorbox}
\tcbuselibrary{skins}
\usepackage[hidelinks]{hyperref}
<<base>>
% \tg, \ctg -- з babel (ukrainian)
\setlength{\parindent}{0pt}
\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\fancyhead[L]{\zinEyebrow{ДОВІДКОВІ МАТЕРІАЛИ}}
\fancyhead[R]{\href{https://t.me/pvtr2525}{\zinChip{\zinPlane\hspace{1.3mm}@pvtr2525}}}
\fancyfoot[L]{{\zinXBold\fontsize{8.5}{10}\selectfont\color{zinMuted}\href{https://t.me/pvtr2525}{t.me/pvtr2525}}}
\fancyfoot[R]{{\zinXBold\fontsize{8.5}{10}\selectfont\color{zinMuted}НМТ\,·\,математика}}
% ---- картка з вкладкою (широкі) і картка із заголовком усередині (вузькі: чотирикутники, тіла)
\tcbset{zref/.style={enhanced, colback=zinSurface, colframe=zinInk, boxrule=0.45mm, arc=2.2mm, shadow={0.9mm}{-0.9mm}{0mm}{fill=zinInk},
  left=3mm, right=3mm, top=4.3mm, bottom=2.3mm, before skip=0pt, after skip=0pt,
  fontupper=\fontsize{10}{14}\selectfont, before upper={\setlength{\parskip}{1.9mm}\setlength{\parindent}{0pt}\raggedright\zfix}}}
\newtcolorbox{zcard}[2][]{zref, #1, overlay={\node[fill=zinInk, text=zinCream, rounded corners=1.5mm, inner xsep=2.2mm,
  inner ysep=1mm, anchor=west, font=\zinCaps\fontsize{7.5}{9}\selectfont] at ([xshift=3mm]frame.north west) {#2};}}
\newtcolorbox{zmini}[2][]{zref, top=2.4mm, left=2mm, right=2mm, halign=center, #1,
  before upper={\setlength{\parskip}{1.1mm}\setlength{\parindent}{0pt}\zfix{\zinBlack\fontsize{9.5}{11}\selectfont #2\par}\vspace{0.6mm}}}
% індекси «осн», «б» -- шрифтом формул (у Mulish «б» схоже на 6)
\newfontfamily\zinSB{Schoolbook-Regular.otf}[Path=<<fonts>>]
\newcommand{\zsub}[1]{\text{\zinSB #1}}
% у картках: пробіли біля «=» не розтягуються, слова не переносяться
\newcommand{\zfix}{\thickmuskip=5mu\relax\medmuskip=4mu\relax\hyphenpenalty=10000\exhyphenpenalty=10000\relax}
\newcommand{\zsec}[1]{\par\vspace{3.6mm}\noindent{\zinBlack\fontsize{14}{17}\selectfont\zinMarker{#1}}\par\vspace{2.6mm}}
\newcommand{\zgroup}[1]{\par\vspace{3.4mm}\noindent\zinEyebrow{#1}\par\vspace{2.2mm}}
\newcommand{\zgap}{\par\vspace{3.4mm}}
\newcommand{\zth}[1]{{\zinXBold\fontsize{8.5}{10.5}\selectfont #1}}
\newcommand{\zt}{\fontsize{9.5}{11}\selectfont}
\tikzset{zfig/.style={line cap=round, line join=round, line width=0.75pt, draw=zinInk, font=\fontsize{9.5}{11}\selectfont},
  zhid/.style={dashed, line width=0.55pt, dash pattern=on 2.2pt off 1.6pt}}
\begin{document}
"""

СТОР_1 = r"""
\noindent\zinEyebrow{НМТ · МАТЕМАТИКА}\par\vspace{0.6mm}
\noindent{\zinBlack\fontsize{26}{31}\selectfont Довідкові \zinMarker{матеріали}}\par\vspace{4.2mm}

\begin{zcard}{ТАБЛИЦЯ КВАДРАТІВ ВІД 10 ДО 49}
\centering\renewcommand{\arraystretch}{1.32}\setlength{\tabcolsep}{0pt}\arrayrulecolor{zinInk!16}
\begin{tabular}{>{\centering\arraybackslash}m{2.3cm}*{10}{>{\centering\arraybackslash}m{1.42cm}}}
 & \multicolumn{10}{c}{\zth{Одиниці}}\\
\zth{Десятки} & <<units>>\\[1.2mm]
<<rows>>
\end{tabular}
\end{zcard}

\zsec{Алгебра і початки аналізу}

\noindent\begin{minipage}[t]{0.47\linewidth}\vspace{0pt}
\begin{zcard}[equal height group=a1]{ФОРМУЛИ СКОРОЧЕНОГО МНОЖЕННЯ}
$a^2-b^2=(a-b)(a+b)$

$(a+b)^2=a^2+2ab+b^2$

$(a-b)^2=a^2-2ab+b^2$
\end{zcard}
\end{minipage}\hfill
\begin{minipage}[t]{0.495\linewidth}\vspace{0pt}
\begin{zcard}[equal height group=a1]{МОДУЛЬ ЧИСЛА}
\vspace{1mm}$|a|=\begin{cases}a, & \text{якщо } a\geqslant 0,\\ -a, & \text{якщо } a<0\end{cases}$
\end{zcard}
\end{minipage}
\zgap
\begin{zcard}{КВАДРАТНЕ РІВНЯННЯ}
\begin{minipage}[t]{0.42\linewidth}
$ax^2+bx+c=0,\ \ a\neq 0$

$D=b^2-4ac$ -- дискримінант

$ax^2+bx+c=a(x-x_1)(x-x_2)$
\end{minipage}\hfill
\begin{minipage}[t]{0.56\linewidth}
$x_1=\dfrac{-b-\sqrt{D}}{2a},\ \ x_2=\dfrac{-b+\sqrt{D}}{2a}$, якщо $D>0$

\vspace{1.2mm}$x_1=x_2=\dfrac{-b}{2a}$, якщо $D=0$
\end{minipage}
\end{zcard}
\zgap
\noindent\begin{minipage}[t]{0.555\linewidth}\vspace{0pt}
\begin{zcard}[equal height group=a2]{СТЕПЕНІ}
$a^1=a,\ \ a^n=\underbrace{a\cdot a\cdot\ldots\cdot a}_{n\text{ разів}}$ для $a\in R,\ n\in N,\ n\geqslant 2$

$a^0=1$, де $a\neq 0$\qquad $\sqrt{a^2}=|a|$

$a^{-n}=\dfrac{1}{a^n}$ для $a\neq 0,\ n\in N$

$a^{\frac{m}{n}}=\sqrt[n]{a^m},\ \ a>0,\ m\in Z,\ n\in N,\ n\geqslant 2$

$a^x\cdot a^y=a^{x+y}$\qquad $\dfrac{a^x}{a^y}=a^{x-y}$\qquad $(a^x)^y=a^{x\cdot y}$

$(ab)^x=a^x\cdot b^x$\qquad $\left(\dfrac{a}{b}\right)^{x}=\dfrac{a^x}{b^x}$
\end{zcard}
\end{minipage}\hfill
\begin{minipage}[t]{0.41\linewidth}\vspace{0pt}
\begin{zcard}[equal height group=a2]{ЛОГАРИФМИ}
$a>0,\ a\neq 1,\ b>0,\ c>0,\ k\neq 0$

$a^{\log_a b}=b$\qquad $\log_a a=1$\qquad $\log_a 1=0$

$\log_a(b\cdot c)=\log_a b+\log_a c$

$\log_a\dfrac{b}{c}=\log_a b-\log_a c$

$\log_a b^n=n\cdot\log_a b$

$\log_{a^k} b=\dfrac{1}{k}\cdot\log_a b$
\end{zcard}
\end{minipage}
\zgap
\noindent\begin{minipage}[t]{0.47\linewidth}\vspace{0pt}
\begin{zcard}[equal height group=a3]{АРИФМЕТИЧНА ПРОГРЕСІЯ}
$a_n=a_1+d(n-1)$\qquad $S_n=\dfrac{a_1+a_n}{2}\cdot n$
\end{zcard}
\end{minipage}\hfill
\begin{minipage}[t]{0.495\linewidth}\vspace{0pt}
\begin{zcard}[equal height group=a3]{ГЕОМЕТРИЧНА ПРОГРЕСІЯ}
$b_n=b_1\cdot q^{n-1}$\qquad $S_n=\dfrac{b_1(q^n-1)}{q-1},\ \ (q\neq 1)$
\end{zcard}
\end{minipage}
\zgap
\noindent\begin{minipage}[t]{0.3\linewidth}\vspace{0pt}
\begin{zcard}[equal height group=a4]{ТЕОРІЯ ЙМОВІРНОСТЕЙ}
$P(A)=\dfrac{k}{n}$
\end{zcard}
\end{minipage}\hfill
\begin{minipage}[t]{0.665\linewidth}\vspace{0pt}
\begin{zcard}[equal height group=a4]{КОМБІНАТОРИКА}
$P_n=1\cdot 2\cdot 3\cdot\ldots\cdot n=n!$\qquad $C_n^k=\dfrac{n!}{k!\cdot(n-k)!}$\qquad $A_n^k=\dfrac{n!}{(n-k)!}$
\end{zcard}
\end{minipage}
\newpage
"""

СТОР_2 = r"""
\noindent\begin{minipage}[t]{0.43\linewidth}\vspace{0pt}
\begin{zcard}[equal height group=b1]{ПОХІДНА ФУНКЦІЇ}
$C$, $\alpha$ -- сталі

$(C)'=0$

\begin{tabular}{@{}p{0.47\linewidth}@{}p{0.5\linewidth}@{}}
$x'=1$ & $(x^\alpha)'=\alpha x^{\alpha-1}$\\[1.8mm]
$(\sqrt{x})'=\dfrac{1}{2\sqrt{x}}$ & $(e^x)'=e^x$\\[2.4mm]
$(\ln x)'=\dfrac{1}{x}$ & $(\sin x)'=\cos x$\\[2.4mm]
$(\cos x)'=-\sin x$ & $(\tg x)'=\dfrac{1}{\cos^2 x}$\\[2.4mm]
$(u+v)'=u'+v'$ & $(u-v)'=u'-v'$\\[1.8mm]
$(uv)'=u'v+uv'$ & $(Cu)'=Cu'$\\[1.8mm]
$\left(\dfrac{u}{v}\right)'=\dfrac{u'v-uv'}{v^2}$ &
\end{tabular}
\end{zcard}
\end{minipage}\hfill
\begin{minipage}[t]{0.535\linewidth}\vspace{0pt}
\begin{zcard}[equal height group=b1]{ПЕРВІСНА ФУНКЦІЇ ТА ВИЗНАЧЕНИЙ ІНТЕГРАЛ}
\centering\renewcommand{\arraystretch}{1.08}\arrayrulecolor{zinInk!16}
\setlength{\tabcolsep}{4pt}
\begin{tabular}{@{}>{\centering\arraybackslash}m{0.33\linewidth}|>{\centering\arraybackslash}m{0.6\linewidth}@{}}
\zth{Функція $f(x)$} & \zth{Загальний вигляд первісних $F(x)+C$, $C$ -- довільна стала}\\[1mm]\hline
$0$ & $C$\\\hline
$1$ & $x+C$\\\hline
\rule{0pt}{6mm}$x^\alpha,\ \alpha\neq -1$ & $\dfrac{x^{\alpha+1}}{\alpha+1}+C$\\[2.2mm]\hline
\rule{0pt}{5.8mm}$\dfrac{1}{x}$ & $\ln|x|+C$\\[2.2mm]\hline
$e^x$ & $e^x+C$\\\hline
$\sin x$ & $-\cos x+C$\\\hline
$\cos x$ & $\sin x+C$\\\hline
\rule{0pt}{5.8mm}$\dfrac{1}{\cos^2 x}$ & $\tg x+C$\\[2.2mm]
\end{tabular}

\vspace{1.6mm}\raggedright
$\displaystyle\int\limits_a^b f(x)\,dx=F(x)\Big|_a^b=F(b)-F(a)$\par
-- формула Ньютона-Лейбніца
\end{zcard}
\end{minipage}

\zgap
\begin{zcard}{ТРИГОНОМЕТРІЯ}
\begin{minipage}[c]{0.66\linewidth}
\renewcommand{\arraystretch}{1.95}
\begin{tabular}{@{}p{0.47\linewidth}@{}p{0.53\linewidth}@{}}
$\sin\alpha=y_\alpha$\qquad $\cos\alpha=x_\alpha$ & $\sin^2\alpha+\cos^2\alpha=1$\\
$\tg\alpha=\dfrac{\sin\alpha}{\cos\alpha}$ & $1+\tg^2\alpha=\dfrac{1}{\cos^2\alpha}$\\
$\sin 2\alpha=2\sin\alpha\cos\alpha$ & $\cos 2\alpha=\cos^2\alpha-\sin^2\alpha$\\
$\sin(90^\circ+\alpha)=\cos\alpha$ & $\sin(180^\circ-\alpha)=\sin\alpha$\\
$\cos(90^\circ+\alpha)=-\sin\alpha$ & $\cos(180^\circ-\alpha)=-\cos\alpha$\\
$\tg(90^\circ+\alpha)=-\dfrac{1}{\tg\alpha}$ & $\tg(180^\circ-\alpha)=-\tg\alpha$\\
\end{tabular}
\end{minipage}\hfill
\begin{minipage}[c]{0.32\linewidth}\centering
\begin{tikzpicture}[zfig, x=1.62cm, y=1.62cm]
\coordinate (O) at (0,0); \coordinate (M) at (125:1);
\draw[fill=zinSageTint, line width=0.8pt] (O) circle (1);
\draw[line width=0.55pt, -{Stealth[length=2mm]}] (-1.3,0) -- (1.32,0);
\draw[line width=0.55pt, -{Stealth[length=2mm]}] (0,-1.22) -- (0,1.3);
\node[below] at (1.25,0) {$x$}; \node[left] at (0,1.24) {$y$};
\draw[zhid] (M) -- (M |- O); \draw[zhid] (M) -- (O |- M);
\draw[line width=0.8pt] (O) -- (M);
\fill[zinInk] (M) circle (1.3pt);
\draw[line width=0.5pt, -{Stealth[length=1.6mm]}] (0.27,0) arc (0:125:0.27);
\node at (62:0.44) {$\alpha$};
\node[above left=-1pt] at (M) {$M(x_\alpha,\,y_\alpha)$};
\node[below=1pt] at (M |- O) {$x_\alpha$};
\node[right=1pt] at (O |- M) {$y_\alpha$};
\node[below left=0pt] at (O) {$0$};
\node[below left=-1pt] at (-1,0) {$-1$}; \node[below right=-1pt] at (1,0) {$1$};
\node[above left=-1pt] at (0,1) {$1$}; \node[below left=-1pt] at (0,-1) {$-1$};
\end{tikzpicture}
\end{minipage}
\end{zcard}
\zgap
\begin{zcard}{ТАБЛИЦЯ ЗНАЧЕНЬ ТРИГОНОМЕТРИЧНИХ ФУНКЦІЙ ДЕЯКИХ КУТІВ}
\centering\renewcommand{\arraystretch}{1.25}\setlength{\tabcolsep}{0pt}\arrayrulecolor{zinInk!16}
\begin{tabular}{>{\centering\arraybackslash}m{1.15cm}>{\centering\arraybackslash}m{1.25cm}|*{8}{>{\centering\arraybackslash}m{1.7cm}}}
\multirow{2}{*}{$\alpha$} & \zth{рад} & $0$ & $\dfrac{\pi}{6}$ & $\dfrac{\pi}{4}$ & $\dfrac{\pi}{3}$ & $\dfrac{\pi}{2}$ & $\pi$ & $\dfrac{3\pi}{2}$ & $2\pi$\\[1.4mm]
 & \zth{град} & $0^\circ$ & $30^\circ$ & $45^\circ$ & $60^\circ$ & $90^\circ$ & $180^\circ$ & $270^\circ$ & $360^\circ$\\\hline
\multicolumn{2}{c|}{\rule{0pt}{6.2mm}$\sin\alpha$} & $0$ & $\dfrac{1}{2}$ & $\dfrac{\sqrt2}{2}$ & $\dfrac{\sqrt3}{2}$ & $1$ & $0$ & $-1$ & $0$\\[1.8mm]\hline
\multicolumn{2}{c|}{\rule{0pt}{6.2mm}$\cos\alpha$} & $1$ & $\dfrac{\sqrt3}{2}$ & $\dfrac{\sqrt2}{2}$ & $\dfrac{1}{2}$ & $0$ & $-1$ & $0$ & $1$\\[1.8mm]\hline
\multicolumn{2}{c|}{\rule{0pt}{6.2mm}$\tg\alpha$} & $0$ & $\dfrac{1}{\sqrt3}$ & $1$ & $\sqrt3$ & {\zt не існує} & $0$ & {\zt не існує} & $0$\\[1.8mm]
\end{tabular}
\end{zcard}
\newpage
"""

СТОР_3 = r"""
\noindent{\zinBlack\fontsize{14}{17}\selectfont\zinMarker{Геометрія}}\par\vspace{2.6mm}

\noindent\begin{minipage}[t]{0.64\linewidth}\vspace{0pt}
\begin{zcard}[equal height group=g1]{ДОВІЛЬНИЙ ТРИКУТНИК}
\begin{minipage}[c]{0.4\linewidth}\centering
\begin{tikzpicture}[zfig, scale=0.95]
\coordinate (A) at (0,0); \coordinate (B) at (3.0,0); \coordinate (C) at (2.15,2.35);
\coordinate (H) at ($(B)!(A)!(C)$);
\draw[fill=zinSageTint] (A) -- (B) -- (C) -- cycle;
\draw[line width=0.6pt] (A) -- (H);
\pic[draw, line width=0.5pt, angle radius=2mm] {right angle = A--H--C};
\pic[draw, line width=0.5pt, angle radius=4mm] {angle = B--A--C};
\pic[draw, line width=0.5pt, angle radius=3.4mm] {angle = C--B--A};
\pic[draw, line width=0.5pt, angle radius=4mm] {angle = C--B--A};
\pic[draw, line width=0.5pt, angle radius=3.4mm] {angle = A--C--B};
\pic[draw, line width=0.5pt, angle radius=4mm] {angle = A--C--B};
\pic[draw, line width=0.5pt, angle radius=4.6mm] {angle = A--C--B};
\node[left] at (A) {$A$}; \node[right] at (B) {$B$}; \node[above] at (C) {$C$};
\node[above left=-1pt] at ($(A)!0.5!(C)$) {$b$};
\node[right] at ($(B)!0.45!(C)$) {$a$};
\node[below] at ($(A)!0.5!(B)$) {$c$};
\node[above=1pt] at ($(A)!0.5!(H)$) {$h_a$};
\node at ($(A)+(15:0.6)$) {$\alpha$};
\node at ($(B)+(150:0.62)$) {$\beta$};
\node at ($(C)+(-95:0.75)$) {$\gamma$};
\end{tikzpicture}
\end{minipage}\hfill
\begin{minipage}[c]{0.58\linewidth}\setlength{\parskip}{2.3mm}\raggedright
$p=\dfrac{a+b+c}{2}$\qquad $\alpha+\beta+\gamma=180^\circ$

$a^2=b^2+c^2-2bc\cos\alpha$

$\dfrac{a}{\sin\alpha}=\dfrac{b}{\sin\beta}=\dfrac{c}{\sin\gamma}=2R$

{\zt $R$ -- радіус кола, описаного навколо трикутника $ABC$}
\end{minipage}

\vspace{1.6mm}
$S=\dfrac{1}{2}a\cdot h_a$\qquad $S=\dfrac{1}{2}b\cdot c\cdot\sin\alpha$\qquad $S=\sqrt{p(p-a)(p-b)(p-c)}$
\end{zcard}
\end{minipage}\hfill
\begin{minipage}[t]{0.33\linewidth}\vspace{0pt}
\begin{zcard}[equal height group=g1]{ПРЯМОКУТНИЙ ТРИКУТНИК}
$a^2+b^2=c^2$ {\zt (теорема Піфагора)}

$\dfrac{b}{c}=\cos\alpha$\qquad $\dfrac{a}{c}=\sin\alpha$

$\dfrac{a}{b}=\tg\alpha$

\vspace{1mm}\centering
\begin{tikzpicture}[zfig, scale=0.95]
\coordinate (P) at (0,0); \coordinate (Q) at (3.1,0); \coordinate (R) at (0,1.75);
\draw[fill=zinSageTint] (P) -- (Q) -- (R) -- cycle;
\pic[draw, line width=0.5pt, angle radius=2.2mm] {right angle = Q--P--R};
\pic[draw, line width=0.5pt, angle radius=5mm] {angle = R--Q--P};
\node at ($(Q)+(171:0.8)$) {$\alpha$};
\node[left] at ($(P)!0.5!(R)$) {$a$};
\node[below] at ($(P)!0.5!(Q)$) {$b$};
\node[above right=-1pt] at ($(Q)!0.5!(R)$) {$c$};
\end{tikzpicture}
\end{zcard}
\end{minipage}

\zgap
\noindent\begin{minipage}[t]{0.235\linewidth}\vspace{0pt}
\begin{zmini}[equal height group=g2]{Паралелограм}
\begin{tikzpicture}[zfig, scale=0.84]
\coordinate (A) at (0,0); \coordinate (B) at (2.3,0); \coordinate (C) at (3.2,1.5); \coordinate (D) at (0.9,1.5);
\coordinate (F) at (0.9,0);
\draw[fill=zinSageTint] (A) -- (B) -- (C) -- (D) -- cycle;
\draw[line width=0.6pt] (D) -- (F);
\pic[draw, line width=0.5pt, angle radius=2mm] {right angle = D--F--B};
\pic[draw, line width=0.5pt, angle radius=3.6mm] {angle = B--A--D};
\node at ($(A)+(28:0.58)$) {$\gamma$};
\node[above left=-1pt] at ($(A)!0.5!(D)$) {$b$};
\node[right] at ($(D)!0.45!(F)$) {$h_a$};
\node[below] at ($(A)!0.5!(B)$) {$a$};
\end{tikzpicture}

$S=ab\sin\gamma$

$S=ah_a$
\end{zmini}
\end{minipage}\hfill
\begin{minipage}[t]{0.235\linewidth}\vspace{0pt}
\begin{zmini}[equal height group=g2]{Прямокутник}
\begin{tikzpicture}[zfig, scale=0.84]
\draw[fill=zinSageTint] (0,0) rectangle (2.2,1.5);
\node[left] at (0,0.75) {$b$}; \node[below] at (1.1,0) {$a$};
\end{tikzpicture}

$S=ab$
\end{zmini}
\end{minipage}\hfill
\begin{minipage}[t]{0.235\linewidth}\vspace{0pt}
\begin{zmini}[equal height group=g2]{Ромб}
\begin{tikzpicture}[zfig, scale=0.84]
\draw[fill=zinSageTint] (-1.35,0) -- (0,0.85) -- (1.35,0) -- (0,-0.85) -- cycle;
\draw[line width=0.6pt] (-1.35,0) -- (1.35,0); \draw[line width=0.6pt] (0,0.85) -- (0,-0.85);
\node at (-0.42,0.25) {$d_1$}; \node at (0.42,-0.25) {$d_2$};
\end{tikzpicture}

$S=\dfrac{1}{2}d_1d_2$,

{\zt $d_1$, $d_2$ -- діагоналі ромба}
\end{zmini}
\end{minipage}\hfill
\begin{minipage}[t]{0.235\linewidth}\vspace{0pt}
\begin{zmini}[equal height group=g2]{Трапеція}
\begin{tikzpicture}[zfig, scale=0.84]
\coordinate (A) at (0,0); \coordinate (B) at (2.6,0); \coordinate (C) at (2.05,1.45); \coordinate (D) at (0.42,1.45);
\coordinate (F) at (0.42,0);
\draw[fill=zinSageTint] (A) -- (B) -- (C) -- (D) -- cycle;
\draw[line width=0.6pt] (D) -- (F);
\pic[draw, line width=0.5pt, angle radius=2mm] {right angle = D--F--B};
\node[above] at ($(D)!0.5!(C)$) {$b$}; \node[below] at ($(A)!0.5!(B)$) {$a$};
\node[right] at ($(D)!0.45!(F)$) {$h$};
\end{tikzpicture}

$S=\dfrac{a+b}{2}\cdot h$,

{\zt $a$ і $b$ -- основи трапеції}
\end{zmini}
\end{minipage}

\zgap
\noindent\begin{minipage}[t]{0.49\linewidth}\vspace{0pt}
\begin{zcard}[equal height group=g3]{КОЛО}
\begin{minipage}[c]{0.36\linewidth}\centering
\begin{tikzpicture}[zfig]
\draw (0,0) circle (0.95);
\fill[zinInk] (0,0) circle (1.3pt);
\draw[line width=0.6pt] (0,0) -- (-58:0.95);
\node[above=1pt, font=\fontsize{8.5}{10}\selectfont] at (0,0) {$M(x_0,\,y_0)$};
\node at (-118:0.46) {$R$};
\end{tikzpicture}
\end{minipage}\hfill
\begin{minipage}[c]{0.6\linewidth}
$L=2\pi R$

$(x-x_0)^2+(y-y_0)^2=R^2$
\end{minipage}
\end{zcard}
\end{minipage}\hfill
\begin{minipage}[t]{0.49\linewidth}\vspace{0pt}
\begin{zcard}[equal height group=g3]{КРУГ}
\begin{minipage}[c]{0.36\linewidth}\centering
\begin{tikzpicture}[zfig]
\draw[fill=zinSage!45] (0,0) circle (0.95);
\fill[zinInk] (0,0) circle (1.3pt);
\draw[line width=0.6pt] (0,0) -- (0.95,0);
\node[above] at (0.48,0) {$R$};
\end{tikzpicture}
\end{minipage}\hfill
\begin{minipage}[c]{0.6\linewidth}
$S=\pi R^2$
\end{minipage}
\end{zcard}
\end{minipage}

\zgap
\noindent\begin{minipage}[t]{0.188\linewidth}\vspace{0pt}
\begin{zmini}[equal height group=g4]{Пряма\\призма}
\begin{tikzpicture}[zfig, scale=0.8]
\coordinate (A) at (0,0); \coordinate (B) at (1.15,-0.42); \coordinate (C) at (1.75,0.3);
\coordinate (A1) at (0,1.55); \coordinate (B1) at (1.15,1.13); \coordinate (C1) at (1.75,1.85);
\fill[zinSageTint] (A) -- (B) -- (C) -- (C1) -- (A1) -- cycle;
\draw (A) -- (B) -- (C); \draw[zhid] (A) -- (C);
\draw (A) -- (A1); \draw (B) -- (B1); \draw (C) -- (C1);
\draw (A1) -- (B1) -- (C1) -- cycle;
\node[right] at ($(C)!0.5!(C1)$) {$H$};
\end{tikzpicture}

$V=S_{\zsub{осн}}\cdot H$

$S_{\zsub{б}}=P_{\zsub{осн}}\cdot H$
\end{zmini}
\end{minipage}\hfill
\begin{minipage}[t]{0.215\linewidth}\vspace{0pt}
\begin{zmini}[equal height group=g4]{Правильна\\піраміда}
\begin{tikzpicture}[zfig, scale=0.85]
\coordinate (A) at (0,0); \coordinate (B) at (1.9,0); \coordinate (C) at (2.6,0.7); \coordinate (D) at (0.7,0.7);
\coordinate (O) at (1.3,0.35); \coordinate (S) at (1.3,2.15); \coordinate (K) at ($(A)!0.5!(B)$);
\fill[zinSageTint] (A) -- (B) -- (C) -- (S) -- cycle;
\draw[zhid] (A) -- (D) -- (C); \draw[zhid] (S) -- (D);
\draw[zhid] (A) -- (C); \draw[zhid] (B) -- (D); \draw[zhid] (S) -- (O);
\draw (A) -- (B) -- (C); \draw (S) -- (A); \draw (S) -- (B); \draw (S) -- (C);
\draw[line width=0.6pt] (S) -- (K);
\pic[draw, line width=0.45pt, angle radius=1.6mm] {right angle = S--K--B};
\node at (1.47,1.08) {$H$};
\node at (0.8,0.85) {$m$};
\end{tikzpicture}

$V=\dfrac{1}{3}S_{\zsub{осн}}\cdot H$

$S_{\zsub{б}}=\dfrac{1}{2}P_{\zsub{осн}}\cdot m$
\end{zmini}
\end{minipage}\hfill
\begin{minipage}[t]{0.188\linewidth}\vspace{0pt}
\begin{zmini}[equal height group=g4]{Циліндр\\\phantom{Ц}}
\begin{tikzpicture}[zfig, scale=0.8]
\fill[zinSageTint] (-0.7,0) -- (-0.7,1.75) arc (180:360:0.7 and 0.2) -- (0.7,0) arc (0:-180:0.7 and 0.2) -- cycle;
\draw (-0.7,0) -- (-0.7,1.75); \draw (0.7,0) -- (0.7,1.75);
\draw (0,1.75) ellipse (0.7 and 0.2);
\draw (-0.7,0) arc (180:360:0.7 and 0.2); \draw[zhid] (0.7,0) arc (0:180:0.7 and 0.2);
\draw[zhid] (0,0) -- (0,1.75); \draw[zhid] (0,0) -- (0.7,0);
\fill[zinInk] (0,0) circle (1pt);
\node[left=-1pt] at (0,0.95) {$H$}; \node[above=-1pt, fill=zinSageTint, inner sep=0.6pt] at (0.4,0.02) {$R$};
\end{tikzpicture}

$V=\pi R^2H$

$S_{\zsub{б}}=2\pi RH$
\end{zmini}
\end{minipage}\hfill
\begin{minipage}[t]{0.188\linewidth}\vspace{0pt}
\begin{zmini}[equal height group=g4]{Конус\\\phantom{К}}
\begin{tikzpicture}[zfig, scale=0.8]
\fill[zinSageTint] (-0.7,0) -- (0,1.95) -- (0.7,0) arc (0:-180:0.7 and 0.2) -- cycle;
\draw (-0.7,0) -- (0,1.95) -- (0.7,0);
\draw (-0.7,0) arc (180:360:0.7 and 0.2); \draw[zhid] (0.7,0) arc (0:180:0.7 and 0.2);
\draw[zhid] (0,0) -- (0,1.95); \draw[zhid] (0,0) -- (0.7,0);
\fill[zinInk] (0,0) circle (1pt);
\node[left=-1pt] at (0,0.85) {$H$}; \node[right] at (0.38,1.0) {$L$}; \node[above=-1pt, fill=zinSageTint, inner sep=0.6pt] at (0.4,0.02) {$R$};
\end{tikzpicture}

$V=\dfrac{1}{3}\pi R^2H$

$S_{\zsub{б}}=\pi RL$
\end{zmini}
\end{minipage}\hfill
\begin{minipage}[t]{0.188\linewidth}\vspace{0pt}
\begin{zmini}[equal height group=g4]{Куля, сфера\\\phantom{К}}
\begin{tikzpicture}[zfig, scale=0.8]
\draw[fill=zinSageTint] (0,0) circle (0.85);
\draw (-0.85,0) arc (180:360:0.85 and 0.25); \draw[zhid] (0.85,0) arc (0:180:0.85 and 0.25);
\fill[zinInk] (0,0) circle (1pt);
\draw[zhid] (0,0) -- (35:0.85);
\node[above left=-2pt] at (35:0.5) {$R$};
\end{tikzpicture}

$V=\dfrac{4}{3}\pi R^3$

$S=4\pi R^2$
\end{zmini}
\end{minipage}
\zgap
\begin{zcard}{КООРДИНАТИ ТА ВЕКТОРИ}
\begin{minipage}[c]{0.43\linewidth}\centering
\begin{tikzpicture}[zfig]
\coordinate (A) at (0,0); \coordinate (M) at (2.3,0); \coordinate (B) at (4.6,0);
\draw (A) -- (B);
\foreach \p in {A,M,B} \fill[zinInk] (\p) circle (1.4pt);
\draw[line width=0.5pt] ($(A)!0.5!(M)+(-0.07,-0.1)$) -- ++(0.14,0.2);
\draw[line width=0.5pt] ($(M)!0.5!(B)+(-0.07,-0.1)$) -- ++(0.14,0.2);
\node[below=2pt] at (A) {$A(x_1,\,y_1,\,z_1)$}; \node[below=2pt] at (B) {$B(x_2,\,y_2,\,z_2)$};
\node[above=2pt] at (M) {$M(x_0,\,y_0,\,z_0)$};
\end{tikzpicture}
\end{minipage}\hfill
\begin{minipage}[c]{0.55\linewidth}
$x_0=\dfrac{x_1+x_2}{2}$\qquad $y_0=\dfrac{y_1+y_2}{2}$\qquad $z_0=\dfrac{z_1+z_2}{2}$
\end{minipage}

\vspace{1.2mm}
$\overrightarrow{AB}(x_2-x_1,\ y_2-y_1,\ z_2-z_1)$\qquad $\bigl|\overrightarrow{AB}\bigr|=\sqrt{(x_2-x_1)^2+(y_2-y_1)^2+(z_2-z_1)^2}$

\vspace{0.6mm}
\begin{minipage}[c]{0.43\linewidth}\centering
\begin{tikzpicture}[zfig]
\coordinate (O) at (0,0);
\draw[-{Stealth[length=2.2mm]}] (O) -- (3.0,0) coordinate (b);
\draw[-{Stealth[length=2.2mm]}] (O) -- (2.3,0.95) coordinate (a);
\pic[draw, line width=0.5pt, angle radius=6mm] {angle = b--O--a};
\node at (11:0.9) {$\varphi$};
\node[above left=-1pt] at (1.2,0.5) {$\vec{a}(a_1,\,a_2,\,a_3)$};
\node[above=1pt] at (2.4,0) {$\vec{b}(b_1,\,b_2,\,b_3)$};
\end{tikzpicture}
\end{minipage}\hfill
\begin{minipage}[c]{0.55\linewidth}
$\vec{a}\cdot\vec{b}=a_1b_1+a_2b_2+a_3b_3$

$\vec{a}\cdot\vec{b}=|\vec{a}|\cdot|\vec{b}|\cos\varphi$
\end{minipage}
\end{zcard}
"""


def main(вихід):
    units = " & ".join("\\zinMark{%d}" % u for u in range(10))
    rows = "\\\\\\hline\n".join("\\zinMarkDark{%d} & " % d + " & ".join("$%d$" % ((10 * d + u) ** 2) for u in range(10)) for d in range(1, 5)) + "\\\\"
    tex = (ПРЕАМБУЛА.replace("<<base>>", Т.основа()).replace("<<fonts>>", Т.ШРИФТИ)
           + СТОР_1.replace("<<units>>", units).replace("<<rows>>", rows) + СТОР_2 + СТОР_3 + "\\end{document}\n")
    tex = tex.replace("\\usepackage{xcolor,array,colortbl,fancyhdr}", "\\usepackage{xcolor,array,colortbl,fancyhdr,multirow}")
    tmp = tempfile.mkdtemp(prefix="довідкові_")
    open(os.path.join(tmp, "довідкові.tex"), "w", encoding="utf-8").write(tex)
    for _ in range(2):                                   # equal height group -- з другого проходу
        r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "довідкові.tex"], cwd=tmp, capture_output=True, text=True)
    log = open(os.path.join(tmp, "довідкові.log"), encoding="utf-8", errors="replace").read()
    if r.returncode != 0:
        print(r.stdout[-3000:]); raise SystemExit("помилка LaTeX")
    import re
    over = re.findall(r"Overfull \\hbox \(([\d.]+)pt", log)
    for m in re.finditer(r"Overfull \\hbox \(([\d.]+)pt too wide\) [^\n]*lines? ([\d-]+)", log):
        if float(m.group(1)) > 1: print("  за полем %spt, рядки tex %s" % (m.group(1), m.group(2)))
    print("рядків за полем:", len([o for o in over if float(o) > 1]), "| сторінок:", len(re.findall(r"\[\d+", r.stdout)) or "?")
    shutil.copy(os.path.join(tmp, "довідкові.pdf"), вихід)
    print("готово:", вихід)


if __name__ == "__main__":
    main(sys.argv[1])
