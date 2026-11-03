# -*- coding: utf-8 -*-
"""Дизайн-система завдань бази (правила -- scripts/ПРАВИЛА_ОФОРМЛЕННЯ.md): стилі TikZ для преамбули та нормалізатор,
який будівник (build_nmt_2023_2026.py) застосовує до кожного завдання, щоб рисунки, графіки й вирази з різних джерел
мали один вигляд, як у зошитах НМТ: чорні лінії однакової товщини, однакові точки й підписи, одна сітка, одна крива,
палітра заливок і ліній замість довільних кольорів; tg, \\dfrac, \\leqslant, десяткова кома {,}, градуси ^\\circ.

    import дизайн_завдань as D
    PREAMBLE += D.СТИЛІ
    c = D.уніфікувати(c)                      # у конвеєрі будівника, для кожного завдання

    python3 scripts/дизайн_завдань.py         # перевірка бази: що нормалізатор не зміг привести до правил
"""
import os, re, sys, json, hashlib, collections, subprocess, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
РОЗМІРИ_JSON = os.path.join(HERE, "data", "дизайн_розміри.json")        # виміряні рисунки: ключ -> {w, h} у см
НА_ВИМІР_JSON = os.path.join(HERE, "data", "дизайн_на_вимір.json")      # ще не виміряні (пише будівник)
# розміри (правила, розділ «Розмір рисунка»): окремий рисунок, рисунки-варіанти в таблиці, «смуга» (числова пряма)
ОКРЕМИЙ_H, ОКРЕМИЙ_W = (3.4, 5.6, 4.0), 8.5           # висота: мін, макс, ціль; ширина: макс
ВАРІАНТ_H, ВАРІАНТ_W = (1.9, 3.0, 2.4), 3.4
СМУГА_W = (5.5, 10.0, 7.0)

# ---------------------------------------------------------------- стилі (у преамбулу)
СТИЛІ = r"""
% ===================== ДИЗАЙН-СИСТЕМА РИСУНКІВ (scripts/ПРАВИЛА_ОФОРМЛЕННЯ.md, scripts/дизайн_завдань.py) =====================
\definecolor{nmtInk}{HTML}{1A1A1A}
\definecolor{nmtGrid}{HTML}{B8B8B8}
\definecolor{nmtBlue}{HTML}{1F6FB2}\definecolor{nmtGreen}{HTML}{2E8B57}\definecolor{nmtRed}{HTML}{C0392B}
\definecolor{nmtOrange}{HTML}{D9822B}\definecolor{nmtViolet}{HTML}{7D4CA8}
\definecolor{nmtFillA}{HTML}{D3E5F5}\definecolor{nmtFillB}{HTML}{D8EDD5}\definecolor{nmtFillC}{HTML}{FBE1C8}
\definecolor{nmtFillD}{HTML}{E4E4E4}\definecolor{nmtFillE}{HTML}{E7DCF2}
\tikzset{
  ultra thin/.style={line width=0.2pt}, very thin/.style={line width=0.3pt}, thin/.style={line width=0.45pt},
  semithick/.style={line width=0.6pt}, thick/.style={line width=0.75pt}, very thick/.style={line width=1.1pt},
  ultra thick/.style={line width=1.5pt},
  >={Stealth[length=2.3mm, width=1.7mm]},
  every picture/.append style={line join=round, line cap=round},
  nmt dot/.style={circle, fill=nmtInk, draw=none, inner sep=0pt, minimum size=3.6pt},
  nmt open dot/.style={circle, fill=white, draw=nmtInk, line width=0.6pt, inner sep=0pt, minimum size=4.2pt},
  nmt grid/.style={draw=nmtGrid, line width=0.3pt},
  nmt curve/.style={line width=1.1pt},
}
% вирази: ≤ і ≥ -- похилі, як у НМТ (десяткову кому без пробілу вже дає mathastext)
\let\leq\leqslant \let\le\leqslant \let\geq\geqslant \let\ge\geqslant
\pgfplotsset{every axis/.append style={axis line style={line width=0.6pt}, tick style={line width=0.45pt},
  tick label style={font=\footnotesize}, label style={font=\small}, grid style={nmtGrid, line width=0.3pt}}}
% ===================== кінець дизайн-системи =====================
"""

