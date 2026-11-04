# -*- coding: utf-8 -*-
"""Єдина розкладка завдання з рисунком (user, 4.11: «вигляд має бути монолітний для всього документу»).

Усі завдання з ОДНИМ рисунком (TikZ або растр) мають один з двох виглядів:
  * S (бічний): умова в лівій minipage 0,56, рисунок у правій 0,40 по центру, під ними -- решта (варіанти, відповідність, поле відповіді);
  * C (широкий): умова на всю ширину, під нею рисунок по центру, далі решта.
Вид визначає форма рисунка: широкий (ширина/висота > 2,2) -- C, інакше S. Завдання на відповідність: список (matchingLayout) завжди
під рисунком (колись у частини завдань рисунок стояв після списку чи в міністорінці поруч). Продовження пункту відповідності
(`\\quad\\quad ...` поза \\matchItem) зливається з пунктом.

Функція нормалізувати(блок) -> новий блок (або той самий, якщо розкладка не підходить: кілька рисунків, нетипова структура).
Інваріант (перевіряє перевірити_зміст): текст завдання без команд розкладки й без рисунків не змінюється."""
import re

ЛІВА, ПРАВА = "0.56", "0.40"
ШИРОКИЙ = 2.2

FIG = re.compile(r"(?:\\begin\{nmtfit\}(?:\[[^\]]*\])?\s*)?\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}(?:\s*\\end\{nmtfit\})?"
                 r"|\\includegraphics(?:\[[^\]]*\])?\{[^}]*\}(?:%@N[^\n]*)?", re.S)
РОЗМІТКА = re.compile(r"\\(?:begin|end)\{(?:minipage|center|flushright|flushleft|samepage)\}(?:\[[^\]]*\])?(?:\{[^}]*\})?|\\hfill|\\centering|\\noindent|"
                      r"\\nopagebreak|\\nmtnobreak|\\nbvspace\{[^}]*\}|\\vspace\*?\{[^}]*\}|\\par(?![a-zA-Z])|\\penalty-?\d+|\\raggedleft|\\raggedright|%[^\n]*")
КІНЕЦЬ_УМОВИ = re.compile(r"\\answerTable(?:Tall)?\s*\{|\\nmtAnswerBox|\\matchingLayout|\\matchHead|\\matchItem|\\answerListVertical|"
                          r"\\begin\{flushleft\}\s*\\textbf\{[А-Д]|\\begin\{tabular\}")
ДУЖКИ = re.compile(r"[{}]")


def _збалансовано(t, i):
    """індекс дужки '}', парної до '{' на позиції i"""
    г = 0
    for k in range(i, len(t)):
        if t[k] == "\\": continue
        if t[k] == "{": г += 1
        elif t[k] == "}":
            г -= 1
            if not г: return k
    return -1


def плоский(t):
    """зміст без розкладки й рисунків -- для перевірки інваріанта"""
    t = FIG.sub(" ", t)
    t = РОЗМІТКА.sub(" ", t)
    t = re.sub(r"\\(?:zadtask|zadnum|matchingGrid|matchingLayout)\b", " ", t)
    t = re.sub(r"\\quad", " ", t)
    return re.sub(r"[\s{}]+", "", t)


def перевірити_зміст(до, після):
    return плоский(до) == плоский(після)


def злити_продовження(b):
    """\\matchItem{N}{текст}\\n\\quad\\quad ... (поза пунктом) -> один пункт"""
    def фікс(b):
        m = re.search(r"(\\matchItem\{[^{}]*\}\{)", b)
        вихід, поз = [], 0
        for m in re.finditer(r"\\matchItem\{[^{}]*\}\{", b):
            if m.start() < поз: continue
            к = _збалансовано(b, m.end() - 1)
            if к < 0: continue
            кінець = к + 1
            додано = []
            while True:
                n = re.match(r"(?:\s|\\nmtnobreak)*\\quad\s*\\quad\s*([^\n]*)", b[кінець:])
                if not n: break
                додано.append(n.group(1).strip()); кінець += n.end()
            if додано:
                вихід.append(b[поз:к]); вихід.append(" " + " ".join(додано) + "}"); поз = кінець
        вихід.append(b[поз:]); return "".join(вихід)
    return фікс(b)


def _умова_і_решта(b):
    """b без рисунка й порожніх обгорток -> (умова, решта): умова -- від \\zadtask/\\zadnum до початку варіантів/списків"""
    m = re.search(r"\\zadtask\s*\{", b)
    if m:
        к = _збалансовано(b, m.end() - 1)
        умова = b[m.end():к]; решта = b[к + 1:]
        # продовження умови до першого маркера кінця (I/II/III у tabular лишаємо в решті)
        return "task", умова, решта
    m = re.search(r"\\zadnum\b", b)
    if not m: return None
    хвіст = b[m.end():]
    k = КІНЕЦЬ_УМОВИ.search(хвіст)
    кінець_мініпейджа = re.search(r"\\end\{minipage\}", хвіст)
    межа = len(хвіст)
    if k: межа = min(межа, k.start())
    if кінець_мініпейджа: межа = min(межа, кінець_мініпейджа.start())
    пуст = re.search(r"\n\s*\n", хвіст[:межа])
    if пуст: межа = min(межа, пуст.start())
    return "num", хвіст[:межа], b[:m.start()] + хвіст[межа:]


def _очистити_обгортки(t):
    """прибирає порожні обгортки й зайві \\hfill після вилучення рисунка"""
    for _ in range(6):
        н = re.sub(r"\\begin\{(center|flushright|flushleft)\}\s*\\end\{\1\}", " ", t)
        н = re.sub(r"\\begin\{minipage\}(?:\[[^\]]*\])?\{[^}]*\}\s*\\end\{minipage\}", " ", н)
        н = re.sub(r"\\hfill\s*(?=\\hfill|\\par|\\nmtnobreak|\\answerTable|\\matchingLayout|\n\n|$)", " ", н)
        if н == t: break
        t = н
    return t


