# -*- coding: utf-8 -*-
"""Тема «як справжній НМТ» для пробного -- оформлення під тестовий зошит УЦОЯО: титульна сторінка в рамці з інструкціями,
номер завдання на полі й текст із відступом, клітинки для чернетки під кожним завданням (сітка розтягується на вільне
місце сторінки, як у зошиті), «Кінець зошита», бланк відповідей і ключ. Без логотипів і назв УЦОЯО: на титулці сказано,
що це авторський пробний тест.

Перевизначає макроси бази (\\zadtask, \\zadnum, \\instructionBox, \\nmtAnswerBox), тож завдання не змінюються.

    import тема_нмт
    tex = тема_нмт.застосувати(tex, назва, завдання, перша_сторінка=5)
    tex = tex.replace("\\end{document}", тема_нмт.бланк(номер) + тема_нмт.ключ(завдання) + "\\end{document}")
    тема_нмт.титулка_pdf(ВИХІД.pdf, номер, сторінки_довідкових="2--4")
"""
import os, re, shutil, tempfile, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

# інструкції перед групами завдань -- як у зошитах (відповіді -- у бланку)
ІНСТРУКЦІЇ = {
    1: "Завдання 1--15 мають по п'ять варіантів відповіді, з яких лише один правильний. Виберіть правильний, на Вашу думку, "
       "варіант відповіді й позначте його в бланку відповідей згідно з інструкцією.",
    16: "У завданнях 16--18 до кожного з трьох рядків інформації, позначених цифрами, доберіть один правильний, на Вашу думку, "
        "варіант, позначений буквою. Поставте позначки в таблицях відповідей до завдань у бланку відповідей на перетині "
        "відповідних рядків (цифри) і колонок (букви).",
    19: "Розв'яжіть завдання 19--22. Одержані числові відповіді запишіть у бланку відповідей. Відповідь записуйте лише "
        "десятковим дробом, урахувавши положення коми, по одній цифрі в кожній клітинці. Знак «мінус» записуйте перед першою "
        "цифрою числа.",
}
# мінімальна висота чернетки під завданням (решту вільного місця сторінки сітка забирає сама)
ЧЕРНЕТКА = {"single": "2.5cm", "matching": "2.5cm", "input": "4cm"}

ПРЕАМБУЛА = r"""
% ===================== ТЕМА «ЯК СПРАВЖНІЙ НМТ» (тестовий зошит) =====================
\geometry{left=1.9cm, right=1.9cm, top=1.7cm, bottom=1.9cm, footskip=0.85cm}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
\fancyfoot[C]{\small\thepage}
\flushbottom
% рисунки -- у відтінках сірого, як у зошитах
\colorlet{mainGreen}{black!50}
\colorlet{yearOrange}{black!38}
% номер завдання -- на полі, текст, таблиці й рисунки -- з відступом
\newlength{\nmtIndent}\setlength{\nmtIndent}{0.85cm}
\newenvironment{nmtTaskBody}{\stepcounter{zad}%
  \begin{list}{}{\setlength{\leftmargin}{\nmtIndent}\setlength{\labelwidth}{\nmtIndent}\setlength{\labelsep}{0pt}%
    \setlength{\topsep}{0pt}\setlength{\partopsep}{0pt}\setlength{\itemsep}{0pt}\setlength{\parsep}{0pt}}%
  \item[{\makebox[\nmtIndent][l]{\textbf{\thezad.}}}]\setlength{\textwidth}{\linewidth}}{\end{list}}
\renewcommand{\zadtask}[1]{#1\par\nopagebreak\vspace{0.2cm}}
\renewcommand{\zadnum}{}
% інструкція перед групою завдань: жирний абзац і рамка з нагадуванням
\renewcommand{\instructionBox}[1]{%
\par\vspace{0.3cm}\noindent{\bfseries #1}\par\nopagebreak\vspace{0.22cm}\noindent
\fbox{\parbox{\dimexpr\linewidth-2\fboxsep-2\fboxrule}{\centering\small\bfseries Будьте особливо уважні під час заповнення
\textit{бланка відповідей}!\\ Неправильно позначену чи виправлену відповідь буде зараховано як помилкову}}%
\par\nopagebreak\vspace{0.35cm}\nopagebreak}
% клітинки для чернетки: рядки по 5 мм, сітка розтягується на вільне місце сторінки (\flushbottom + \cleaders)
\newsavebox{\nmtRowBox}
\newif\ifnmtRowReady
\newcommand{\nmtEnsureRow}{\ifnmtRowReady\else\global\nmtRowReadytrue
  \pgfmathtruncatemacro{\nmtCols}{(\textwidth-\nmtIndent)/14.22638}%
  \pgfmathtruncatemacro{\nmtColsM}{\nmtCols-1}%
  \global\setbox\nmtRowBox=\hbox{\begin{tikzpicture}[x=5mm, y=5mm]
    \useasboundingbox (0,0) rectangle (\nmtCols,1);
    \draw[gray!32, line width=0.3pt] (0,0) -- (\nmtCols,0) (0,1) -- (\nmtCols,1);
    \foreach \k in {1,...,\nmtColsM} \draw[gray!32, line width=0.3pt] (\k,0) -- (\k,1);
    \draw[gray!60, line width=0.45pt] (0,0) -- (0,1) (\nmtCols,0) -- (\nmtCols,1);
  \end{tikzpicture}}\fi}
\newcommand{\nmtGridFill}[1]{\par\nopagebreak\nmtEnsureRow
  \cleaders\vbox to 5mm{\vss\hbox{\hskip\nmtIndent\copy\nmtRowBox}}\vskip #1 plus 1fill\relax}
% поле відповіді під чернеткою (завдання 19--22)
\renewcommand{\nmtAnswerBox}{}
\newcommand{\nmtAnswerLine}{\par\nopagebreak\vspace{0.25cm}\noindent\hspace*{\nmtIndent}Відповідь:\ \
\begin{tabular}{@{}*{5}{|>{\centering\arraybackslash}p{0.8cm}}|@{\hspace{0.1cm}\textbf{,}\hspace{0.1cm}}*{3}{|>{\centering\arraybackslash}p{0.8cm}}|@{}}
\hline
\rule[-0.2cm]{0pt}{0.7cm} & & & & & & & \\
\hline
\end{tabular}\par}
% ===================== кінець теми «як справжній НМТ» =====================
"""