# ---------------------------------------------------------------- кольори
КОЛІР = r"(?:mainGreen|yearOrange|headerblue|red|blue|green|gray|grey|black|white|cyan|magenta|orange|violet|brown|purple|teal|olive|yellow|lime|pink|lightgray|darkgray)(?:!-?[0-9.]+(?:![a-zA-Z]+(?:![0-9.]+)?)?)*"
КОЛІР_RE = re.compile(r"^" + КОЛІР + r"$")
РОДИНИ = [("Blue", "A", ("cyan", "blue", "teal", "headerblue")), ("Green", "B", ("green", "olive", "lime", "mainGreen")),
          ("Red", "C", ("red", "magenta", "pink")), ("Orange", "C", ("orange", "yellow", "brown", "yearOrange")),
          ("Violet", "E", ("violet", "purple"))]


def _родина(колір):
    """Blue/Green/... і літера заливки -- за першою кольоровою назвою специфікації; сірі/чорні/білі -- None"""
    for назва in re.findall(r"[A-Za-z]+", колір):
        for лінія, заливка, імена in РОДИНИ:
            if назва in імена: return лінія, заливка
        if назва in ("gray", "grey", "lightgray", "darkgray", "black", "white"): return None
    return None


def лінія_палітри(колір):
    р = _родина(колір)
    return "nmt" + р[0] if р else колір


def заливка_палітри(колір):
    if re.search(r"white", колір) and not re.search(r"[!]", колір): return колір
    р = _родина(колір)
    return "nmtFill" + р[1] if р else колір      # сірі тони не чіпаємо: gray!20 і gray!90 -- різні сектори діаграми


# ---------------------------------------------------------------- розбір
def _опції(s):
    """'a, b={x, y}, c' -> ['a', 'b={x, y}', 'c'] (коми всередині дужок не ділять)"""
    out, глиб, поточна = [], 0, ""
    for ch in s:
        if ch in "{(": глиб += 1
        elif ch in "})": глиб -= 1
        if ch == "," and глиб == 0:
            out.append(поточна.strip()); поточна = ""
        else:
            поточна += ch
    if поточна.strip(): out.append(поточна.strip())
    return out


def _масштаб(відкриття):
    m = re.search(r"(?<![a-z ])scale\s*=\s*([\d.]+)", відкриття)
    return float(m.group(1)) if m else 1.0


ЛІНІЇ = {"ultra thin", "very thin", "thin", "semithick", "thick", "very thick", "ultra thick"}
СТРІЛКИ = {"-latex": "->", "latex-": "<-", "latex-latex": "<->", "-stealth": "->", "stealth-": "<-", "stealth-stealth": "<->",
           "-Latex": "->", "-Stealth": "->", "-{Latex}": "->", "-{Stealth}": "->", "->>": "->", "-to": "->"}


def _стрілка(o):
    if o in СТРІЛКИ: return СТРІЛКИ[o]
    if re.fullmatch(r"-\{(Stealth|Latex|Triangle|To)(\[[^\]]*\])?\}", o): return "->"
    if re.fullmatch(r"\{(Stealth|Latex|Triangle|To)(\[[^\]]*\])?\}-", o): return "<-"
    if re.fullmatch(r"\{(Stealth|Latex)(\[[^\]]*\])?\}-\{(Stealth|Latex)(\[[^\]]*\])?\}", o): return "<->"
    return o


def _нові_опції(опції, команда, крива=False, сітка=False, кольорова_крива=False, палітра=True):
    out = []
    for o in опції:
        if re.fullmatch(r">\s*=\s*.+", o): continue                    # >=stealth / >=latex -- глобальний наконечник
        o = _стрілка(o)
        if сітка:
            if КОЛІР_RE.match(o) or o in ЛІНІЇ or re.match(r"(line width|draw|color)\s*=", o): continue
        elif крива:
            if o in ЛІНІЇ or re.match(r"line width\s*=", o): continue
            if (КОЛІР_RE.match(o) or re.match(r"(draw|color)\s*=", o)) and not кольорова_крива: continue
        m = re.match(r"(fill|draw|color|text|pattern color)\s*=\s*(.+)$", o)
        if not палітра:
            out.append(o); continue
        if m and КОЛІР_RE.match(m.group(2).strip()):
            к = m.group(2).strip()
            o = "%s=%s" % (m.group(1), заливка_палітри(к) if m.group(1) == "fill" else лінія_палітри(к))
        elif КОЛІР_RE.match(o):
            o = заливка_палітри(o) if команда == "fill" else лінія_палітри(o)
        out.append(o)
    if сітка: out.insert(0, "nmt grid")
    if крива: out.insert(0, "nmt curve")
    return out


