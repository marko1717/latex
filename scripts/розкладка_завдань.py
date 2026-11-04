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
КІНЕЦЬ_УМОВИ = re.compile(r"\\nmtOptions|\\answerTable(?:Tall)?\s*\{|\\nmtAnswerBox|\\matchingLayout|\\matchHead|\\matchItem|\\answerListVertical|"
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
    t = ДУБЛЬ_ВІДПОВІДІ.sub("", t)
    t = t.replace("\\nmtSetCell", "")
    t = re.sub(r"\\begin\{tabular\}\{\|\*\{5\}\{[^\n]*?\|\}\}", r"\\begin{tabular}", t)
    t = РОЗМІТКА.sub(" ", t)
    t = re.sub(r"\\(?:zadtask|zadnum|matchingGrid|matchingLayout|nmtOptions|nmtStmt)\b", " ", t)
    t = re.sub(r"\\quad", " ", t)
    return re.sub(r"[\s{}]+", "", t)


def _слова(t):
    """зміст без розмітки: лише літери, цифри й знаки (для рукописних відповідностей, де змінюються самі команди пунктів)"""
    t = FIG.sub(" ", t)
    t = re.sub(r"%[^\n]*", "", t)
    t = re.sub(r"\\begingroup.*?\\endgroup", " ", t, flags=re.S)
    t = re.sub(r"\\begin\{tabular\}\{@\{\}l@\{\\hspace\{1cm\}\}l@\{\}\}", " ", t)
    t = re.sub(r"\\(?:begin|end)\{[^}]*\}(?:\[[^\]]*\])?(?:\{[^}]*\})?", " ", t)
    t = re.sub(r"\\(?:mbox|nmtyear|nbvspace|vspace|penalty)(?:\{[^}]*\}|-?\d+)?", " ", t)
    t = re.sub(r"\\\\(?:\[[^\]]*\])?|\\[a-zA-Z]+\*?", " ", t)
    return re.sub(r"[\s{}&\[\]]+", "", t)


def _слова_тв(t):
    """зміст тверджень без розмітки: порівняння до/після єдині_твердження (мітки I., \\textbf{I}, \\item -- не зміст)"""
    t = плоский(t)
    t = re.sub(r"\\nmtStmt|\\textbf|\\makebox\[[^\]]*\]\[l\]|\\hangindent=[\d.]+em|\\noindent|\\hspace\{[^}]*\}|\\item|\\quad|\\,|\\\\|&", "", t)
    return re.sub(r"(?<![A-Za-z])I{1,3}\.?(?=[А-ЯІЇЄA-Z$\\])", "", t)


def перевірити_зміст(до, після):
    if плоский(єдині_варіанти(до)) == плоский(після) or плоский(до) == плоский(після): return True
    if _слова_тв(єдині_твердження(єдині_варіанти(до))) == _слова_тв(після): return True
    if "\\matchItem" in після and "\\matchItem" not in до: return sorted(_слова(до)) == sorted(_слова(після))      # пункти двох стовпчиків були чергувані по рядках
    return "Початок речення" in до and "\\cline{2-6}" in до and _слова(до) == _слова(після)


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


СПИСОК_ВІДПОВІДНОСТІ = re.compile(r"\\matchingLayout|\\matchHead|\\matchItem|\\nmtAnswerBox|\\nmtOptions|\\answerTable(?:Tall)?\s*\{")


def _умова_і_решта(b):
    """b без рисунка й порожніх обгорток -> (умова, решта): умова -- від \\zadtask/\\zadnum до початку варіантів/списків"""
    m = re.search(r"\\zadtask\s*\{", b)
    if m:
        к = _збалансовано(b, m.end() - 1)
        умова = b[m.end():к]; решта = b[к + 1:]
        # список відповідності / поле відповіді / варіанти, що опинилися в дужках умови, -- у «решту» (рисунок має стояти НАД ними)
        k = СПИСОК_ВІДПОВІДНОСТІ.search(умова)
        if k: решта = умова[k.start():] + решта; умова = умова[:k.start()]
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


def _без_пунктів(b):
    """решта після вилучення \\matchHead, \\matchItem і \\matchingGrid (коментар з відповіддю й \\solution лишаються)"""
    діапазони = []
    for m in re.finditer(r"\\matchItem\{[^{}]*\}\{|\\matchHead\{", b):
        к = _збалансовано(b, m.end() - 1)
        if к >= 0: діапазони.append((m.start(), к + 1))
    вихід, поз = [], 0
    for а, к in діапазони:
        if а < поз: continue
        вихід.append(b[поз:а]); поз = к
    вихід.append(b[поз:])
    t = re.sub(r"\\matchingGrid\b|\\hfill\b", " ", "".join(вихід))
    return _прибрати_порожнє(ПРОБІЛИ_ПЕРЕД.sub("", t))


def _список_відповідності(заг, ліві, праві):
    h1 = заг[0] if заг else "Відрізок"
    h2 = заг[1] if len(заг) > 1 else "Довжина відрізка"
    л = "\\matchHead{%s}\n" % h1 + "\n".join("\\matchItem{%s}{%s}" % p for p in ліві)
    п = "\\matchHead{%s}\n" % h2 + "\n".join("\\matchItem{%s}{%s}" % p for p in праві)
    return "\\matchingLayout{\n%s\n}{\n%s\n}{\n\\matchingGrid\n}" % (л, п)


ХВІСТ = re.compile(r"\s*(\\par\\penalty-20(?:\\vspace\{0\.25cm\})?)\s*$")
ОБГОРТКИ = re.compile(r"\\(?:begin|end)\{(?:minipage|center|flushright|flushleft)\}(?:\[[^\]]*\])?(?:\{[^}]*\})?%?|\\hfill|\\centering|\\noindent")
ВІДСТУП = re.compile(r"\\(?:par|nopagebreak)\\nbvspace\{0\.2cm\}")


ПРОБІЛИ_ПЕРЕД = re.compile(r"^(?:\s|\\nmtnobreak|\\nopagebreak|\\nbvspace\{[^}]*\}|\\vspace\{[^}]*\}|\\par(?![a-zA-Z]))*")


def _прибрати_порожнє(t):
    """рядки з одиноким % -- геть; послідовність порожніх рядків -- один порожній рядок"""
    t = re.sub(r"(?m)^[ \t]*%[ \t]*$\n?", "", t)
    t = re.sub(r"[ \t]*\n(?:[ \t]*\n)+", "\n\n", t)
    return t.strip("\n ")


ПОРОЖНІЙ_РИСУНОК = re.compile(r"(?:\\begin\{nmtfit\}\s*)?\\begin\{tikzpicture\}((?:(?!\\end\{tikzpicture\}).)*)\\end\{tikzpicture\}(?:\s*\\end\{nmtfit\})?", re.S)
МАЛЮЄ = re.compile(r"\\(?:draw|fill|filldraw|node|pic|shade|foreach|addplot|clip|coordinate)\b|\\includegraphics|\\begin\{axis\}")


ДУБЛЬ_ВІДПОВІДІ = re.compile(r"\\noindent\\textbf\{Відповідь:\s*\\underline\{\\hspace\{[^}]*\}\}\}[ \t]*\n?(?=\s*\\nmtAnswerBox)")


СПЕЦ_ТАБЛИЦІ_РИСУНКІВ = re.compile(r"\\begin\{tabular\}\{\|\*\{5\}\{(?:>\{[^}]*\})?(?:m\{[\d.]+cm\}|c)\|\}\}")


def таблиця_рисунків(b):
    """таблиця п'яти рисунків-варіантів А--Д: клітинки колись мали довільну ширину (2,2--3,2 см) -- тепер завжди на всю ширину рядка (m{\nmtcellw}, як у
    \nmtOptions), тож усі такі таблиці однакові"""
    def зам(m):
        після = b[m.end():m.end() + 6000].split("\\end{tabular}")[0]
        if "tikzpicture" not in після and "includegraphics" not in після: return m.group(0)
        return "\\nmtSetCell\n\\begin{tabular}{|*{5}{>{\\centering\\arraybackslash}m{\\nmtcellw}|}}"
    return СПЕЦ_ТАБЛИЦІ_РИСУНКІВ.sub(зам, b)


def без_порожніх_рисунків(b):
    """«рисунок» без жодної команди малювання (заглушка `\\path (0,0);` чи \\useasboundingbox) -- геть разом з обгорткою center
    (колись його масштабувало дизайн-система до 26 см² -- виходила величезна порожнеча між умовою й варіантами)"""
    n = ПОРОЖНІЙ_РИСУНОК.sub(lambda m: m.group(0) if МАЛЮЄ.search(m.group(1)) else "", b)
    if n != b:
        n = re.sub(r"\\begin\{center\}\s*\\end\{center\}", "", n)
        n = re.sub(r"%\s*Легенда під малюнком\s*\n", "", n)
    return n


def нормалізувати(b, аспект=None):
    """нерухома точка _раз: результат нормалізації сам є нормалізованим (збірка не залежить від кількості проходів)"""
    b = таблиця_рисунків(без_порожніх_рисунків(єдині_варіанти(єдині_твердження(ДУБЛЬ_ВІДПОВІДІ.sub("", b)))))
    n, v = _раз(b, аспект)
    for _ in range(3):
        n2, v2 = _раз(n, аспект)
        if n2 == n: break
        n, v = n2, v2 or v
    n2 = єдині_варіанти(n)
    if n2 != n: n, v = n2, v
    return n, v


def _раз(b, аспект=None):
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
    решта = ПРОБІЛИ_ПЕРЕД.sub("", ВІДСТУП.sub(" ", решта))
    решта = _прибрати_порожнє(решта)
    решта = _стара_відповідність(решта)
    умова = _прибрати_порожнє(умова) if "\n" in умова else умова
    # абзаци всередині умови не розривають сторінку (samepage не забороняє розрив між абзацами)
    умова = re.sub(r"\n[ \t]*\n+\s*(?=[^\s}])", lambda m: "\n\\par\n", умова)
    умова = re.sub(r"\\par\b(?!\\nmtnobreak)\s*(?=[^\s}])", lambda m: "\\par\\nmtnobreak ", умова)
    if re.search(r"\\matchItem", решта):
        if "\\matchingLayout" not in решта:
            заг, ліві, праві = _пункти(решта)
            if len(ліві) < 2 or len(праві) < 2: return b2, None
            залишок = _без_пунктів(решта)
            решта = _список_відповідності(заг, ліві, праві) + ("\n" + залишок if залишок else "")
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


# ------------------------------------------------------------------ єдині варіанти А--Д
# Різні форми запису п'яти варіантів (абзаци «\\textbf{А} \\quad ...», tabular{ll}, рукописна таблиця |*{5}{m{..}}|, \\answerListVertical)
# зводяться до \\nmtOptions{А}{Б}{В}{Г}{Д}; рядок-таблицю чи вертикальний список обирає TeX за виміром (див. nmtbase.sty).
ЛІТЕРИ = "АБВГД"
НЕ_ВАРІАНТИ = re.compile(r"\\matchItem|\\matchingLayout|\\matchHead|Початок речення|Закінчення речення|\\matchingGrid|\\begin\{axis\}")


def _дужки(t, i):
    """прочитати n груп {..} підряд з позиції i -> (список змістів, позиція після останньої) або None"""
    вих = []
    for _ in range(5):
        m = re.compile(r"\s*\{").match(t, i)
        if not m: return None
        к = _збалансовано(t, m.end() - 1)
        if к < 0: return None
        вих.append(t[m.end():к]); i = к + 1
    return вих, i


class НеВаріанти(Exception): pass


def _опції(частини):
    if any(re.search(r"\\(?:begin|end)\{(?:minipage|center|tikzpicture|samepage|nmtfit)\}|\\hfill|\\includegraphics", x) for x in частини): raise НеВаріанти()
    return "\\nmtOptions" + "".join("{%s}" % re.sub(r"\s+", " ", p.strip()) for p in частини)


def _варіанти_список_старий(b):
    m = re.search(r"\\answerListVertical", b)
    if not m: return b
    р = _дужки(b, m.end())
    if not р: return b
    return b[:m.start()] + _опції(р[0]) + b[р[1]:]


def _варіанти_абзаци(b):
    m = re.search(r"(?m)^[ \t]*\\textbf\{А\}\s*\\quad\s*", b)
    if not m: return b
    і, частини = m.start(), []
    for л in ЛІТЕРИ:
        mm = re.compile(r"[ \t]*\\textbf\{%s\}\s*\\quad\s*([^\n]*(?:\n(?![ \t]*\n)[^\n]*)*)" % л).match(b, і)
        if not mm: return b
        текст, кін_абзацу = mm.group(1), mm.end()
        if л == "Д":
            т = КІНЕЦЬ_ОСТАННЬОГО.search(текст)
            if т: текст, кін_абзацу = текст[:т.start()], mm.start(1) + т.start()
        частини.append(текст); і = кін_абзацу
        пр = re.compile(r"(?:[ \t]*\n)+").match(b, і)
        if пр: і = пр.end()
    хв = re.compile(r"(?:\s|\\nmtnobreak|\\nopagebreak|\\nbvspace\{[^}]*\})*").match(b, і)
    return b[:m.start()] + _опції(частини) + "\n" + b[хв.end():]


def _рядки_таблиці(тіло):
    """тіло tabular -> список рядків (розбиття по \\\\ на верхньому рівні дужок)"""
    рядки, гл, початок = [], 0, 0
    i = 0
    while i < len(тіло):
        c = тіло[i]
        if c == "\\":
            if тіло.startswith("\\\\", i) and гл == 0:
                рядки.append(тіло[початок:i]); i += 2
                m = re.compile(r"\[[^\]]*\]").match(тіло, i)
                if m: i = m.end()
                початок = i; continue
            i += 2; continue
        if c == "{": гл += 1
        elif c == "}": гл -= 1
        i += 1
    рядки.append(тіло[початок:])
    return [r.strip() for r in рядки if r.strip()]


def _клітинки(рядок):
    """розбиття рядка на клітинки по & на верхньому рівні дужок"""
    вих, гл, п = [], 0, 0
    for i, c in enumerate(рядок):
        if c == "\\": continue
        if c == "{": гл += 1
        elif c == "}": гл -= 1
        elif c == "&" and гл == 0 and (i == 0 or рядок[i - 1] != "\\"):
            вих.append(рядок[п:i]); п = i + 1
    вих.append(рядок[п:])
    return [x.strip() for x in вих]


def _варіанти_таблиця_ll(b):
    for m in re.finditer(r"\\begin\{tabular\}\{ll\}(.*?)\\end\{tabular\}", b, re.S):
        рядки = _рядки_таблиці(re.sub(r"(?m)^[ \t]*%[^\n]*$", "", m.group(1)))
        if len(рядки) != 5: continue
        частини, ok = [], True
        for л, р in zip(ЛІТЕРИ, рядки):
            кл = _клітинки(р)
            if len(кл) != 2 or кл[0] != "\\textbf{%s}" % л or "\\begin" in кл[1]: ok = False; break
            частини.append(кл[1])
        if ok: return b[:m.start()] + _опції(частини) + b[m.end():]
    return b


def _варіанти_таблиця_рядок(b):
    """рукописна таблиця |*{5}{m{..}|}| із заголовком А--Д і одним рядком текстових варіантів"""
    for m in re.finditer(r"\\begin\{tabular\}\{\|\*\{5\}\{[^\n]*?\}\|\}\}?\s*\\hline(.*?)\\end\{tabular\}", b, re.S):
        тіло = m.group(1)
        if "tikzpicture" in тіло or "includegraphics" in тіло or "\\mini" in тіло: continue
        рядки = _рядки_таблиці(re.sub(r"\\hline|\\rule\[[^\]]*\]\{[^}]*\}\{[^}]*\}|(?m)^[ \t]*%[^\n]*$", "", тіло))
        if len(рядки) != 2: continue
        голова, дані = _клітинки(рядки[0]), _клітинки(рядки[1])
        if голова != ["\\textbf{%s}" % л for л in ЛІТЕРИ] or len(дані) != 5: continue
        return b[:m.start()] + _опції(дані) + b[m.end():]
    return b


РОЗДІЛЬНИКИ_КІНЕЦЬ = re.compile(r"(?:\\qquad|\\quad|\\\\(?:\[[^\]]*\])?|\\par\b|\\nmtnobreak|\\hfill|\\noindent|~|\s)+$")
РОЗДІЛЬНИКИ_ПОЧАТОК = re.compile(r"^(?:\\ |\\quad|\\qquad|\\,|~|\\noindent|\\par\b|\\nmtnobreak|\s)+")
КІНЕЦЬ_ОСТАННЬОГО = re.compile(r"\n[ \t]*\n|\\end\{(?:flushleft|minipage|center|enumerate|itemize)\}|%|\\ifshowsolutions|\\par\\penalty|\\par\\nbvspace|"
                               r"\\nopagebreak|\\nmtnobreak\s*\n|\\nbvspace|\\vspace|\\begin\{(?:minipage|center|tikzpicture)\}|\\answerTable|\\nmtAnswerBox")


def _чистий(t):
    t = РОЗДІЛЬНИКИ_ПОЧАТОК.sub("", t)
    return РОЗДІЛЬНИКИ_КІНЕЦЬ.sub("", t)


def _варіанти_мітки(b):
    """\\textbf{А} ... \\textbf{Б} ... \\textbf{Д} ... підряд (вертикально, в рядок через \\qquad, у flushleft) -> \\nmtOptions"""
    for m in re.finditer(r"\\textbf\{А\}", b):
        поч = m.start(); к = m.end(); частини = []; мітки = [(m.start(), m.end())]
        ok = True
        for л in ЛІТЕРИ[1:]:
            n = re.compile(r"\\textbf\{%s\}" % л).search(b, к)
            if not n: ok = False; break
            частини.append(b[к:n.start()]); к = n.end(); мітки.append((n.start(), n.end()))
        if not ok: continue
        кін = КІНЕЦЬ_ОСТАННЬОГО.search(b, к)
        кінець = кін.start() if кін else len(b)
        частини.append(b[к:кінець])
        частини = [_чистий(x) for x in частини]
        if any(not x or re.search(r"\\(?:begin|end)\{(?:minipage|center|tikzpicture|tabular|flushleft)\}|\\textbf\{[АБВГД]\}|&|\\hline|nmtfit|\\rule|\\includegraphics", x) for x in частини): continue
        if any(len(x) > 400 for x in частини): continue
        # обгортка flushleft навколо
        поч2, кін2 = поч, кінець
        пер = re.search(r"\\begin\{flushleft\}\s*$", b[:поч])
        if пер: поч2 = пер.start()
        пот = re.compile(r"\s*\\end\{flushleft\}").match(b, кінець)
        if пот: кін2 = пот.end()
        elif пер: continue
        return b[:поч2] + _опції(частини) + "\n" + b[кін2:]
    return b


def _варіанти_enumerate(b):
    m = re.search(r"\\begin\{enumerate\}\[label=\\textbf\{\\Alph\*\}[^\]]*\]", b)
    if not m: return b
    к = b.find("\\end{enumerate}", m.end())
    if к < 0: return b
    пункти = re.split(r"\\item\b", b[m.end():к])[1:]
    пункти = [x.strip() for x in пункти]
    if len(пункти) != 5 or any(not x for x in пункти): return b
    return b[:m.start()] + _опції(пункти) + b[к + len("\\end{enumerate}"):]


def _відповідність_таблицею(b):
    """відповідність у tabular{@{}l@{\hspace{1cm}}l@{}}: «\textit{Заголовок} & \textit{Заголовок}», рядки «\textbf{1} \quad … & \textbf{А} \quad …», продовження «\quad\quad …»,
    сітка окремо -> \matchingLayout"""
    m = re.search(r"\\begin\{tabular\}\{@\{\}l@\{\\hspace\{1cm\}\}l@\{\}\}(.*?)\\end\{tabular\}", b, re.S)
    if not m or "\\matchItem" in b: return b
    рядки = _рядки_таблиці(m.group(1))
    if len(рядки) < 3: return b
    гол = [re.fullmatch(r"\\textit\{(.*)\}", c.strip(), re.S) for c in _клітинки(рядки[0])]
    if len(гол) != 2 or not all(гол): return b
    ліві, праві = [], []
    for р in рядки[1:]:
        кл = _клітинки(р); л = кл[0]; п = кл[1] if len(кл) > 1 else ""
        ml = re.fullmatch(r"\\textbf\{(\d)\}\s*\\quad\s*(.*)", л, re.S)
        if ml: ліві.append([ml.group(1), ml.group(2).strip()])
        elif re.match(r"\\quad\s*\\quad", л) and ліві: ліві[-1][1] += " " + re.sub(r"^(?:\\quad\s*)+", "", л).strip()
        elif л.strip(): return b
        mr = re.fullmatch(r"\\textbf\{([А-Д])\}\s*\\quad\s*(.*)", п.strip(), re.S)
        if mr: праві.append([mr.group(1), mr.group(2).strip()])
        elif п.strip(): return b
    if len(ліві) < 2 or len(праві) != 5: return b
    нова = _список_відповідності([гол[0].group(1), гол[1].group(1)], [tuple(x) for x in ліві], [tuple(x) for x in праві])
    після = re.compile(r"(?:\s|\\nopagebreak|\\nbvspace\{[^}]*\})*\\matchingGrid(?:\s|\\nbvspace\{[^}]*\})*").match(b, m.end())
    кінець = після.end() if після else m.end()
    return b[:m.start()] + нова + "\n" + b[кінець:]


def _стара_відповідність(b):
    """рукописна відповідність «\\textit{Початок речення} / \\textbf{1} \\quad ... / tabular{ll} А--Д / ручна сітка» -> \\matchingLayout"""
    b = _відповідність_таблицею(b)
    if "\\matchItem" in b or "\\textit{Початок речення}" not in b or "\\cline{2-6}" not in b: return b
    а = b.index("\\textit{Початок речення}")
    в = ХВІСТ.search(b)
    кінець = в.start() if в else len(b)
    ділянка = b[а:кінець]
    л = re.search(r"\\textit\{Початок речення\}(.*?)\\textit\{Закінчення речення\}(.*)", ділянка, re.S)
    if not л: return b
    пункти = re.findall(r"\\textbf\{([123])\}\s*\\quad\s*([^\n]*?)\s*(?:\\\\(?:\[[^\]]*\])?)?\s*(?:\n|$)", л.group(1))
    таб = re.search(r"\\begin\{tabular\}\{ll\}(.*?)\\end\{tabular\}", л.group(2), re.S)
    if len(пункти) < 2 or not таб: return b
    рядки = _рядки_таблиці(таб.group(1))
    варіанти = []
    for літ, р in zip(ЛІТЕРИ, рядки):
        кл = _клітинки(р)
        if len(кл) != 2 or кл[0] != "\\textbf{%s}" % літ: return b
        варіанти.append((літ, кл[1]))
    if len(варіанти) != 5: return b
    ліва = "\\matchHead{Початок речення}\n" + "\n".join("\\matchItem{%s}{%s}" % п for п in пункти)
    права = "\\matchHead{Закінчення речення}\n" + "\n".join("\\matchItem{%s}{%s}" % п for п in варіанти)
    нова = "\\matchingLayout{\n%s\n}{\n%s\n}{\n\\matchingGrid\n}\n" % (ліва, права)
    # коментарі-«блоки» перед текстом теж геть
    початок = re.sub(r"%\s*---[^\n]*---\s*$", "", b[:а].rstrip()) 
    return початок + "\n" + нова + b[кінець:]


def _без_сміття_перед_варіантами(b):
    return re.sub(r"(?:\s|\\nmtnobreak|\\nopagebreak|\\nbvspace\{[^}]*\})+(?=\\nmtOptions)", "\n", b)


def єдині_варіанти(b):
    """див. вище; блоки з відповідністю не чіпаємо"""
    if НЕ_ВАРІАНТИ.search(b): return b
    for f in (_варіанти_список_старий, _варіанти_enumerate, _варіанти_абзаци, _варіанти_таблиця_ll, _варіанти_таблиця_рядок, _варіанти_мітки):
        try: b = f(b)
        except НеВаріанти: pass
    return _без_сміття_перед_варіантами(b)


# ------------------------------------------------------------------ єдині твердження I--III
# Списки тверджень «Які з тверджень правильні? I. … II. … III. …» писали сімома способами (tabular{rl} з ручними \\, enumerate з \Roman*, \hangindent,
# \makebox, рядки «I. \quad …»): у частині виходили за поле чи налазили на таблицю. Усе зводиться до \nmtStmt{I}{текст}\nmtStmt{II}{…}\nmtStmt{III}{…}
# (мітка в колонці сталої ширини, текст у parbox -- продовження вирівняне під текстом).
РИМСЬКІ = ["I", "II", "III", "IV"]
МІТКА_ТВ = r"(?:\\textbf\{{{n}\.?\}}|\\makebox\[[^\]]*\]\[l\]\{{\\textbf\{{{n}\}}\}}|{n}\.)"
РОЗДІЛ_МІТКИ = r"(?:\\ |\\quad|\\qquad|\\hspace\{{[^}}]*\}}|\\,|~|&|\s)*"
ПОЧАТОК_РЯДКА = r"(?:(?<=\n)|(?<=\\\\)|(?<=\\par)|(?<=\A))[ \t]*(?:\\noindent\s*)?(?:\\hspace\{[^}]*\}\s*)?(?:\\hangindent=[\d.]+em\s*)?"
ТЕРМІНАТОР_ТВ = re.compile(r"\n[ \t]*\n|\\end\{(?:enumerate|tabular|flushleft|minipage|center)\}|%|\\ifshowsolutions|\\par\\penalty|"
                           r"\\nbvspace|\\nopagebreak|\\nmtnobreak|\\vspace|\\answerTable|\\nmtOptions|\\nmtAnswerBox|\\noindent\s*Які|\\par\s*\\noindent\s*Які")


МІЖ_ТВЕРДЖЕННЯМИ = re.compile(r"\n[ \t]*\n|\\end\{(?:enumerate|tabular|flushleft|minipage|center)\}|%|\\ifshowsolutions|\\answerTable|\\nmtOptions|\\nmtAnswerBox")


def _таблиця_rl_у_рядки(b):
    """tabular{rl}, де рядки «I. & текст \\\\ & продовження \\\\ II. & …» -> звичайні рядки «I. текст продовження»"""
    def зам(m):
        рядки = _рядки_таблиці(re.sub(r"(?m)^[ \t]*%[^\n]*$", "", m.group(1)))
        вих = []
        for р in рядки:
            кл = _клітинки(р)
            if len(кл) != 2: return m.group(0)
            if кл[0].strip():
                if not re.fullmatch(r"(?:I{1,3}|IV)\.?", кл[0].strip()): return m.group(0)
                вих.append(кл[0].strip().rstrip(".") + ". " + кл[1].strip())
            elif вих: вих[-1] += " " + кл[1].strip()
            else: return m.group(0)
        return "\n".join(вих) + "\n"
    return re.sub(r"\\begin\{tabular\}\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}(.*?)\\end\{tabular\}", зам, b, flags=re.S)


def _твердження_enumerate(b):
    m = re.search(r"\\begin\{enumerate\}\[label=(?:\\textbf\{\\Roman\*\.?\}|\\Roman\*\.?)[^\]]*\]", b)
    if not m: return b
    к = b.find("\\end{enumerate}", m.end())
    if к < 0: return b
    пункти = [x.strip() for x in re.split(r"\\item\b", b[m.end():к])[1:]]
    if not 2 <= len(пункти) <= 4 or any(not x for x in пункти): return b
    нова = "\n".join("\\nmtStmt{%s}{%s}" % (РИМСЬКІ[i], re.sub(r"\s+", " ", x)) for i, x in enumerate(пункти))
    return b[:m.start()] + нова + b[к + len("\\end{enumerate}"):]


def _тверд_текст(t):
    t = re.sub(r"\s*(?:\\\\(?:\[[^\]]*\])?|\\par\b|\\nmtnobreak|\\nopagebreak|\\nbvspace\{[^}]*\}|\\vspace\{[^}]*\})*\s*$", "", t)
    return re.sub(r"\s+", " ", t).strip()


def _твердження_мітки(b):
    b = _таблиця_rl_у_рядки(b)
    for m in re.finditer(ПОЧАТОК_РЯДКА + МІТКА_ТВ.format(n="I") + РОЗДІЛ_МІТКИ, b):
        поч = m.start(); тексти = []; к = m.end(); ok = True; позиції = [m.end()]
        n = 1
        while True:
            наст = РИМСЬКІ[n] if n < 4 else None
            mm = re.compile(ПОЧАТОК_РЯДКА + МІТКА_ТВ.format(n=наст) + РОЗДІЛ_МІТКИ).search(b, позиції[-1]) if наст else None
            if mm and МІЖ_ТВЕРДЖЕННЯМИ.search(b, позиції[-1], mm.start()) is None:
                тексти.append(b[позиції[-1]:mm.start()]); позиції.append(mm.end()); n += 1
            else: break
        if n < 2: continue
        # кінець останнього: термінатор або незбалансована "}" (закриття \zadtask)
        ост = позиції[-1]; кін = ТЕРМІНАТОР_ТВ.search(b, ост); межа = кін.start() if кін else len(b)
        гл = 0; кінець = межа
        for i in range(ост, межа):
            if b[i] == "\\": continue
            if b[i] == "{": гл += 1
            elif b[i] == "}":
                if гл == 0: кінець = i; break
                гл -= 1
        тексти.append(b[ост:кінець])
        тексти = [_тверд_текст(x) for x in тексти]
        if any(not x or re.search(r"\\(?:begin|end)\{(?:minipage|center|tikzpicture|tabular)\}|\\textbf\{I{1,3}\}", x) for x in тексти): continue
        if any(len(x) > 500 for x in тексти): continue
        нова = "\n".join("\\nmtStmt{%s}{%s}" % (РИМСЬКІ[i], x) for i, x in enumerate(тексти)) + "\n"
        return b[:поч] + нова + b[кінець:]
    return b


def _збалансовані_середовища(t):
    return all(len(re.findall(r"\\begin\{%s\}" % e, t)) == len(re.findall(r"\\end\{%s\}" % e, t)) for e in ("tabular", "minipage", "center", "enumerate", "flushleft"))


def єдині_твердження(b):
    if "лише I" not in b and "I, II" not in b and "I та" not in b: return b
    n = _твердження_enumerate(b)
    if n == b: n = _твердження_мітки(b)
    return n if _збалансовані_середовища(n) or not _збалансовані_середовища(b) else b