def _міністорінки(блок):
    """minipage[c] -> [t]: номер завдання на полі стоїть біля першого рядка умови, а не посередині; рисунок -- від верху"""
    def заміна(m):
        хвіст = блок[m.end():m.end() + 40]
        if re.match(r"\s*(?:\\raggedright\s*)?\\zadnum", хвіст):
            return "\\begin{minipage}[t]{%s}" % m.group(1)
        return "\\begin{minipage}[t]{%s}\\vspace{0pt}" % m.group(1)
    return re.sub(r"\\begin\{minipage\}\[c\]\{([^{}]*)\}", заміна, блок)


def застосувати(tex, назва, завдання, перша_сторінка=1):
    """tex від пробний.документ(): тема в преамбулу; кожне завдання (samepage) -> номер на полі + чернетка (+ поле відповіді);
    заголовок прибрано (його роль -- титулка), нумерація сторінок продовжує титулку й довідкові"""
    assert tex.count("\\begin{document}") == 1
    tex = tex.replace("\\begin{document}", ПРЕАМБУЛА + "\\begin{document}", 1)
    частини = re.split(r"\\begin\{samepage\}\n(.*?)\n\\end\{samepage\}\n", tex, flags=re.S)
    assert len(частини) == 2 * 22 + 1, len(частини)
    out = [частини[0]]
    for i, z in enumerate(завдання):
        блок, тип = частини[2 * i + 1], z["тип"]
        блок = _міністорінки(re.sub(r"[ \t]*\\nmtAnswerBox[ \t]*\n?", "", блок))
        блок = re.sub(r"\b(?:blue|red|green|orange|cyan|magenta|violet|teal|purple|brown|yellow)!(\d+)", r"black!\1", блок)   # заливки -- сірі
        out.append("\\par\\noindent\\begin{minipage}{\\linewidth}\n\\begin{nmtTaskBody}\n%s\n\\end{nmtTaskBody}\n\\end{minipage}\n"
                   "\\nmtGridFill{%s}\n%s\\par\\penalty-200\\vspace{0.4cm}\n"
                   % (блок.strip(), ЧЕРНЕТКА[тип], "\\nmtAnswerLine\n" if тип == "input" else ""))
        out.append(частини[2 * i + 2])
    tex = "".join(out)
    старий = "\\chapterTitle{%s}\n" % назва
    assert старий in tex
    tex = tex.replace(старий, "\\setcounter{page}{%d}\n" % перша_сторінка, 1)
    return tex.replace("\\end{document}", "\\par\\vspace{0.5cm}\\begin{center}\\bfseries Кінець зошита\\end{center}\n\\end{document}", 1)