# точка: (координата) circle (r) -- координата може мати вкладені дужки: ($(A)!0.5!(B)$)
КРУГ = re.compile(r"(\((?:[^()]|\((?:[^()]|\([^()]*\))*\))*\))\s*circle\s*(?:\(\s*([\d.]+)\s*(pt|mm|cm)?\s*\)|\[\s*radius\s*=\s*([\d.]+)\s*(pt|mm|cm)?\s*\])")


def _ефективний_pt(r, одиниця, масштаб):
    r = float(r)
    return r * масштаб * {"pt": 1, "mm": 2.845, "cm": 28.45, None: 28.45}[одиниця]


def _точки(команда, опції, тіло, масштаб):
    """статементи, що складаються лише з маленьких кругів (і вузлів) -> \\path з вузлами nmt dot / nmt open dot"""
    if команда not in ("fill", "filldraw", "draw"): return None
    залишок = КРУГ.sub("", тіло)
    залишок = re.sub(r"node\s*(\[[^\]]*\])?\s*(\([^()]*\))?\s*(at\s*\([^()]*\))?\s*\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}", "", залишок)
    if залишок.strip(): return None
    круги = list(КРУГ.finditer(тіло))
    if not круги: return None
    for m in круги:
        r, u = (m.group(2), m.group(3)) if m.group(2) else (m.group(4), m.group(5))
        if _ефективний_pt(r, u, масштаб) > 4.6: return None
    біла = any(re.fullmatch(r"fill\s*=\s*white", o) for o in опції) or (команда == "draw" and not any(o.startswith("fill") for o in опції))
    стиль = "nmt open dot" if біла else "nmt dot"
    return "\\path " + КРУГ.sub(lambda m: "%s node[%s] {}" % (m.group(1), стиль), тіло).lstrip()


СТАТЕМЕНТ = re.compile(r"\\(filldraw|shadedraw|draw|fill|path|shade|clip|node|addplot\+?)(?![A-Za-z])\s*(\[((?:[^\[\]]|\[[^\[\]]*\])*)\])?")


def _статементи(картинка, масштаб, звіт, палітра=True):
    """кожен \\draw / \\fill / \\addplot ...; -- опції за правилами, маленькі круги -> точки"""
    кривих = len(re.findall(r"\\addplot|\\draw[^;]*\bplot\b", картинка))
    out, i = [], 0
    for m in СТАТЕМЕНТ.finditer(картинка):
        if m.start() < i: continue
        # кінець статементу -- перша «;» поза дужками
        j, глиб = m.end(), 0
        while j < len(картинка):
            ch = картинка[j]
            if ch in "{([": глиб += 1
            elif ch in "})]": глиб -= 1
            elif ch == ";" and глиб <= 0: break
            j += 1
        тіло = картинка[m.end():j]
        команда = m.group(1).rstrip("+")
        опції = _опції(m.group(3) or "")
        сітка = bool(re.search(r"\bgrid\b", тіло)) and команда in ("draw", "path")
        крива = (команда == "addplot" or (команда == "draw" and re.search(r"\bplot\b", тіло))) and not сітка
        точки = _точки(команда, опції, тіло, масштаб)
        out.append(картинка[i:m.start()])
        if точки is not None:
            out.append(точки); звіт["точки"] += 1
        else:
            нові = _нові_опції(опції, команда, крива=bool(крива), сітка=сітка, кольорова_крива=кривих > 1 or not палітра, палітра=палітра)
            if крива: звіт["криві"] += 1
            if сітка: звіт["сітки"] += 1
            out.append("\\" + m.group(1) + ("[" + ", ".join(нові) + "]" if нові else " ") + тіло)   # без опцій -- пробіл: \\node at, \\draw plot
        i = j
    out.append(картинка[i:])
    return "".join(out)


ШРИФТИ = re.compile(r"\\(tiny|scriptsize|footnotesize)(?![A-Za-z])")


try:
    РОЗМІРИ = json.load(open(РОЗМІРИ_JSON, encoding="utf-8"))
except (OSError, ValueError):
    РОЗМІРИ = {}
НА_ВИМІР = {}


def ключ_рисунка(код):
    return hashlib.sha1(re.sub(r"\s+", "", код).encode("utf-8")).hexdigest()[:16]