def _пункти(b):
    """відповідність -> (заголовок1, [(мітка, текст)], заголовок2, [...]) із довільного (в т.ч. старого) розташування"""
    заг = re.findall(r"\\matchHead\{((?:[^{}]|\{[^{}]*\})*)\}", b)
    пункти = []
    for m in re.finditer(r"\\matchItem\{([^{}]*)\}\{", b):
        к = _збалансовано(b, m.end() - 1)
        пункти.append((m.group(1), b[m.end():к]))
    ліві = [p for p in пункти if re.fullmatch(r"\d", p[0])]
    праві = [p for p in пункти if not re.fullmatch(r"\d", p[0])]
    return заг, ліві, праві


def _список_відповідності(заг, ліві, праві):
    h1 = заг[0] if заг else "Відрізок"
    h2 = заг[1] if len(заг) > 1 else "Довжина відрізка"
    л = "\\matchHead{%s}\n" % h1 + "\n".join("\\matchItem{%s}{%s}" % p for p in ліві)
    п = "\\matchHead{%s}\n" % h2 + "\n".join("\\matchItem{%s}{%s}" % p for p in праві)
    return "\\matchingLayout{\n%s\n}{\n%s\n}{\n\\matchingGrid\n}" % (л, п)


ХВІСТ = re.compile(r"\s*(\\par\\penalty-20(?:\\vspace\{0\.25cm\})?)\s*$")
ОБГОРТКИ = re.compile(r"\\(?:begin|end)\{(?:minipage|center|flushright|flushleft)\}(?:\[[^\]]*\])?(?:\{[^}]*\})?|\\hfill|\\centering|\\noindent")
ПРОБІЛИ_ПЕРЕД = re.compile(r"^(?:\s|\\nmtnobreak|\\nopagebreak|\\nbvspace\{[^}]*\}|\\vspace\{[^}]*\}|\\par(?![a-zA-Z]))*")


def нормалізувати(b, аспект=None):
    """повертає (новий блок, вид 'S'|'C'|None); None -- не міняли (лише злито продовження пунктів)"""
    b2 = злити_продовження(b)
    фігури = list(FIG.finditer(b2))
    if len(фігури) != 1: return b2, None
    ф = фігури[0]; фігура = ф.group(0).strip()
    мм = re.search(r"%@N\s*([\d.]+)x([\d.]+)\s*([SC])", фігура)          # природний розмір і вид (пише дизайн_завдань)
    вид_з_маркера = мм.group(3) if мм else None
    голова = re.match(r"(\s*(?:%[^\n]*\n\s*)*)", b2).group(1)
    тіло = b2[len(голова):]
    ф = FIG.search(тіло)
    хв = ХВІСТ.search(тіло); хвіст = хв.group(1) if хв else ""
    if хв: тіло = тіло[:хв.start()]
    ф = FIG.search(тіло)
    без = _очистити_обгортки(тіло[:ф.start()] + " " + тіло[ф.end():])
    р = _умова_і_решта(без)
    if not р: return b2, None
    вид, умова, решта = р
    умова = ОБГОРТКИ.sub(" ", умова)
    умова = re.sub(r"\\(?:nopagebreak|nmtnobreak)\b|\\nbvspace\{[^}]*\}", " ", умова)
    умова = re.sub(r"[ \t]+", " ", умова).strip()
    решта = ОБГОРТКИ.sub(" ", решта)
    решта = ПРОБІЛИ_ПЕРЕД.sub("", решта).strip("\n ")
    if re.search(r"\\matchItem", решта):
        if "\\matchingLayout" not in решта:
            заг, ліві, праві = _пункти(решта)
            if len(ліві) < 2 or len(праві) < 2: return b2, None
            решта = _список_відповідності(заг, ліві, праві)
        else:
            решта = re.sub(r"\\hfill\s*(?=\\matchingGrid)", "", решта)
    if "\\begin{axis}" in фігура:
        широкий = True                                # діаграма pgfplots -- завжди широка, під умовою, єдиного розміру
    elif вид_з_маркера:
        широкий = вид_з_маркера == "C"
    elif аспект is None:
        до_фіг = тіло[:ф.start()]
        відкр = len(re.findall(r"\\begin\{minipage\}", до_фіг)) - len(re.findall(r"\\end\{minipage\}", до_фіг))
        широкий = відкр <= 0                          # без виміру: лишаємо поточний вид (в міністорінці -- бічний)
    else:
        широкий = аспект > ШИРОКИЙ
    фіг = ф.group(0).strip()
    if "\\includegraphics" not in фіг and "\\begin{nmtfit}" not in фіг: фіг = "\\begin{nmtfit}" + фіг + "\\end{nmtfit}"
    кінець = ("\n" + хвіст if хвіст else "")
    if широкий:
        нов = голова + "\\zadtask{%s}\n\\begin{center}\n%s\n\\end{center}\n\\nopagebreak\\nbvspace{0.2cm}\n%s" % (умова, фіг, решта)
        return нов.rstrip() + кінець + "\n", "C"
    нов = (голова + "\\noindent\n\\begin{minipage}[c]{%s\\textwidth}\n\\zadnum %s\n\\end{minipage}%%\n\\hfill\n"
           "\\begin{minipage}[c]{%s\\textwidth}\n\\centering\n%s\n\\end{minipage}\n\\par\\nbvspace{0.2cm}\n%s" % (ЛІВА, умова, ПРАВА, фіг, решта))
    return нов.rstrip() + кінець + "\n", "S"