def бланк(номер):
    """бланк відповідей: 1--15 (клітинки А--Д), 16--18 (сітки 3 x 5), 19--22 (знак, цифри, кома)"""
    def блок_тест(a, b):
        рядки = []
        for k, n in enumerate(range(a, b + 1)):
            y = -(k + 1) * 0.75
            рядки.append(r"\node[anchor=east, font=\bfseries] at (-0.15,%.2f) {%d};" % (y, n))
            рядки.append(r"\foreach \i in {0,...,4} \draw[line width=0.5pt] (\i*0.75+0.06,%.2f) rectangle ++(0.6,0.6);" % (y - 0.3))
        return (r"\begin{tikzpicture}[baseline=(current bounding box.north)]"
                r"\foreach \L [count=\i from 0] in {А,Б,В,Г,Д} \node[font=\bfseries] at (\i*0.75+0.36,0) {\L};"
                + "".join(рядки) + r"\end{tikzpicture}")
    def блок_відп(n):
        рядки = [r"\node[font=\bfseries\large, anchor=east] at (-0.45,-1.24) {%d};" % n]
        for r in range(1, 4):
            y = -r * 0.62
            рядки.append(r"\node[anchor=east, font=\bfseries\small] at (0.05,%.2f) {%d};" % (y, r))
            рядки.append(r"\foreach \i in {0,...,4} \draw[line width=0.5pt] (\i*0.62+0.12,%.2f) rectangle ++(0.5,0.5);" % (y - 0.25))
        return (r"\begin{tikzpicture}[baseline=(current bounding box.north)]"
                r"\foreach \L [count=\i from 0] in {А,Б,В,Г,Д} \node[font=\bfseries\small] at (\i*0.62+0.37,0) {\L};"
                + "".join(рядки) + r"\end{tikzpicture}")
    def рядок_числа(n):
        return (r"\begin{tikzpicture}[baseline=-0.1cm]\node[font=\bfseries\large, anchor=east] at (-0.2,0) {%d};"
                r"\foreach \i in {0,...,6} \draw[line width=0.5pt] (\i*0.72,-0.36) rectangle ++(0.66,0.72);"
                r"\end{tikzpicture}" % n)
    return (
        "\\clearpage\n\\begin{center}{\\bfseries\\Large БЛАНК ВІДПОВІДЕЙ}\\\\[1mm]"
        "{\\small Пробний НМТ з математики · варіант %s · @pvtr2525}\\end{center}\n"
        "\\vspace{0.2cm}\\noindent Прізвище, ім'я:\\ \\rule[-1mm]{8.2cm}{0.4pt}\\hfill Дата:\\ \\rule[-1mm]{3cm}{0.4pt}\\par\\vspace{0.55cm}\n"
        "\\noindent\\fbox{\\parbox{\\dimexpr\\linewidth-2\\fboxsep-2\\fboxrule}{\\small Позначайте відповідь хрестиком так: "
        "\\tikz[baseline=-0.6ex]{\\draw[line width=0.5pt] (0,-0.21) rectangle ++(0.42,0.42); \\draw[line width=0.9pt] (0.07,-0.14) -- (0.35,0.14) (0.07,0.14) -- (0.35,-0.14);}. "
        "Щоб виправити відповідь, повністю зафарбуйте неправильну позначку й поставте нову. Числові відповіді записуйте "
        "чітко, по одній цифрі в клітинці; кому й знак «мінус» -- в окремих клітинках.}}\\par\\vspace{0.6cm}\n"
        "\\noindent{\\bfseries Завдання 1--15}\\par\\vspace{0.35cm}\n"
        "\\noindent\\hspace*{0.6cm}%s\\hfill%s\\hfill%s\\hspace*{0.6cm}\\par\\vspace{0.8cm}\n"
        "\\noindent{\\bfseries Завдання 16--18}\\par\\vspace{0.35cm}\n"
        "\\noindent\\hspace*{1.1cm}%s\\hfill%s\\hfill%s\\hspace*{0.6cm}\\par\\vspace{0.8cm}\n"
        "\\noindent{\\bfseries Завдання 19--22}\\par\\vspace{0.4cm}\n"
        "\\noindent\\hspace*{0.9cm}%s\\hfill%s\\hspace*{0.6cm}\\par\\vspace{0.55cm}\n"
        "\\noindent\\hspace*{0.9cm}%s\\hfill%s\\hspace*{0.6cm}\\par\n"
        % (номер, блок_тест(1, 5), блок_тест(6, 10), блок_тест(11, 15), блок_відп(16), блок_відп(17), блок_відп(18),
           рядок_числа(19), рядок_числа(20), рядок_числа(21), рядок_числа(22)))