def множник(w, h, варіант):
    """у скільки разів змінити масштаб рисунка з природним розміром w x h см (1 -- не міняти)"""
    if w <= 0 or h <= 0: return 1.0
    if w / h > 3.5 and not варіант:                     # смуга: числова пряма, ряд точок
        мін, макс, ціль = СМУГА_W
        k = ціль / w if w < мін else (ціль / w if w > макс else 1.0)
    else:
        (мін, макс, ціль), wмакс = (ВАРІАНТ_H, ВАРІАНТ_W) if варіант else (ОКРЕМИЙ_H, ОКРЕМИЙ_W)
        k = ціль / h if h < мін else (ціль / h if h > макс else 1.0)
        if w * k > wмакс: k = min(k, wмакс / w) if k > 1 else wмакс / w
    return 1.0 if abs(k - 1) < 0.08 else k


def _масштабувати(відкриття, k):
    """scale = старий * k (у відкритті tikzpicture)"""
    m = re.search(r"(?<![a-z ])scale\s*=\s*([\d.]+)", відкриття)
    новий = "%.3g" % ((float(m.group(1)) if m else 1.0) * k)
    if m: return відкриття[:m.start(1)] + новий + відкриття[m.end(1):]
    if "[" in відкриття: return відкриття.replace("[", "[scale=%s, " % новий, 1)
    return відкриття + "[scale=%s]" % новий


def _палітра_безпечна(тіло):
    """перефарбувати можна, лише якщо різні кольори рисунка не зливаються в один тон палітри"""
    кольори = set(re.findall(r"(?:fill|draw|color|text)\s*=\s*(" + КОЛІР + r")", тіло))
    кольори |= set(re.findall(r"\\(?:fill|draw|filldraw|node)\s*\[\s*(" + КОЛІР + r")\s*[,\]]", тіло))
    заливки = {к for к in кольори if _родина(к)}
    return len({заливка_палітри(к) for к in заливки}) == len(заливки) and len({лінія_палітри(к) for к in заливки}) == len(заливки)


def інфографіка(тіло):
    """рисунок з текстом усередині (слова в підписах, растрова картинка, діаграма): його розмір і шрифти підібрано під
    текст -- нормалізатор їх не чіпає (зменшений сектор діаграми не вміщує «Мелодрама», етикетка -- «Масова частка»)"""
    код = re.sub(r"(?<!\\)%[^\n]*", "", тіло)
    if re.search(r"\\includegraphics|\\begin\{axis\}|legend|ybar|xbar", код): return True
    слова = [w for w in re.findall(r"[А-Яа-яІіЇїЄєҐґ'’]{4,}", код) if w.lower() not in ("рис",)]
    return bool(слова)


def _рисунок(відкриття, тіло, звіт, варіант=False, кольори_зміст=False):
    """правила для одного рисунка (без розміру): -> (відкриття, тіло, ключ виміру або None, якщо розмір не міняємо)"""
    масштаб = _масштаб(відкриття)
    палітра = not кольори_зміст and _палітра_безпечна(тіло)
    if not палітра: звіт["кольори лишено"] += 1
    текст = інфографіка(тіло)
    if текст:
        звіт["інфографіка"] += 1
        return відкриття, _статементи(тіло, масштаб, звіт, палітра), None
    # підписи -- \small (у підписах поділок pgfplots -- \footnotesize, задано стилем)
    тіло = re.sub(r"((?:tick label style|ticklabel style|every tick label/.style)\s*=\s*\{[^{}]*?)font\s*=\s*\\[a-z]+",
                  r"\1font=@@ПОДІЛКИ@@", тіло)
    підпис = "\\footnotesize" if варіант else "\\small"           # у малих рисунках-варіантах -- \footnotesize
    тіло, n = ШРИФТИ.subn(lambda m: m.group(0) if m.group(0) == підпис else підпис, тіло); звіт["шрифти"] += n
    тіло = тіло.replace("@@ПОДІЛКИ@@", "\\footnotesize")
    відкриття, n2 = ШРИФТИ.subn(lambda m: m.group(0) if m.group(0) == підпис else підпис, відкриття); звіт["шрифти"] += n2
    # опції самої картинки: наконечники й товщини -- глобальні
    m = re.match(r"(\\begin\{tikzpicture\})\s*\[((?:[^\[\]]|\[[^\[\]]*\])*)\]", відкриття)
    if m:
        опції = [_стрілка(o) for o in _опції(m.group(2)) if not re.fullmatch(r">\s*=\s*.+", o)]
        відкриття = m.group(1) + ("[" + ", ".join(опції) + "]" if опції else "")
    тіло = _статементи(тіло, масштаб, звіт, палітра)
    if "\\begin{axis}" in тіло or "#" in тіло:      # pgfplots: розмір -- width/height осей; з параметрами #1 -- не виміряти
        return відкриття, тіло, None
    ключ = ключ_рисунка(відкриття + тіло)
    if ключ not in РОЗМІРИ: НА_ВИМІР[ключ] = відкриття + тіло + "\\end{tikzpicture}"
    return відкриття, тіло, ключ


