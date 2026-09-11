#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Збірка бази завдань НМТ 2023--2026 по темах у єдиному форматі (формат збірника 2026).

Джерела:
  archive/старий_формат/<тема>/завдання*.tex  -- старі файли 2023--2025 (старий преамбул)
  scripts/data/originals_2026.json            -- оригінали НМТ-2026 (17 сесій, витягнуто скриптом extract_2026_originals.py)
  scripts/data/topics_2026.json               -- розподіл завдань 2026 за темами (можна правити вручну)

Результат:
  <тема>/завдання.tex (для тем 28 і 30 -- окремі файли) у новому форматі + НМТ_2023-2026_всі_теми.tex (master, docmute).

Запуск:  python3 scripts/build_nmt_2023_2026.py
"""
import re, os, sys, json, glob, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCH = os.path.join(ROOT, "archive", "старий_формат")
DATA = os.path.join(ROOT, "scripts", "data")
SESSIONS = ["23.05","30.05","1.06","2.06","3.06","4.06","5.06","8.06","9.06","10.06","11.06","12.06","15.06","16.06","17.06","18.06","19.06"]

# ---------------------------------------------------------------- теми (одиниці збірки)
# key -> (номер папки, відносний шлях файла у папці (вихід), відносний шлях старого файла у папці (в archive), назва)
UNITS = {
 "1":  (1,  "завдання.tex", "завдання.tex", "Числа. Звичайні та десяткові дроби. Модуль числа"),
 "2":  (2,  "завдання.tex", "завдання.tex", "Відсотки, арифметичні задачі, подільність"),
 "3":  (3,  "завдання.tex", "завдання.tex", "Степені. Одночлени. Стандартний вигляд числа"),
 "4":  (4,  "завдання.tex", "завдання.tex", "Многочлени. Формули скороченого множення"),
 "5":  (5,  "завдання.tex", "завдання.tex", "Дробові раціональні вирази і перетворення"),
 "6":  (6,  "завдання.tex", "завдання.tex", "Лінійні рівняння"),
 "7":  (7,  "завдання.tex", "завдання.tex", "Квадратні корені. Корені вищих степенів. Раціональний степінь"),
 "8":  (8,  "завдання.tex", "завдання.tex", "Квадратні рівняння і рівняння, що до них зводяться"),
 "9":  (9,  "завдання.tex", "завдання.tex", "Системи рівнянь"),
 "10": (10, "завдання.tex", "завдання.tex", "Основи планіметрії"),
 "11": (11, "завдання.tex", "завдання.tex", "Трикутники"),
 "12": (12, "завдання.tex", "завдання.tex", "Паралелограм"),
 "13": (13, "завдання.tex", "завдання.tex", "Прямокутник"),
 "14": (14, "завдання.tex", "завдання.tex", "Квадрат"),
 "15": (15, "завдання.tex", "завдання.tex", "Ромб"),
 "16": (16, "завдання.tex", "завдання.tex", "Трапеція"),
 "17": (17, "завдання.tex", "завдання.tex", "Коло, круг і їх елементи"),
 "18": (18, "завдання.tex", "завдання.tex", "Координати і вектори на площині і в просторі. Рівняння кола"),
 "19": (19, "завдання.tex", "завдання.tex", "Лінійні та квадратні нерівності. Системи лінійних нерівностей. Метод інтервалів"),
 "20": (20, "завдання.tex", "завдання.tex", "Функція та її властивості"),
 "21": (21, "завдання.tex", "завдання.tex", "Графіки елементарних функцій, їх побудова та перетворення"),
 "22": (22, "завдання.tex", "завдання.tex", "Модульні рівняння та нерівності"),
 "23": (23, "завдання.tex", "завдання.tex", "Ірраціональні рівняння та нерівності"),
 "24": (24, "завдання.tex", "завдання.tex", "Арифметична прогресія"),
 "25": (25, "завдання.tex", "завдання.tex", "Геометрична прогресія"),
 "26": (26, "завдання.tex", "завдання.tex", "Тригонометричні вирази"),
 "27": (27, "завдання.tex", "завдання.tex", "Тригонометричні рівняння"),
 "28a":(28, "Показникові рівняння/завдання.tex", "Показникові рівняння/завдання.tex", "Показникові рівняння"),
 "28b":(28, "Показникові функція і вирази/завдання.tex", "Показникові функція і вирази/завдання.tex", "Показникова функція і показникові вирази"),
 "29": (29, "завдання.tex", "завдання.tex", "Показникові нерівності"),
 "30a":(30, "завдання вирази.tex", "завдання вирази.tex", "Логарифмічні вирази"),
 "30b":(30, "завдання функція.tex", "завдання функція.tex", "Логарифмічна функція"),
 "31": (31, "завдання.tex", "завдання.tex", "Логарифмічні рівняння"),
 "32": (32, "завдання.tex", "завдання.tex", "Логарифмічні нерівності"),
 "33": (33, "завдання.tex", "завдання.tex", "Похідна"),
 "34": (34, "завдання.tex", "завдання1.tex", "Первісна та інтеграл"),
 "35": (35, "завдання.tex", "завдання.tex", "Комбінаторика"),
 "36": (36, "завдання.tex", "завдання.tex", "Теорія ймовірності"),
 "37": (37, "завдання.tex", "завдання.tex", "Статистика"),
 "38": (38, "завдання.tex", "завдання.tex", "Призма. Паралелепіпед. Куб"),
 "39": (39, "завдання.tex", "завдання.tex", "Піраміда"),
 "40": (40, "завдання.tex", "завдання.tex", "Циліндр"),
 "41": (41, "завдання.tex", "завдання.tex", "Конус"),
 "42": (42, "завдання.tex", "завдання.tex", "Куля. Сфера"),
 "43": (43, "завдання.tex", "завдання.tex", "Параметри"),
}
UNIT_ORDER = sorted(UNITS, key=lambda k: (UNITS[k][0], k))

# ---------------------------------------------------------------- шість розділів (як у збірнику НМТ-2026)
SECTIONS = [
 ("1", "Числа і вирази", ["1","2","3","4","5","7","26","30a"]),
 ("2", "Рівняння і нерівності", ["6","8","9","19","22","23","27","28a","29","31","32","43"]),
 ("3", "Функції", ["20","21","24","25","28b","30b","33","34"]),
 ("4", "Планіметрія", ["10","11","12","13","14","15","16","17"]),
 ("5", "Стереометрія", ["18","38","39","40","41","42"]),
 ("6", "Комбінаторика, теорія ймовірності, статистика", ["35","36","37"]),
]
SECTION_OF = {u: (num, name) for num, name, units in SECTIONS for u in units}
assert set(SECTION_OF) == set(UNITS), "кожна тема має належати рівно одному розділу"

def folder_for(num):
    """папка теми в корені репозиторію за номером (назви містять пробіли/кирилицю)"""
    cands = [d for d in os.listdir(ROOT) if os.path.isdir(os.path.join(ROOT, d)) and re.match(r"^%d\.(\s|\S)" % num, d) and not re.match(r"^%d\d" % num, d)]
    cands = [d for d in cands if re.match(r"^%d\.[^\d]" % num, d)]
    if len(cands) != 1:
        raise SystemExit(f"Не знайдено папку теми {num}: {cands}")
    return cands[0]

# ---------------------------------------------------------------- преамбул формату 2026
PREAMBLE = r"""\documentclass[12pt]{article}
\usepackage[ukrainian,shorthands=off]{babel}   % shorthands=off: символ " не активний (потрібно для міток "..." у TikZ всередині \zadtask)
\usepackage{fontspec}
% --- НАЛАШТУВАННЯ ШРИФТІВ ---
% Шрифти Schoolbook-*.otf лежать у корені проєкту. Шлях підбирається автоматично:
% ../ (компіляція з папки теми), ./ (корінь проєкту), ../../ (підпапки теми 28); інакше -- TeX Gyre Schola.
\newcommand{\nmtSchoolbook}[1]{\setmainfont{Schoolbook-Regular.otf}[
    Path = #1,
    BoldFont = Schoolbook-Bold.otf,
    ItalicFont = Schoolbook-Italic.otf,
    BoldItalicFont = Schoolbook-BoldItalic.otf
]}
\IfFileExists{../Schoolbook-Regular.otf}{\nmtSchoolbook{../}}{%
 \IfFileExists{./Schoolbook-Regular.otf}{\nmtSchoolbook{./}}{%
  \IfFileExists{../../Schoolbook-Regular.otf}{\nmtSchoolbook{../../}}{%
   \setmainfont{texgyreschola}[Extension=.otf, UprightFont=*-regular, BoldFont=*-bold, ItalicFont=*-italic, BoldItalicFont=*-bolditalic]}}}