def ключ(завдання):
    """ключ відповідей: таблиці, як в офіційних ключах; оцінювання"""
    в = {z["номер"]: z["відповідь"] for z in завдання}
    num = lambda n: re.sub(r"[.,]", "{,}", str(в[n]))
    т1 = (" & ".join("\\textbf{%d}" % n for n in range(1, 16)) + " \\\\\\hline\n"
          + " & ".join(str(в[n]) for n in range(1, 16)) + " \\\\\\hline\n")
    т2 = "\n".join("\\textbf{%d} & %s \\\\\\hline" % (n, ", ".join("%d~--~%s" % (i + 1, x) for i, x in enumerate(в[n]))) for n in (16, 17, 18))
    т3 = "\n".join("\\textbf{%d} & $%s$ \\\\\\hline" % (n, num(n)) for n in (19, 20, 21, 22))
    return ("\\clearpage\n\\begin{center}{\\bfseries\\Large КЛЮЧ ВІДПОВІДЕЙ}\\end{center}\\vspace{0.3cm}\n"
            "\\noindent{\\bfseries Завдання 1--15} (1 бал за правильну відповідь)\\par\\vspace{0.25cm}\n"
            "\\noindent{\\renewcommand{\\arraystretch}{1.5}\\setlength{\\tabcolsep}{0pt}"
            "\\begin{tabular}{|*{15}{>{\\centering\\arraybackslash}p{\\dimexpr(\\linewidth-16\\arrayrulewidth)/15\\relax}|}}\\hline\n"
            + т1 + "\\end{tabular}}\\par\\vspace{0.6cm}\n"
            "\\noindent{\\bfseries Завдання 16--18} (1 бал за кожну правильно встановлену відповідність, до 3 балів)\\par\\vspace{0.25cm}\n"
            "\\noindent{\\renewcommand{\\arraystretch}{1.5}\\begin{tabular}{|>{\\centering\\arraybackslash}p{1.2cm}|p{6cm}|}\\hline\n"
            + т2 + "\n\\end{tabular}}\\par\\vspace{0.6cm}\n"
            "\\noindent{\\bfseries Завдання 19--22} (2 бали за правильну відповідь)\\par\\vspace{0.25cm}\n"
            "\\noindent{\\renewcommand{\\arraystretch}{1.5}\\begin{tabular}{|>{\\centering\\arraybackslash}p{1.2cm}|>{\\centering\\arraybackslash}p{3cm}|}\\hline\n"
            + т3 + "\n\\end{tabular}}\\par\\vspace{0.5cm}\n"
            "\\noindent Максимальна кількість балів~-- 32.\\par\n")