# колір названо в умові -- він частина змісту (жовта зала, червоний сектор): не перефарбовуємо
КОЛЬОРИ_СЛОВАМИ = r"бiл[аиоуеі]\w*|біл[аиоуеі]\w*|блакитн\w*|жовт\w*|зелен\w*|фіолетов\w*|червон\w*|синь\w*|сині?\b|помаранчев\w*|рожев\w*|коричнев\w*|сір[аиоуеі]\w*|чорн\w*|кольор\w*|зафарбован\w*|замальован\w*"
РИС = re.compile(r"(\\begin\{tikzpicture\}\s*(?:\[(?:[^\[\]]|\[[^\[\]]*\])*\])?)(.*?)(?=\\end\{tikzpicture\})", re.S)
МАТЕМАТИКА = re.compile(r"(?<!\\)\$(?!\$)((?:[^$\\]|\\.)+?)(?<!\\)\$")


def _вираз(m):
    s = m.group(1)
    s = re.sub(r"\\(mathrm|operatorname|text)\{tg\}\s*(\\,)?\s*", r"\\tg ", s)
    s = re.sub(r"\\displaystyle\s*\\frac", r"\\dfrac", s)
    s = re.sub(r"\\(leq|le)(?![A-Za-z])", r"\\leqslant", s)
    s = re.sub(r"\\(geq|ge)(?![A-Za-z])", r"\\geqslant", s)
    s = re.sub(r"(?<=[\d}])\s*°", r"^\\circ", s)
    if "\\{" not in s: s = re.sub(r"(?<=\d),(?=\d)", "{,}", s)     # у множинах \{1,2,3\} кома -- роздільник
    s = re.sub(r"\\tg\s+(?=[\\{(])", r"\\tg", s)
    return "$" + s + "$"