\usepackage[italic]{mathastext}
\usepackage[a4paper,margin=1.8cm,bottom=2cm,top=2cm]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{tikz}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\usepgfplotslibrary{fillbetween}
\usetikzlibrary{calc,patterns,angles,quotes,intersections,babel,3d,shapes.symbols,shapes.geometric,decorations.pathreplacing,shadings,arrows.meta,hobby}
\usepackage{xcolor,array,fancyhdr,enumitem,multicol}
\usepackage{colortbl,multirow,diagbox}
\usepackage{tcolorbox}
\tcbuselibrary{skins,breakable}
\usepackage[hidelinks]{hyperref}
\usepackage[firstpage=false, text=@pvtr2525, scale=0.6, color=gray!12]{draftwatermark}

% Заборона розриву інлайн-формул
\binoppenalty=10000
\relpenalty=10000

\definecolor{mainGreen}{RGB}{34, 120, 64}
\definecolor{yearOrange}{RGB}{220, 100, 30}
\definecolor{yearcolor}{RGB}{220, 100, 30}
\definecolor{titleBg}{RGB}{225, 240, 220}
\definecolor{instrBg}{RGB}{255, 240, 220}
\definecolor{instrBorder}{RGB}{220, 150, 80}
\definecolor{headerblue}{RGB}{0, 102, 204}   % використовується в рисунках старої бази

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0.4pt}
\fancyhead[C]{\small\color{gray!80} @@HEADER@@}
\fancyhead[R]{\small\color{mainGreen}\textbf{\href{https://t.me/pvtr2525}{@pvtr2525}}}
\fancyfoot[L]{\small\color{gray!80}\href{https://t.me/pvtr2525}{ТГ: @pvtr2525}}
\fancyfoot[C]{\small\color{gray!80}\thepage}
\fancyfoot[R]{\small\color{gray!80}НМТ 2023--2026}

% --- ТАБЛИЦІ ВІДПОВІДЕЙ ---
\newcommand{\answerTable}[5]{%
\par\vspace{0.15cm}
\noindent
\begin{tabular}{|*{5}{>{\centering\arraybackslash}m{3cm}|}}
\hline
\rule[-0.15cm]{0pt}{0.6cm}\textbf{А} & \rule[-0.15cm]{0pt}{0.6cm}\textbf{Б} & \rule[-0.15cm]{0pt}{0.6cm}\textbf{В} & \rule[-0.15cm]{0pt}{0.6cm}\textbf{Г} & \rule[-0.15cm]{0pt}{0.6cm}\textbf{Д} \\
\hline
\rule[-0.2cm]{0pt}{0.75cm}#1 & \rule[-0.2cm]{0pt}{0.75cm}#2 & \rule[-0.2cm]{0pt}{0.75cm}#3 & \rule[-0.2cm]{0pt}{0.75cm}#4 & \rule[-0.2cm]{0pt}{0.75cm}#5 \\
\hline
\end{tabular}
\par\vspace{0.25cm}
}
\newcommand{\answerTableTall}[5]{%
\par\vspace{0.15cm}
\noindent
\begin{tabular}{|*{5}{>{\centering\arraybackslash}m{3cm}|}}
\hline
\rule[-0.2cm]{0pt}{0.7cm}\textbf{А} & \rule[-0.2cm]{0pt}{0.7cm}\textbf{Б} & \rule[-0.2cm]{0pt}{0.7cm}\textbf{В} & \rule[-0.2cm]{0pt}{0.7cm}\textbf{Г} & \rule[-0.2cm]{0pt}{0.7cm}\textbf{Д} \\
\hline
\rule[-0.45cm]{0pt}{1.2cm}#1 & \rule[-0.45cm]{0pt}{1.2cm}#2 & \rule[-0.45cm]{0pt}{1.2cm}#3 & \rule[-0.45cm]{0pt}{1.2cm}#4 & \rule[-0.45cm]{0pt}{1.2cm}#5 \\
\hline
\end{tabular}
\par\vspace{0.25cm}
}
\newcommand{\instructionBox}[1]{%
\par\vspace{0.3cm}
\begin{tcolorbox}[colback=instrBg, colframe=instrBorder, boxrule=0.6pt, arc=2pt,
    left=8pt, right=8pt, top=4pt, bottom=4pt]
\centering\small\bfseries #1
\end{tcolorbox}
\par\vspace{0.15cm}
}
\newcommand{\sectionTitle}[1]{%
\par\vspace{0.4cm}
\begin{tcolorbox}[colback=titleBg, colframe=titleBg, boxrule=0pt, arc=8pt,
    halign=center, fontupper=\Large\bfseries\color{mainGreen}]
#1
\end{tcolorbox}
\par\vspace{0.3cm}
}
\newcommand{\task}[2]{\noindent\textbf{#1.}\ \ #2\par\vspace{0.2cm}}
% --- НМТ-СТИЛЬ ПОЛЕ ВІДПОВІДІ ---
\newcommand{\nmtAnswerBox}{%
\par\vspace{0.2cm}\noindent
Відповідь:\ \
\begin{tabular}{@{}*{4}{|>{\centering\arraybackslash}p{0.8cm}}|@{\hspace{0.1cm}\textbf{,}\hspace{0.1cm}}*{3}{|>{\centering\arraybackslash}p{0.8cm}}|@{}}
\hline
\rule[-0.2cm]{0pt}{0.7cm} & & & & & & \\
\hline
\end{tabular}
\par\vspace{0.3cm}
}
% --- СІТКА ДЛЯ МАТЧИНГУ ---
\newcommand{\matchingGrid}{%
    \begingroup
    \renewcommand{\arraystretch}{1.15}
    \setlength{\tabcolsep}{4pt}
    \footnotesize
    \begin{tabular}{r|c|c|c|c|c|}
         \multicolumn{1}{c}{} & \multicolumn{1}{c}{\textbf{А}} & \multicolumn{1}{c}{\textbf{Б}} & \multicolumn{1}{c}{\textbf{В}} & \multicolumn{1}{c}{\textbf{Г}} & \multicolumn{1}{c}{\textbf{Д}} \\ \cline{2-6}
         \textbf{1} & \phantom{X} & \phantom{X} & \phantom{X} & \phantom{X} & \phantom{X} \\ \cline{2-6}
         \textbf{2} & & & & & \\ \cline{2-6}
         \textbf{3} & & & & & \\ \cline{2-6}
    \end{tabular}
    \endgroup
}
% --- ДОДАТКОВІ МАКРОСИ ЗБІРНИКА ---
\newcommand{\taskBlock}[1]{%
\par\vspace{0.45cm}
\noindent{\color{mainGreen}\rule{\linewidth}{0.8pt}}\par\vspace{0.12cm}
\noindent{\small\bfseries\color{mainGreen}#1}\par\vspace{0.25cm}
}
\newcounter{zad}
\newcommand{\zadtask}[1]{\stepcounter{zad}\noindent\textbf{\thezad.}\ \ #1\par\vspace{0.2cm}}
\newcommand{\zadnum}{\stepcounter{zad}\textbf{\thezad.}\ \ }
\newcounter{ans}
\newcommand{\ansitem}[1]{\stepcounter{ans}\noindent\textbf{\theans.}\ #1\par\vspace{0.07cm}}
\newcommand{\nmtyear}[1]{\hfill{\small\color{yearOrange}(НМТ #1)}}
% --- МАКРОС КОРОТКОГО РОЗВ'ЯЗКУ ---
\newcommand{\solution}[1]{%
\par\vspace{0.12cm}
\begin{tcolorbox}[colback=titleBg!45, colframe=mainGreen!55, boxrule=0.4pt, arc=2pt,
    left=6pt, right=6pt, top=3pt, bottom=3pt, breakable]
\footnotesize\textbf{Короткий розв'язок.}\ #1
\end{tcolorbox}
\par\vspace{0.12cm}
}
% Розв'язки й відповіді (є до завдань НМТ-2026): \showsolutionstrue -- показати, \showsolutionsfalse -- сховати
\newif\ifshowsolutions
\showsolutionsfalse
% --- ЗАГОЛОВКИ З ПУНКТАМИ КЛІКАБЕЛЬНОГО ЗМІСТУ ---
\setcounter{tocdepth}{2}
\newcommand{\chapterTitle}[1]{%
\clearpage\phantomsection\addcontentsline{toc}{section}{#1}%
\sectionTitle{#1}}
\newcommand{\typeTitle}[1]{%
\phantomsection\addcontentsline{toc}{subsection}{\quad #1}%
\par\vspace{0.3cm}
\noindent{\large\bfseries\color{yearOrange}#1}\par\vspace{0.08cm}
\noindent{\color{yearOrange}\rule{\linewidth}{0.4pt}}\par\vspace{0.2cm}}
\newcommand{\ansTheme}[1]{\par\vspace{0.25cm}\noindent{\bfseries\color{mainGreen}#1}\par\vspace{0.12cm}}
\newcommand{\ansType}[1]{\par\vspace{0.1cm}\noindent{\itshape\color{yearOrange}#1}\par\vspace{0.08cm}}
"""

# макроси нового преамбула (їх зі старих файлів НЕ переносимо)
NEW_DEFINED = {"answerTable","answerTableTall","instructionBox","sectionTitle","task","nmtAnswerBox","matchingGrid",
               "taskBlock","zadtask","zadnum","ansitem","nmtyear","solution","chapterTitle","typeTitle","ansTheme","ansType",
               "nmtSchoolbook","ifshowsolutions","showsolutionstrue","showsolutionsfalse"}
# старі макроси, які перейменовуємо в тілі на нові
RENAMES = [(r"\\answerTableBig\b", r"\\answerTableTall"),
           (r"\\matchTable\b", r"\\matchingGrid"),
           (r"\\answerGridSmall\b", r"\\matchingGrid"),
           (r"\\answerGrid\b", r"\\matchingGrid"),
           (r"\\answerBox\b", r"\\nmtAnswerBox"),
           (r"\\shortAnswer\b", r"\\nmtAnswerBox")]
COMPAT = r"""% --- сумісність зі старою базою (діє, якщо тема не має власного визначення) ---
\providecommand{\trigStyle}[1]{\textbf{#1}}
\providecommand{\answerTableSmall}[5]{%
\begin{tabular}{|*{5}{>{\centering\arraybackslash}m{1.65cm}|}}
\hline
\rule[-0.2cm]{0pt}{0.6cm}\textbf{А} & \textbf{Б} & \textbf{В} & \textbf{Г} & \textbf{Д} \\
\hline
\rule[-0.4cm]{0pt}{0.9cm}#1 & \rule[-0.4cm]{0pt}{0.9cm}#2 & \rule[-0.4cm]{0pt}{0.9cm}#3 & \rule[-0.4cm]{0pt}{0.9cm}#4 & \rule[-0.4cm]{0pt}{0.9cm}#5 \\
\hline
\end{tabular}}
\providecommand{\matchingLayout}[3]{%
    \noindent
    \begin{minipage}[t]{0.40\textwidth}
        #1
    \end{minipage}%
    \hfill
    \begin{minipage}[t]{0.28\textwidth}
        #2
    \end{minipage}%
    \hfill
    \begin{minipage}[t]{0.30\textwidth}
        \vspace{0pt}
        \begin{flushright}
        #3
        \end{flushright}
    \end{minipage}}
\providecommand{\matchingLayoutBottom}[2]{%
    \noindent
    \begin{minipage}[t]{0.48\textwidth}
        #1
    \end{minipage}%
    \hfill
    \begin{minipage}[t]{0.48\textwidth}
        #2
    \end{minipage}
    \vspace{0.5cm}
    \noindent
    \matchingGrid}
\providecommand{\answerListVertical}[5]{%
    \vspace{0.2cm}
    \begin{itemize}[itemsep=0.4cm, leftmargin=1.5cm, labelsep=0.5cm]
        \item[\textbf{А}] #1
        \item[\textbf{Б}] #2
        \item[\textbf{В}] #3
        \item[\textbf{Г}] #4
        \item[\textbf{Д}] #5
    \end{itemize}
    \vspace{0.2cm}}

"""
DROPPED = {"answerTableBig","matchTable","answerGrid","answerGridSmall","answerBox","shortAnswer"}
KNOWN_PKGS = {"fontspec","polyglossia","geometry","amsmath","amssymb","enumitem","tikz","pgfplots","xcolor","array","fancyhdr",
              "multirow","multicol","diagbox","graphicx","babel","mathastext","colortbl","tcolorbox","hyperref","draftwatermark"}
GLOBAL_TIKZLIBS = {"calc","patterns","angles","quotes","intersections","babel","3d","shapes.symbols","shapes.geometric",
                   "decorations.pathreplacing","shadings","arrows.meta","hobby"}

def balanced(s, i):
    """s[i]=='{' -> індекс парної '}' (з урахуванням \\{ \\})"""
    d = 0; j = i
    while j < len(s):
        c = s[j]
        if c == '\\':
            j += 2; continue
        if c == '{': d += 1
        elif c == '}':
            d -= 1
            if d == 0: return j
        j += 1
    raise ValueError("unbalanced braces")

def read_group(s, i):
    """пропустити пробіли, прочитати {..} або [..] або \\cs; повернути (text, next_index) або (None,i)"""
    j = i
    while j < len(s) and s[j] in " \t\n%": 
        if s[j] == '%':
            while j < len(s) and s[j] != '\n': j += 1
        else: j += 1
    if j >= len(s): return None, i
    if s[j] == '{':
        e = balanced(s, j); return s[j:e+1], e+1
    if s[j] == '[':
        e = s.find(']', j); return s[j:e+1], e+1
    if s[j] == '\\':
        m = re.match(r"\\([a-zA-Z@]+|.)", s[j:]); return m.group(0), j+len(m.group(0))
    return None, i

# ---------------------------------------------------------------- перенесення макросів зі старого преамбула
def extract_defs(pre, warn):
    """повертає (список рядків-визначень для перенесення, множина tikz-бібліотек, множина пакетів)"""
    carried, libs, pkgs = [], set(), set()
    pat = re.compile(r"\\(newcommand|renewcommand|providecommand|newenvironment|newcounter|newlength|DeclareMathOperator|tikzset|pgfplotsset|pgfmathdeclarefunction|definecolor|colorlet|newif|setlength|usetikzlibrary|usepackage|def(?![a-zA-Z]))\*?")
    pos = 0
    while True:
        m = pat.search(pre, pos)
        if not m: break
        # пропустити закоментовані
        ls = pre.rfind("\n", 0, m.start()) + 1
        if "%" in pre[ls:m.start()]:
            pos = m.end(); continue
        cmd = m.group(1); j = m.end()
        try:
            if cmd in ("newcommand","renewcommand","providecommand"):
                name, j = read_group(pre, j); name = name.strip("{}")
                opts = []
                while True:
                    g, j2 = read_group(pre, j)
                    if g and g.startswith("["): opts.append(g); j = j2
                    else: break
                body, j = read_group(pre, j)
                stmt = pre[m.start():j]
                nm = name.lstrip("\\")
                if nm in NEW_DEFINED or nm in DROPPED or nm in ("headrulewidth","footrulewidth"): pass
                else: carried.append(stmt)
            elif cmd == "def":
                name, j = read_group(pre, j)
                k = pre.find("{", j); e = balanced(pre, k); j = e+1
                stmt = pre[m.start():j]; nm = name.lstrip("\\")
                if nm not in NEW_DEFINED and nm not in DROPPED: carried.append(stmt)
            elif cmd == "newenvironment":
                name, j = read_group(pre, j)
                while True:
                    g, j2 = read_group(pre, j)
                    if g and g.startswith("["): j = j2
                    else: break
                b1, j = read_group(pre, j); b2, j = read_group(pre, j)
                carried.append(pre[m.start():j])
            elif cmd in ("newcounter","newlength","newif"):
                g, j = read_group(pre, j)
                if cmd == "newcounter":
                    g2, j2 = read_group(pre, j)
                    if g2 and g2.startswith("["): j = j2
                stmt = pre[m.start():j]
                if g.strip("{}").lstrip("\\") not in ("zad","ans","showsolutions"): carried.append(stmt)
            elif cmd == "DeclareMathOperator":
                g1, j = read_group(pre, j); g2, j = read_group(pre, j); carried.append(pre[m.start():j])
            elif cmd in ("tikzset","pgfmathdeclarefunction"):
                g, j = read_group(pre, j)
                if cmd == "pgfmathdeclarefunction":
                    g2, j = read_group(pre, j); g3, j = read_group(pre, j)
                carried.append(pre[m.start():j])
            elif cmd == "pgfplotsset":
                g, j = read_group(pre, j)
                if "compat" not in g: carried.append(pre[m.start():j])
            elif cmd == "definecolor":
                g1, j = read_group(pre, j); g2, j = read_group(pre, j); g3, j = read_group(pre, j)
                if g1.strip("{}") not in ("headerblue","yearcolor","mainGreen","yearOrange","titleBg","instrBg","instrBorder"):
                    carried.append(pre[m.start():j])
            elif cmd == "colorlet":
                g1, j = read_group(pre, j); g2, j = read_group(pre, j); carried.append(pre[m.start():j])
            elif cmd == "setlength":
                g1, j = read_group(pre, j); g2, j = read_group(pre, j)
                if g1.strip("{}") not in ("\\headheight","\\headsep","\\footskip","\\parindent"): carried.append(pre[m.start():j])
            elif cmd == "usetikzlibrary":
                g, j = read_group(pre, j)
                for x in g.strip("{}").split(","):
                    x = x.strip()
                    if x: libs.add(x)
            elif cmd == "usepackage":
                g, j = read_group(pre, j)
                if g.startswith("["): g, j = read_group(pre, j)
                for x in g.strip("{}").split(","):
                    x = x.strip()
                    if x: pkgs.add(x)
        except Exception as e:
            warn(f"не вдалося розібрати {cmd} у преамбулі: {e}")
            j = m.end()
        pos = j
    return carried, libs, pkgs

# ---------------------------------------------------------------- захист tikz-блоків
def protect(body):
    store = []
    def rep(m):
        store.append(m.group(0)); return "\x00TIKZ%d\x00" % (len(store)-1)
    body = re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", rep, body, flags=re.S)
    return body, store
def restore(text, store):
    return re.sub(r"\x00TIKZ(\d+)\x00", lambda m: store[int(m.group(1))], text)

# ---------------------------------------------------------------- заголовки років у старих файлах
def mark_headers(body):
    def rep(m):
        c = m.group(1)
        if re.search(r"НМТ\s*20\d\d\s*-{1,3}\s*20\d\d", c): return "\n@@DROP@@\n"
        y = re.search(r"НМТ\s*(20\d\d)", c)
        if y and ("headerblue" in c or "БАЗА" in c or "Large" in c or "large" in c): return "\n@@YEAR %s@@\n" % y.group(1)
        if ("Тема" in c and ("large" in c or "Large" in c)) or "БАЗА ЗАВДАНЬ" in c: return "\n@@DROP@@\n"
        return m.group(0)
    body = re.sub(r"\\begin\{center\}(.*?)\\end\{center\}", rep, body, flags=re.S)
    # коментарі-розділювачі блоків
    body = re.sub(r"^[ \t]*%[ \t]*БЛОК[^\n]*$", "@@DROP@@", body, flags=re.M)
    body = re.sub(r"^[ \t]*%[ \t]*=+[ \t]*$", "", body, flags=re.M)
    return body

START_RE = re.compile(
    r"(?P<A>\\task\{(?P<na>\d+)\}\{)"
    r"|(?P<B>\\noindent\s*\\makebox\[[^\]]*\]\[l\]\{\\textbf\{(?P<nb>\d+)\.\}\}\s*\\parbox\[t\]\{[^{}]*\}\{)"
    r"|(?P<C>\\textbf\{(?P<nc>\d+)(?:\s*\(Fix\))?\.\})")

def chunk_start_line(body, pos):
    """початок chunk'а: рядок з матчем + попередні рядки-коментарі / \\noindent / \\begin{minipage}"""
    ls = body.rfind("\n", 0, pos) + 1
    while True:
        pe = ls - 1
        if pe < 0: break
        pls = body.rfind("\n", 0, pe) + 1
        prev = body[pls:pe].strip()
        if prev == "": break
        if prev.startswith("%") or prev.rstrip("%").strip() == "\\noindent" or prev.startswith("\\begin{minipage}") or prev.startswith("\\noindent\\begin{minipage}"):
            ls = pls; continue
        break
    return ls

def split_old(body, warn):
    """-> (pre_text, [chunk_text...], [old_number...])"""
    ms = list(START_RE.finditer(body))
    if not ms: return body, [], []
    starts = [chunk_start_line(body, m.start()) for m in ms]
    # усунути можливі перекриття (start не може бути раніше попереднього матчу)
    for k in range(1, len(starts)):
        if starts[k] <= ms[k-1].start(): starts[k] = body.rfind("\n", 0, ms[k].start()) + 1
    nums = [int(m.group("na") or m.group("nb") or m.group("nc")) for m in ms]
    chunks = [body[starts[k]:(starts[k+1] if k+1 < len(starts) else len(body))] for k in range(len(starts))]
    # перевірка нумерації
    for k in range(1, len(nums)):
        if nums[k] not in (nums[k-1]+1, 1, nums[k-1]) and "Fix" not in ms[k].group(0):
            warn(f"нетипова нумерація: після {nums[k-1]} іде {nums[k]}")
    return body[:starts[0]], chunks, nums

def convert_start(chunk):
    """перший старт завдання у chunk -> \\zadtask{ / \\zadnum"""
    m = START_RE.search(chunk)
    if not m: raise ValueError("no task start in chunk")
    if m.group("A") or m.group("B"):
        return chunk[:m.start()] + "\\zadtask{" + chunk[m.end():]
    # C
    after = chunk[m.end():]
    after = re.sub(r"^(\\ )*[ \t]*", "", after)   # прибрати \ \ або пробіли після номера
    before = chunk[:m.start()]
    if re.search(r"\\noindent\s*$", before):
        before = re.sub(r"\\noindent\s*$", "\\\\noindent", before)
    return before + "\\zadnum " + after

def clean_chunk(chunk):
    for a, b in RENAMES: chunk = re.sub(a, b, chunk)
    lines = []
    for l in chunk.split("\n"):
        ls = l.strip()
        if ls in ("\\newpage", "\\clearpage", "@@DROP@@") or ls.startswith("@@YEAR"): continue
        if re.fullmatch(r"%\s*[-=]{4,}\s*", ls): continue
        if re.fullmatch(r"%\s*={3,}\s*(№\s*\d+|Завдання\s*\d+|ЗАВДАННЯ\s*\d+)\s*={3,}\s*", ls): continue
        lines.append(l.rstrip())
    # зняти хвостові \vspace / порожні рядки
    while lines and (lines[-1].strip() == "" or re.fullmatch(r"\\vspace\*?\{[^}]*\}", lines[-1].strip()) or re.fullmatch(r"\\vspace\*?\{[^}]*\}\s*%.*", lines[-1].strip())):
        lines.pop()
    while lines and lines[-1].strip() == "": lines.pop()
    while lines and lines[0].strip() == "": lines.pop(0)
    t = "\n".join(lines)
    t = re.sub(r"\n{3,}", "\n\n", t)
    # помилки старих файлів: зайвий $ після одиниць вимірювання у клітинці таблиці
    t = re.sub(r"(\\textit\{[^{}]*\})\$(\s*\})", r"\1\2", t)
    # незбалансований \end{minipage} у старому файлі -- прибрати зайві
    nb = len(re.findall(r"\\begin\{minipage\}", t)); ne = len(re.findall(r"\\end\{minipage\}", t))
    while ne > nb:
        k = t.rfind("\\end{minipage}"); t = t[:k] + t[k+len("\\end{minipage}"):]; ne -= 1
    return t

BOUNDARY_RE = re.compile(r"\n[ \t]*(\n|\\vspace|\\begin\{|\\par\b|\\nmtAnswerBox|\\answer|\\matching|\\hfill|\\centering|\\end\{minipage\}|\\noindent|\\newline|\\item|\\hspace|\\tikz|\\includegraphics|\\renewcommand)|\\\\(\[[^\]]*\])?")
MASK_RE = re.compile(r"\$(?:\\.|[^$\\])*\$|\\\[.*?\\\]|\\begin\{(cases|tabular|array|aligned|align\*?|matrix|pmatrix|bmatrix|tikzpicture|axis|itemize|enumerate)\}.*?\\end\{\1\}", re.S)

def find_boundary(region):
    masked = [(m.start(), m.end()) for m in MASK_RE.finditer(region)]
    for m in BOUNDARY_RE.finditer(region):
        if any(a <= m.start() < b for a, b in masked): continue
        return m.start()
    return len(region)

PREFIX_RE = re.compile(r"\s*(\\begin\{minipage\}(\[[^\]]*\])?\{[^{}]*\}|\\begin\{center\}|\\vspace\*?\{[^}]*\}|\\noindent|\\centering|%[^\n]*\n)")

def insert_year(chunk, year):
    """вставити \\nmtyear{year} наприкінці умови (перший абзац після \\zadtask{ або \\zadnum)"""
    m = re.search(r"\\zadtask\{|\\zadnum\s?", chunk)
    if not m: return chunk
    i = m.end()
    if m.group(0).startswith("\\zadtask"):
        region_end = balanced(chunk, m.end()-1)
    else:
        region_end = len(chunk)
    # пропустити префікси макета (minipage/center/vspace) на початку умови
    while True:
        pm = PREFIX_RE.match(chunk, i, region_end)
        if pm and pm.end() > i: i = pm.end()
        else: break
    region = chunk[i:region_end]
    b = find_boundary(region)
    seg = region[:b].rstrip()
    if seg.endswith("%"): seg = seg[:-1].rstrip()
    ins = i + len(seg)
    return chunk[:ins] + " \\nmtyear{%s}" % year + chunk[ins:]

def count_starts(chunk):
    return len(re.findall(r"\\zadtask\{|\\zadnum\b", chunk))

# ---------------------------------------------------------------- 2026
def load_2026():
    tasks = json.load(open(os.path.join(DATA, "originals_2026.json"), encoding="utf-8"))
    topics = json.load(open(os.path.join(DATA, "topics_2026.json"), encoding="utf-8"))
    by_unit = collections.defaultdict(list)
    for t in tasks:
        tops = topics.get(t["id"])
        if not tops:
            print("УВАГА: завдання 2026 без теми:", t["id"]); continue
        for k, u in enumerate(tops):
            by_unit[u].append((t, tops[0] if k > 0 else None, tops[1:] if k == 0 else []))
    for u in by_unit:
        by_unit[u].sort(key=lambda x: (SESSIONS.index(x[0]["session"]), x[0]["n"]))
    return by_unit

def prep_2026(t):
    c = t["latex"]
    c = re.sub(r"\s*\\nmtyear\{\d{4}\}", "", c)
    c = clean_chunk(c)
    c = insert_year(c, "2026")
    if count_starts(c) != 1: raise SystemExit(f"2026 {t['id']}: {count_starts(c)} стартів завдання")
    return c

# ---------------------------------------------------------------- збірка однієї теми
def build_unit(key, by2026, log):
    num, out_rel, old_rel, title = UNITS[key]
    folder = folder_for(num)
    old_path = os.path.join(ARCH, folder, old_rel)
    out_path = os.path.join(ROOT, folder, out_rel)
    warns = []
    warn = lambda s: warns.append(s)
    tex = open(old_path, encoding="utf-8").read()
    pre, body = tex.split("\\begin{document}", 1)
    body = body.split("\\end{document}")[0]
    carried, libs, pkgs = extract_defs(pre, warn)
    for x in libs - GLOBAL_TIKZLIBS: warn(f"tikz-бібліотека {x} відсутня в новому преамбулі")
    for x in pkgs - KNOWN_PKGS: warn(f"пакет {x} відсутній у новому преамбулі")
    body, store = protect(body)
    body = mark_headers(body)
    pre_text, chunks, nums = split_old(body, warn)
    # визначення у тілі до першого завдання
    pre_defs = []
    for l in pre_text.split("\n"):
        ls = l.strip()
        if not ls or ls.startswith("%") or ls.startswith("@@") or ls.startswith("\\vspace") or ls in ("\\noindent",): continue
        if re.match(r"\\(newcommand|renewcommand|def|tikzset|pgfplotsset|newcounter|setlength|setcounter|newlength)\b", ls): pre_defs.append(l)
        else: warn(f"текст до першого завдання пропущено: {ls[:70]}")
    # роки
    cur_year = None
    for m in re.finditer(r"@@YEAR (\d{4})@@", pre_text): cur_year = m.group(1)
    items = []
    for ch, n in zip(chunks, nums):
        tags = re.findall(r"\\nmtyear\{(\d{4})\}", ch)
        header_year = cur_year
        for m in re.finditer(r"@@YEAR (\d{4})@@", ch): cur_year = m.group(1)
        year = tags[0] if tags else header_year
        items.append(dict(chunk=ch, num=n, year=year, tagged=bool(tags), inferred=False))
    # вивід року за сусідами, якщо немає ні тегу, ні заголовка
    for k, it in enumerate(items):
        if it["year"] is None:
            prev = next((items[j]["year"] for j in range(k-1, -1, -1) if items[j]["year"]), None)
            nxt = next((items[j]["year"] for j in range(k+1, len(items)) if items[j]["year"]), None)
            it["year"] = prev or nxt or "2023"; it["inferred"] = True
            warn(f"завдання {it['num']}: рік не вказано, взято {it['year']} за сусідніми")
    # конвертація
    for it in items:
        c = convert_start(it["chunk"])
        c = clean_chunk(c)
        if not it["tagged"]:
            c = insert_year(c, it["year"])
        c = restore(c, store)
        # відомі помилкові рядки старих файлів (некоректний синтаксис TikZ; далі координата задана вручну)
        c = re.sub(r"^[ \t]*\\coordinate \(C\) at \(intersection of O--B and O circle 1\.5cm\);[^\n]*\n", "", c, flags=re.M)
        if count_starts(c) != 1:
            warn(f"завдання {it['num']}: {count_starts(c)} стартів у chunk")
        it["out"] = c
    # дублікати (те саме завдання двічі у старому файлі) -- лишаємо перше
    seen = set(); uniq = []
    for it in items:
        sig = re.sub(r"%[^\n]*", "", it["out"]); sig = re.sub(r"\s+", "", sig)
        if sig in seen:
            warn(f"завдання {it['num']}: точний дублікат уже наявного завдання пропущено"); continue
        seen.add(sig); uniq.append(it)
    items = uniq
    # групування за роками (стабільно)
    years = sorted({it["year"] for it in items})
    if [it["year"] for it in items] != sorted(it["year"] for it in items):
        warn("порядок завдань за роками змінено (згруповано за роками)")
    parts = []
    counts = collections.OrderedDict()
    gl = 0
    for y in years:
        grp = [it for it in items if it["year"] == y]
        counts[y] = len(grp)
        parts.append("\\typeTitle{НМТ %s}\n" % y)
        for it in grp:
            gl += 1
            s = it["out"]
            if it["inferred"]: s = "% рік визначено за сусідніми завданнями (у старому файлі тег року відсутній)\n" + s
            parts.append(s + "\n")
    # 2026
    t26 = by2026.get(key, [])
    ans_lines = []
    if t26:
        counts["2026"] = len(t26)
        parts.append("\\typeTitle{НМТ 2026}\n")
        for t, primary, secondary in t26:
            gl += 1
            note = f"% НМТ 2026, сесія {t['session']}, завдання №{t['n']}"
            if t.get("restored"): note += " (відновлено за збірником)"
            if primary: note += f" --- основна тема: {UNITS[primary][3]}"
            if secondary: note += " --- також у темі: " + ", ".join(UNITS[s][3] for s in secondary)
            s = note + "\n" + prep_2026(t) + "\n"
            if t.get("answer"):
                s += "% Відповідь: " + t["answer"].replace("\n", " ") + "\n"
                ans_lines.append((gl, t["answer"], t["session"], t["n"]))
            if t.get("solution"):
                s += "\\ifshowsolutions\\solution{" + t["solution"].strip() + "}\\fi\n"
            parts.append(s)
    total = sum(counts.values())
    stat = ", ".join(f"{y}~--- {c}" for y, c in counts.items())
    header = f"База завдань НМТ 2023--2026 \\textendash{{}} Тема {key}"
    out = [PREAMBLE.replace("@@HEADER@@", header)]
    out.append("\n\\begin{document}\n\\begingroup\\setcounter{zad}{0}\n")
    if carried or pre_defs:
        out.append("% --- макроси, перенесені зі старого файлу теми ---\n")
        for c in carried:
            for a, b in RENAMES: c = re.sub(a, b, c)
            out.append(c + "\n")
        for c in pre_defs: out.append(c + "\n")
        out.append("\n")
    # макроси з преамбул сесійних файлів 2026, потрібні рисункам
    ex_seen = {}
    for t, _, _ in t26:
        for d in t.get("extra_defs", []):
            nm = re.search(r"\\(?:definecolor|newcommand|renewcommand|def)\*?\s*\{?\\?([a-zA-Z0-9]+)", d).group(1)
            if nm in ("arraystretch", "tabcolsep"): continue
            if nm in ex_seen:
                if re.sub(r"\s+","",ex_seen[nm]) != re.sub(r"\s+","",d): warn(f"2026: різні визначення {nm} у різних сесіях, взято перше")
            else: ex_seen[nm] = d
    if ex_seen:
        out.append("% --- макроси з файлів сесій НМТ-2026 (для рисунків) ---\n")
        for d in ex_seen.values(): out.append(d + "\n")
        out.append("\n")
    out.append(COMPAT)
    if "\\includegraphics" in "".join(it["out"] for it in items):
        out.append("\\graphicspath{{./}{%s/}}\n" % folder)
    out.append("\\chapterTitle{Тема %s. %s}\n" % (key, title))
    secnum, secname = SECTION_OF[key]
    out.append("\\noindent{\\small\\color{gray!80} Розділ %s. %s \\quad\\textbullet\\quad Усього завдань: %d (НМТ %s).}\\par\\vspace{0.2cm}\n\n" % (secnum, secname, total, stat))
    out.append("\n".join(parts))
    if ans_lines:
        out.append("\n\\ifshowsolutions\n\\sectionTitle{ВІДПОВІДІ ДО ЗАВДАНЬ НМТ 2026}\n\\begin{multicols}{3}\\noindent\n")
        for gl_, a, sess, n in ans_lines:
            out.append("\\noindent\\textbf{%d.}~%s \\ {\\scriptsize\\color{gray}(%s, №%d)}\\par\n" % (gl_, a.replace("\n"," "), sess, n))
        out.append("\\end{multicols}\n\\fi\n")
    out.append("\n\\endgroup\n\\end{document}\n")
    text = "".join(out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    open(out_path, "w", encoding="utf-8").write(text)
    log.append(dict(key=key, title=title, out=os.path.relpath(out_path, ROOT), counts=dict(counts), total=total, warns=warns,
                    carried=[re.match(r"\\\w+\{?\\?(\w+)", c).group(0) if re.match(r"\\\w+\{?\\?(\w+)", c) else c[:20] for c in carried]))
    return out_path

MASTER_EXTRA = r"""\usepackage{docmute}
% у зведених документах: розділ = section, тема = subsection, рік = subsubsection
\setcounter{tocdepth}{3}
\renewcommand{\chapterTitle}[1]{\clearpage\phantomsection\addcontentsline{toc}{subsection}{#1}\sectionTitle{#1}}
\renewcommand{\typeTitle}[1]{\phantomsection\addcontentsline{toc}{subsubsection}{\quad #1}%
\par\vspace{0.3cm}\noindent{\large\bfseries\color{yearOrange}#1}\par\vspace{0.08cm}%
\noindent{\color{yearOrange}\rule{\linewidth}{0.4pt}}\par\vspace{0.2cm}}
\newcommand{\partTitle}[1]{\clearpage\phantomsection\addcontentsline{toc}{section}{#1}%
\vspace*{0.5cm}\begin{tcolorbox}[colback=titleBg, colframe=mainGreen!60, boxrule=0.8pt, arc=8pt, halign=center, fontupper=\LARGE\bfseries\color{mainGreen}]
#1
\end{tcolorbox}\par\vspace{0.4cm}}
"""

def input_line(rel):
    # шляхи з пробілами (зокрема подвійними) -- у лапках, пробіл як \space
    return "\\input{\"%s\"}\n" % rel.replace("\\", "/").replace(" ", "\\space ")

def build_collection(fname, header, title_lines, sections, paths_by_unit):
    out = [PREAMBLE.replace("@@HEADER@@", header), MASTER_EXTRA, "\\begin{document}\n"]
    out.append("\\thispagestyle{empty}\n\\vspace*{2cm}\n\\begin{center}\n" + title_lines +
               "\n{\\large\\color{mainGreen}\\textbf{\\href{https://t.me/pvtr2525}{Телеграм: @pvtr2525}}}\n\\end{center}\n\\clearpage\n")
    out.append("{\\hypersetup{linkcolor=black}\\tableofcontents}\n")
    for num, name, units in sections:
        out.append("\\partTitle{РОЗДІЛ %s. %s}\n" % (num, name.upper()))
        for u in units: out.append(input_line(paths_by_unit[u]))
    out.append("\\end{document}\n")
    open(os.path.join(ROOT, fname), "w", encoding="utf-8").write("".join(out))

def build_master(paths_by_unit):
    t = ("{\\Huge\\bfseries\\color{mainGreen} БАЗА ЗАВДАНЬ НМТ}\\\\[0.4cm]\n{\\LARGE\\bfseries\\color{mainGreen} 2023--2026}\\\\[0.6cm]\n"
         "{\\Large\\bfseries з математики}\\\\[0.8cm]\n{\\large Усі завдання основних сесій: 6 розділів, 43 теми}\\\\[1.2cm]")
    build_collection("НМТ_2023-2026_всі_теми.tex", "База завдань НМТ 2023--2026 \\textendash{} усі теми", t, SECTIONS, paths_by_unit)
    for num, name, units in SECTIONS:
        t = ("{\\Huge\\bfseries\\color{mainGreen} РОЗДІЛ %s}\\\\[0.4cm]\n{\\LARGE\\bfseries\\color{mainGreen} %s}\\\\[0.6cm]\n"
             "{\\Large База завдань НМТ 2023--2026}\\\\[0.8cm]\n{\\large Теми: %s}\\\\[1.2cm]") % (num, name, ", ".join(u for u in units))
        fname = "Розділ_%s_%s.tex" % (num, re.sub(r"[ ,]+", "_", name))
        build_collection(fname, "База завдань НМТ 2023--2026 \\textendash{} Розділ %s" % num, t, [(num, name, units)], paths_by_unit)

def main():
    by2026 = load_2026()
    log = []; paths_by_unit = {}
    for key in UNIT_ORDER:
        p = build_unit(key, by2026, log)
        paths_by_unit[key] = os.path.relpath(p, ROOT)
    build_master(paths_by_unit)
    json.dump(log, open(os.path.join(DATA, "build_log.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    tot = collections.Counter()
    for e in log:
        print(f"[{e['key']:>3}] {e['total']:4d}  {e['counts']}  -> {e['out']}")
        for w in e["warns"]: print("       ! " + w)
        for y, c in e["counts"].items(): tot[y] += c
    print("РАЗОМ (з урахуванням завдань у кількох темах):", dict(tot), "=", sum(tot.values()))

if __name__ == "__main__":
    main()