ТИТУЛКА = r"""\documentclass[12pt]{article}
\usepackage[ukrainian,shorthands=off]{babel}
\usepackage{fontspec}
\setmainfont{Schoolbook-Regular.otf}[Path=<<sb>>, BoldFont=Schoolbook-Bold.otf, ItalicFont=Schoolbook-Italic.otf,
  BoldItalicFont=Schoolbook-BoldItalic.otf]
\usepackage[a4paper, left=1.85cm, right=3.65cm, top=1.75cm, bottom=2.65cm]{geometry}
\usepackage{tikz, enumitem}
\pagestyle{empty}
\setlength{\parindent}{0pt}
\setlist[enumerate]{label=\textbf{\arabic*.}, leftmargin=0.75cm, itemsep=0.5pt, parsep=0pt, topsep=2pt}
\begin{document}
\begin{tikzpicture}[remember picture, overlay]
\draw[line width=0.7pt] ([xshift=1.45cm, yshift=-1.35cm]current page.north west) rectangle ([xshift=-3.25cm, yshift=2.25cm]current page.south east);
\node[draw, line width=0.7pt, minimum width=2.35cm, minimum height=2.45cm, align=center, inner sep=1pt, anchor=north west]
  at ([xshift=-3.0cm, yshift=-1.35cm]current page.north east) {{\bfseries\large Варіант}\\[-1mm]{\bfseries\fontsize{44}{48}\selectfont <<номер>>}};
\node[anchor=north east, font=\small] at ([xshift=-3.25cm, yshift=2.05cm]current page.south east)
  {© @pvtr2525, 2026 · авторський пробний тест, не є офіційним матеріалом};
\end{tikzpicture}%
{\small\bfseries ПРОБНИЙ ТЕСТ · @pvtr2525}\hfill{\bfseries\fontsize{22}{24}\selectfont 2026}\par\vspace{0.25cm}
\noindent\fbox{\parbox{\dimexpr\linewidth-2\fboxsep-2\fboxrule}{\centering\vspace{2.5mm}
{\bfseries\fontsize{17.5}{21}\selectfont ПРОБНИЙ НАЦІОНАЛЬНИЙ\\[0.5mm] МУЛЬТИПРЕДМЕТНИЙ ТЕСТ}\\[2.5mm]
{\bfseries\fontsize{23}{27}\selectfont З МАТЕМАТИКИ}\\[2mm]
{\large Авторський варіант \textnumero~<<номер>>}\vspace{2.5mm}}}\par\vspace{0.4cm}
Тест складається з 22 завдань трьох форм. Відповіді до всіх завдань Ви маєте позначити в \textbf{бланку відповідей}
(сторінка <<бланк>>).\par\vspace{0.15cm}
За виконання тесту можна одержати \textbf{32 тестові бали}: завдання 1--15~-- по 1 балу, 16--18~-- до 3 балів (по 1 балу за
кожну правильно встановлену відповідність), 19--22~-- по 2 бали.\par\vspace{0.45cm}
\begin{center}\bfseries Інструкція щодо роботи з тестом\end{center}\vspace{-0.25cm}
\begin{enumerate}
\item Правила виконання завдань зазначено перед кожною новою формою завдань.
\item Рисунки до завдань виконано схематично, без строгого дотримання пропорцій.
\item Відповідайте лише після того, як уважно прочитали й зрозуміли завдання. Використовуйте як чернетку клітинки під
завданнями та вільні від тексту місця в зошиті.
\item Намагайтеся виконати всі завдання.
\item Ви можете користуватися довідковими матеріалами на сторінках <<довідкові>>.
\end{enumerate}\vspace{0.2cm}
\begin{center}\bfseries Інструкція щодо заповнення бланка відповідей\end{center}\vspace{-0.25cm}
\begin{enumerate}
\item У бланк відповідей записуйте чітко, згідно з вимогами інструкції до кожної форми завдань, лише правильні, на Вашу
думку, відповіді.
\item У завданнях 1--15 позначте хрестиком одну клітинку в рядку завдання; у завданнях 16--18~-- по одній клітинці в кожному
з трьох рядків таблиці.
\item Якщо Ви позначили відповідь неправильно, повністю зафарбуйте неправильну позначку й поставте нову, як на зразку:\\[1mm]
\hspace*{1.2cm}<<зразок>>
\item Відповіді до завдань 19--22 записуйте десятковим дробом, по одній цифрі в кожній клітинці; кому й знак «мінус»~--
в окремих клітинках.
\item Неправильно позначені, підчищені чи виправлені не за зразком відповіді буде зараховано як помилкові.
\end{enumerate}
\vfill
\begin{center}\bfseries\large Зичимо Вам успіху!\end{center}
\end{document}
"""

ЗРАЗОК = (r"\begin{tikzpicture}[baseline=-0.1cm, x=0.6cm, y=0.6cm]"
          r"\foreach \L [count=\i from 0] in {А,Б,В,Г,Д} {\node[font=\bfseries\small] at (\i+0.5,0.75) {\L}; \draw[line width=0.5pt] (\i+0.12,-0.38) rectangle ++(0.76,0.76);}"
          r"\fill[black!85] (1.15,-0.35) rectangle ++(0.7,0.7);"
          r"\draw[line width=1pt] (3.25,-0.25) -- (3.75,0.25) (3.25,0.25) -- (3.75,-0.25);"
          r"\end{tikzpicture}")


def титулка_pdf(вихід, номер, довідкові="2--4", сторінка_бланка="?"):
    tmp = tempfile.mkdtemp(prefix="титулка_нмт_")
    tex = (ТИТУЛКА.replace("<<sb>>", ROOT + "/").replace("<<номер>>", str(номер)).replace("<<довідкові>>", довідкові)
           .replace("<<бланк>>", str(сторінка_бланка)).replace("<<зразок>>", ЗРАЗОК))
    open(os.path.join(tmp, "титулка.tex"), "w", encoding="utf-8").write(tex)
    for _ in range(2):
        r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "титулка.tex"], cwd=tmp, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-2500:]); raise SystemExit("титулка: помилка LaTeX")
    shutil.copy(os.path.join(tmp, "титулка.pdf"), вихід)