def уніфікувати(t, звіт=None):
    """текст завдання -> текст за правилами (рисунки TikZ / pgfplots і вирази в $...$)"""
    звіт = звіт if звіт is not None else collections.Counter()
    частини, рисунки, i = [], [], 0
    усі = list(РИС.finditer(t))
    поза = РИС.sub(" ", t)
    кольори_зміст = bool(re.search(КОЛЬОРИ_СЛОВАМИ, поза, re.I)) or bool(re.search(r"legend|ybar|xbar|bar width|\\addlegendentry|діаграм", t))
    for m in усі:
        текст = t[i:m.start()]
        частини.append(текст)     # текст завдання не міняємо: від нього залежить id (вирази -- стилями преамбули)
        # рисунки-варіанти: три й більше рисунків у завданні або рисунок у клітинці таблиці
        варіант = len(усі) >= 3 or bool(re.search(r"&\s*(\\begin\{nmtfit\}\s*)?$", текст[-60:]))
        рисунки.append((len(частини), варіант) + _рисунок(m.group(1), m.group(2), звіт, варіант, кольори_зміст))
        частини.append(None)
        i = m.end()
    частини.append(t[i:])
    # розмір за виміром; рисунки-варіанти одного завдання -- спільний множник (за медіаною), щоб лишалися однакові
    виміряні = [РОЗМІРИ[к] for _, в, _, _, к in рисунки if в and к in РОЗМІРИ]
    спільний = None
    if виміряні:
        hs = sorted(r["h"] for r in виміряні); ws = sorted(r["w"] for r in виміряні)
        спільний = множник(ws[len(ws) // 2], hs[len(hs) // 2], True)
    for місце, варіант, відкриття, тіло, ключ in рисунки:
        if ключ in РОЗМІРИ:
            k = спільний if варіант and спільний is not None else множник(РОЗМІРИ[ключ]["w"], РОЗМІРИ[ключ]["h"], False)
            if k != 1.0:
                відкриття = _масштабувати(відкриття, k); звіт["розмір"] += 1
        частини[місце] = відкриття + тіло
    return "".join(частини)


# ---------------------------------------------------------------- перевірка
def перевірити(t):
    """що лишилося поза правилами (для ручного виправлення)"""
    зауваги = []
    for m in РИС.finditer(t):
        відк, тіло = m.group(1), m.group(2)
        for к in sorted(set(re.findall(r"(?<![A-Za-z])(red|blue|cyan|magenta|orange|violet|brown|purple|teal|olive|yellow|lime|pink)(?![A-Za-z])", тіло))):
            зауваги.append("колір поза палітрою: %s" % к)
        if re.search(r"\\fill[^;]*circle\s*\(\s*[\d.]+\s*pt", тіло): зауваги.append("точка не вузлом (великий круг?)")
        if "\\includegraphics" in тіло: зауваги.append("растровий рисунок у TikZ")
    for м in МАТЕМАТИКА.finditer(t):
        if re.search(r"\\(mathrm|operatorname)\{tg\}|\\displaystyle\s*\\frac|(?<=\d),(?=\d)", м.group(1)):
            зауваги.append("вираз: %s" % м.group(1)[:40])
    return зауваги


def записати_на_вимір():
    json.dump(НА_ВИМІР, open(НА_ВИМІР_JSON, "w", encoding="utf-8"), ensure_ascii=False)
    return len(НА_ВИМІР)


def виміряти():
    """природний розмір (см) кожного ще не виміряного рисунка: одна компіляція, \\typeout розмірів"""
    sys.path.insert(0, os.path.join(HERE, "варіант_нмт"))
    import спільне as SP, варіант as V
    на_вимір = json.load(open(НА_ВИМІР_JSON, encoding="utf-8"))
    if not на_вимір: print("нового для виміру немає"); return
    s = [V.преамбула("вимір", "вимір"), "\\begin{document}"] + [V.тіло_теми(f) for _, f in SP.файли_тем()]
    s.append("\\newsavebox{\\вимбокс}\\newcommand{\\виміряти}[2]{\\sbox{\\вимбокс}{#2}"
             "\\typeout{ВИМІР #1 \\the\\wd\\вимбокс\\space\\the\\ht\\вимбокс\\space\\the\\dp\\вимбокс}}")
    for к, код in на_вимір.items():
        s.append("\\виміряти{%s}{%s}" % (к, код))
    s.append("\\end{document}")
    ROOT = os.path.dirname(HERE)
    tmp = tempfile.mkdtemp(prefix="вимір_")
    src = os.path.join(ROOT, "варіанти", "_вимір.tex")
    open(src, "w", encoding="utf-8").write(SP.нфк("\n".join(s)))
    try:
        subprocess.run(["xelatex", "-interaction=nonstopmode", "-output-directory=" + tmp, "_вимір.tex"],
                       cwd=os.path.dirname(src), capture_output=True, text=True, timeout=900)
    finally:
        os.remove(src)
    log = open(os.path.join(tmp, "_вимір.log"), encoding="utf-8", errors="replace").read()
    pt = 28.4528
    нові = 0
    for к, w, h, d in re.findall(r"ВИМІР ([0-9a-f]{16}) ([\d.]+)pt ([\d.]+)pt ([\d.]+)pt", log):
        РОЗМІРИ[к] = dict(w=round(float(w) / pt, 2), h=round((float(h) + float(d)) / pt, 2)); нові += 1
    json.dump(РОЗМІРИ, open(РОЗМІРИ_JSON, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)
    print("виміряно %d з %d (без виміру -- рисунки з помилками LaTeX у відриві від теми)" % (нові, len(на_вимір)))


def main():
    if "--виміряти" in sys.argv[1:]:
        виміряти(); return
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "варіант_нмт"))
    import спільне as SP
    звіт, зауваги = collections.Counter(), collections.Counter()
    з_завданнями = collections.defaultdict(list)
    for t in SP.завдання_бази():
        for з in перевірити(t["блок"]):
            ключ = re.sub(r":.*", "", з)
            зауваги[ключ] += 1; з_завданнями[ключ].append(t["id"])
    print("завдань:", len(SP.завдання_бази()))
    for к, n in зауваги.most_common():
        print("  %-40s %4d   напр.: %s" % (к, n, ", ".join(з_завданнями[к][:5])))


if __name__ == "__main__":
    main()
