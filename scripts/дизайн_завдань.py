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
# як у НМТ 2026: піраміда поруч з умовою ~5 x 5 см, широка трапеція по центру ~9,7 x 3,6 см, клітинка сітки 0,5 см
# Єдиний розмір (user, 4.11: «нема однакового розміру для такого типу рисунків ... вигляд має бути монолітний для всього документу»):
# окремий рисунок вписується за «рівною площею» -- усі фігури мають приблизно однаковий візуальний вага (ПЛОЩА), а не довільний масштаб авторів;
# ширину обмежує місце (minipage), висоту -- ОКРЕМИЙ_H, смуги й варіанти -- власні цілі.
ОКРЕМИЙ_ПЛОЩА = 26.0                                   # см^2: ціль для площі рисунка (ширина x висота): 5,3 x 4,9 см
ОКРЕМИЙ_H, ОКРЕМИЙ_W = 4.8, 12.0                       # см: найбільші висота й ширина (рисунок на всю ширину під умовою)
ДОПУСК = 0.03                                          # менше за 3 % не міняємо
КЛІТИНКА, КЛІТИНКА_ВАРІАНТ = 0.5, 0.3                  # см: клітинка сітки (графік, папір у клітинку)
ШИРИНА_ТЕКСТУ = 17.4                                   # см: A4, поля 1,8 см (преамбула бази)
ВАРІАНТ_H, ВАРІАНТ_W = (1.9, 3.0, 2.4), 3.4            # (мін, макс, ціль) висоти і найбільша ширина варіанта в клітинці
ВАРІАНТ_ПРОСТОРИЙ_H, ВАРІАНТ_ПРОСТОРИЙ_W, ПРОСТОРЕ_МІСЦЕ = (1.9, 4.4, 3.0), 5.5, 6.0   # рисунки-пункти у просторій колонці (minipage ≥ 6 см, напр. три трикутники 1--3 у відповідності):
                                                         # вікно більше -- підписи кутів і сторін вміщуються всередині пласких фігур
ДІАГРАМА_W, ДІАГРАМА_H = 12.5, 6.2                      # см: pgfplots-діаграма під умовою (ширина/висота осей); у вузькому місці -- пропорційно
СМУГА_ЦІЛЬ = 8.5                                       # см: ширина смуги (числова пряма, ряд точок; ширина/висота >= 5)
ШИРОКИЙ_ПОРІГ, ШИРОКИЙ_W = 2.2, 11.0                   # ширина/висота > 2,2: широкий рисунок під умовою -- ширина 11 см (усі «смуги між прямими» однакові)
БІЧНИЙ_W = 6.5                                         # см: найбільша ширина рисунка в бічному виді (minipage 0,40)

# ---------------------------------------------------------------- стилі (у преамбулу)
СТИЛІ = r"""
% ===================== ДИЗАЙН-СИСТЕМА РИСУНКІВ (scripts/ПРАВИЛА_ОФОРМЛЕННЯ.md, scripts/дизайн_завдань.py) =====================
\definecolor{nmtInk}{HTML}{1A1A1A}
\definecolor{nmtGrid}{HTML}{3A3A3A}      % сітка, як у НМТ 2026: темна й тонка (0,35 pt), клітинка 0,5 см
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
  nmt grid/.style={draw=nmtGrid, line width=0.35pt},
  nmt curve/.style={line width=1.1pt},
}
% вирази: ≤ і ≥ -- похилі, як у НМТ (десяткову кому без пробілу вже дає mathastext)
\let\leq\leqslant \let\le\leqslant \let\geq\geqslant \let\ge\geqslant
\pgfplotsset{every axis/.append style={axis line style={line width=0.6pt}, tick style={line width=0.45pt},
  tick label style={font=\footnotesize}, label style={font=\small}, grid style={nmtGrid, line width=0.35pt}}}
% стовпчасті діаграми pgfplots: один вигляд (колір, сітка, поділки); ширину стовпця й розмір осей задає нормалізатор (_діаграма_стовпчики)
\pgfplotsset{nmt bar/.style={fill=nmtBlue!55!white, draw=nmtInk, line width=0.45pt}}
\pgfplotsset{nmt bars/.style={ybar, ymin=0, axis x line*=bottom, axis y line*=left, ymajorgrids=true, major grid style={nmtGrid!45, line width=0.35pt},
  enlarge x limits=0.12,
  x tick label style={font=\footnotesize, align=center}, y tick label style={font=\footnotesize}, x label style={align=center}, y label style={align=center}}}
% ===================== кінець дизайн-системи =====================
% підпис кута біля дуги: \nmtAngleLabel{A}{B}{C}{радіус дуги, см}{підпис} -- кут AB C проти годинникової стрілки, як \pic{angle=A--B--C}.
% Підпис ставиться на бісектрисі, найближчим краєм на 0,08 см від дуги (радіус дуги масштабується разом з рисунком, підпис -- ні),
% тож не відлітає від кута, хоч який масштаб рисунка й хоч яка довжина підпису
\newcommand{\nmtAngleLabel}[5]{%
  \path let \p1=(#2), \p2=(#1), \p3=(#3), \p4=(0,0), \p5=(1,0),
    \n1={atan2(\y2-\y1,\x2-\x1)}, \n2={atan2(\y3-\y1,\x3-\x1)},
    \n3={mod(\n2-\n1+720,360)}, \n4={\n1+\n3/2}, \n5={\n4+180},
    \n6={veclen(\x5-\x4,\y5-\y4)/28.45274}, \n7={(#4*\n6+0.08)*28.45274}
  in (#2) node[anchor=\n5, inner sep=1.2pt, shift={(\n4:\n7)}] {#5};}

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


def _це_риска(тіло):
    """короткий відрізок (ризка на осі, ≤0,4 одиниці): (x1,y1) -- (x2,y2); його не потовщуємо"""
    m = re.fullmatch(r"\s*\(\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*\)\s*--\s*\(\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*\)\s*;?\s*", тіло)
    if not m: return False
    x1, y1, x2, y2 = (float(v) for v in m.groups())
    return max(abs(x2 - x1), abs(y2 - y1)) <= 0.4


def _нові_опції(опції, команда, крива=False, сітка=False, кольорова_крива=False, палітра=True, на_сітці=False):
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
    # контури фігур на клітинках (багатокутники, відрізки, одиничний квадрат) -- 1,1 pt, як криві графіків: тонкі 0,75 pt губляться на густій сітці
    # (user, 5.11: «чіткіші зроби контури в задачі на площу по клітинках»); осі зі стрілками, ризки й допоміжні thin не чіпаємо
    if (на_сітці and not сітка and not крива and команда in ("draw", "filldraw")
            and not any(o in ("->", "<-", "<->") or re.search(r"dashed|dotted", o) for o in out)):
        out = ["very thick" if o in ("thick", "semithick") else o for o in out]
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
    на_сітці = bool(re.search(r"\bgrid\b", картинка)) and "\\begin{axis}" not in картинка
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
            нові = _нові_опції(опції, команда, крива=bool(крива), сітка=сітка, кольорова_крива=кривих > 1 or not палітра, палітра=палітра, на_сітці=на_сітці and not _це_риска(тіло))
            if крива: звіт["криві"] += 1
            if сітка: звіт["сітки"] += 1
            out.append("\\" + m.group(1) + ("[" + ", ".join(нові) + "]" if нові else " ") + тіло)   # без опцій -- пробіл: \\node at, \\draw plot
        i = j
    out.append(картинка[i:])
    return "".join(out)


ПІДПИС_НА_СІТЦІ = re.compile(r"\\node\s*(?:\[([^\]]*)\])?(\s*at\s*\([^)]*\)\s*)\{(\$(?:-?\d+(?:[.,]\d+)?|-?\\[a-z]+|[A-Z](?:_\{?\d\}?)?)\$)\}")


def _підписи_на_сітці(тіло):
    """числа на осях і літери точок у рисунках на сітці -- на білій підкладці (лінії сітки не перерізають цифри; підкладка тісна: inner sep 1 pt)"""
    def зам(m):
        опції = m.group(1)
        if опції is not None and "fill" in опції: return m.group(0)
        нові = (опції + ", " if опції else "") + "fill=white, inner sep=1pt, outer sep=1pt"       # outer sep: підкладка не з'їдає край товстої лінії біля точки
        return "\\node[" + нові + "]" + m.group(2) + "{" + m.group(3) + "}"
    return ПІДПИС_НА_СІТЦІ.sub(зам, тіло)


def _контури_на_сітці(тіло):
    """перемальовані рисунки (не проходять _статементи): контури фігур на сітці thick -> very thick (див. _нові_опції); осі, штрихові лінії, сітка, криві -- ні"""
    def зам(m):
        опції, решта = _опції(m.group(2)), m.group(3)
        if _це_риска(решта) or re.search(r"\bgrid\b|\bplot\b", решта) or any(o in ("->", "<-", "<->", "nmt grid", "nmt curve") or re.search(r"dashed|dotted", o) for o in опції): return m.group(0)
        if not any(o in ("thick", "semithick") for o in опції): return m.group(0)
        return m.group(1) + "[" + ", ".join("very thick" if o in ("thick", "semithick") else o for o in опції) + "]" + решта
    return re.sub(r"(\\draw\s*)\[((?:[^\[\]]|\[[^\[\]]*\])*)\]([^;]*;)", зам, тіло)


ШРИФТИ = re.compile(r"\\(tiny|scriptsize|footnotesize)(?![A-Za-z])")
ШРИФТИ_З_SMALL = re.compile(r"\\(tiny|scriptsize|footnotesize|small)(?![A-Za-z])")


try:
    РОЗМІРИ = json.load(open(РОЗМІРИ_JSON, encoding="utf-8"))
except (OSError, ValueError):
    РОЗМІРИ = {}
ІНФО = set()                                           # ключі інфографіки: розмір міряємо (щоб вибрати вид розкладки), але масштаб не міняємо
НА_ВИМІР = {}


def ключ_рисунка(код):
    return hashlib.sha1(re.sub(r"\s+", "", код).encode("utf-8")).hexdigest()[:16]


def ширина_місця(до):
    """ширина (см) minipage, у якій стоїть рисунок (текст до рисунка), або None: ширший рисунок \\begin{nmtfit}
    зменшить разом з підписами, тож розмір обмежуємо цим місцем"""
    відкриті = []
    for m in re.finditer(r"\\begin\{minipage\}(?:\[[^\]]*\])*\{([\d.]+)\\(?:textwidth|linewidth)\}|\\end\{minipage\}", до):
        if m.group(0).startswith("\\end"):
            if відкриті: відкриті.pop()
        else:
            відкриті.append(float(m.group(1)))
    return відкриті[-1] * ШИРИНА_ТЕКСТУ - 0.4 if відкриті else None


def множник(w, h, варіант, wмісця=None, одна=False):
    """у скільки разів змінити масштаб рисунка з природним розміром w x h см (1 -- не міняти). -> (k, вид)
    вид: 'S' (бічний, поруч з умовою) чи 'C' (широкий, під умовою) -- його вибирає тільки форма рисунка (ширина/висота), розкладка (розкладка_завдань.py) слухається.
    Бічний: цільова площа ОКРЕМИЙ_ПЛОЩА (великий -- менший, малий -- більший), не вище ОКРЕМИЙ_H, не ширше БІЧНИЙ_W.
    Широкий (a > 2,2): ширина ШИРОКИЙ_W. Смуга (a >= 5): СМУГА_ЦІЛЬ. Варіант у клітинці: вписується в рамку.
    одна=False (кілька рисунків у завданні, розкладка їх не чіпає): додатково обмежує реальне місце wмісця."""
    if w <= 0 or h <= 0: return 1.0, "S"
    if варіант:
        простор = bool(wмісця and wмісця >= ПРОСТОРЕ_МІСЦЕ)
        мін, макс, ціль = ВАРІАНТ_ПРОСТОРИЙ_H if простор else ВАРІАНТ_H
        wмакс = min(ВАРІАНТ_ПРОСТОРИЙ_W, wмісця) if простор else ВАРІАНТ_W
        k = min(ціль / h, wмакс / w) if (h < мін or h > макс or w > wмакс) else 1.0
        return (1.0 if abs(k - 1) < ДОПУСК else k), "S"
    a = w / h
    if a >= 5: k, вид = СМУГА_ЦІЛЬ / w, "C"
    elif a > ШИРОКИЙ_ПОРІГ: k, вид = min(ШИРОКИЙ_W / w, ОКРЕМИЙ_H / h), "C"
    else: k, вид = min((ОКРЕМИЙ_ПЛОЩА / (w * h)) ** 0.5, ОКРЕМИЙ_H / h, БІЧНИЙ_W / w), "S"
    if not одна and wмісця: k = min(k, wмісця / w)
    return (1.0 if abs(k - 1) < ДОПУСК else k), вид


def крок_сітки(відкриття, тіло):
    """крок сітки в одиницях рисунка (для правила «клітинка 0,5 см») або None: сітки немає чи одиниця не 1 см (x=, y=)"""
    if re.search(r"(?<![a-z])(x|y)\s*=", відкриття): return None
    for m in re.finditer(r"\\draw\s*\[([^\]]*)\][^;]*?\bgrid\b", тіло):
        крок = re.search(r"(?<![a-z])(?:x?step)\s*=\s*([\d.]+)\s*(cm)?", m.group(1))
        return float(крок.group(1)) if крок else 1.0
    if re.search(r"\bgrid\b", тіло): return 1.0
    return None


def множник_клітинки(відкриття, тіло, w, варіант, wмісця=None, одна=False):
    """масштаб, за якого клітинка сітки -- 0,5 см (у варіантах 0,3); None -- правило не діє. -> (k, вид) або None
    широкий графік (ширина > БІЧНИЙ_W за клітинки 0,5 см) -- широкий вид, до ОКРЕМИЙ_W; вузький -- бічний"""
    крок = крок_сітки(відкриття, тіло)
    if not крок: return None
    # «варіанти» (≥3 рисунки в завданні) у вузьких клітинках таблиці -- сітка 0,3 см; але в просторих колонках (minipage ≥5 см: «Рис. 1», «Рис. 2», «Рис. 3»
    # поруч) -- звичайна клітинка 0,5 см, інакше графіки виходять дрібними
    if варіант and wмісця and wмісця >= 5.0: варіант = False
    k = (КЛІТИНКА_ВАРІАНТ if варіант else КЛІТИНКА) / (крок * _масштаб(відкриття))
    if варіант:
        wмакс = ВАРІАНТ_W
        if wмісця: wмакс = min(wмакс, wмісця)
        if w and w * k > wмакс: k = wмакс / w
        return (1.0 if abs(k - 1) < 0.05 else k), "S"
    вид = "C" if (w and w * k > БІЧНИЙ_W + 0.1) else "S"
    wмакс = ОКРЕМИЙ_W if вид == "C" else БІЧНИЙ_W
    if not одна and wмісця: wмакс = min(wмакс, wмісця)
    if w and w * k > wмакс: k = wмакс / w
    return (1.0 if abs(k - 1) < 0.05 else k), вид


ВІДСТУП_КУТА, ВІДСТУП_КУТА_ВАРІАНТ = 0.45, 0.34       # см: від дуги до центру підпису кута (\\normalsize / \\small)


def _дов(значення, одиниця):
    return float(значення) * {"cm": 1, "mm": 0.1, "pt": 0.03515, "": 1, None: 1}[одиниця]


def _збалансовано(t, i, відкр, закр):
    """індекс закривної дужки, парної до t[i] == відкр"""
    г = 0
    for k in range(i, len(t)):
        if t[k] == відкр: г += 1
        elif t[k] == закр:
            г -= 1
            if not г: return k
    return -1


def кути_біля_дуги(тіло):
    """підпис кута (pic text / "$60^\\circ$" в \\pic[..]{angle=A--B--C}) -> \\nmtAngleLabel після дуги: підпис стоїть
    на бісектрисі, найближчим краєм біля дуги, і не відлітає хоч який масштаб рисунка (макрос -- у СТИЛІ).
    Радіус для підпису -- найбільший серед усіх дуг цього кута (подвійна дуга)."""
    дуги = []                                   # (початок, кінець, опції, A, B, C)
    for m in re.finditer(r"\\pic\s*\[", тіло):
        i = m.end() - 1; j = _збалансовано(тіло, i, "[", "]")
        if j < 0: continue
        k = j + 1
        while k < len(тіло) and тіло[k] in " \n\t": k += 1
        if k >= len(тіло) or тіло[k] != "{": continue
        l = _збалансовано(тіло, k, "{", "}")
        спец = re.fullmatch(r"\s*angle\s*=\s*(\w+)\s*--\s*(\w+)\s*--\s*(\w+)\s*", тіло[k + 1:l])
        if not спец: continue
        e = l + 1
        while e < len(тіло) and тіло[e] in " \t": e += 1
        if e < len(тіло) and тіло[e] == ";": e += 1
        дуги.append((m.start(), e, тіло[i + 1:j], спец.groups(), l + 1))
    радіус = {}
    for _, _, оп, кут, _ in дуги:
        r = re.search(r"angle radius\s*=\s*([\d.]+)\s*(cm|mm|pt)?", оп)
        радіус[кут] = max(радіус.get(кут, 0), _дов(r.group(1), r.group(2)) if r else 0.5)
    вихід, поз = [], 0
    for початок, кінець, оп, кут, _ in дуги:
        частини = _опції(оп); підпис = None; лишити = []
        for o in частини:
            q = re.fullmatch(r'"(.*)"(?:\{.*\})?', o.strip(), re.S)
            t = re.fullmatch(r"pic text\s*=\s*(.*)", o.strip(), re.S)
            if q: підпис = q.group(1)
            elif t: підпис = t.group(1).strip()[1:-1] if t.group(1).strip().startswith("{") else t.group(1).strip()
            elif re.match(r"(pic text options|angle eccentricity)\b", o.strip()): continue
            else: лишити.append(o)
        if підпис is None: continue
        нова_дуга = "\\pic[" + ", ".join(лишити) + "] " + тіло[тіло.index("{", початок + 4 + len(оп)):кінець]
        нова_дуга = нова_дуга.rstrip()
        if not нова_дуга.endswith(";"): нова_дуга += ";"
        a, b, c = кут
        мітка = "\n    \\nmtAngleLabel{%s}{%s}{%s}{%.3g}{%s}" % (a, b, c, радіус[кут], підпис)
        вихід.append(тіло[поз:початок]); вихід.append(нова_дуга + мітка); поз = кінець
    вихід.append(тіло[поз:])
    return "".join(вихід)



def підписи_кутів(тіло, масштаб, варіант):
    """підпис кута (\\pic[..., "$60^\\circ$"] або pic text) -- не на дузі: центр не ближче за радіус дуги + відступ
    (радіус дуги масштабується разом з рисунком, підпис -- ні)"""
    відступ = ВІДСТУП_КУТА_ВАРІАНТ if варіант else ВІДСТУП_КУТА
    def fix(m):
        опції = m.group(1)
        if not ('"' in опції or "pic text" in опції): return m.group(0)
        r = re.search(r"angle radius\s*=\s*([\d.]+)\s*(cm|mm|pt)?", опції)
        радіус = (_дов(r.group(1), r.group(2)) if r else 0.5) * масштаб
        e = re.search(r"angle eccentricity\s*=\s*([\d.]+)", опції)
        ексц = float(e.group(1)) if e else 0.6
        треба = 1 + відступ / max(радіус, 0.05)
        if ексц >= треба: return m.group(0)
        нове = "angle eccentricity=%.2f" % треба
        опції = опції[:e.start()] + нове + опції[e.end():] if e else опції + ", " + нове
        return "\\pic[" + опції + "]"
    return re.sub(r"\\pic\s*\[((?:[^\[\]]|\[[^\[\]]*\])*)\]", fix, тіло)


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


def _без_масштабу(відкриття):
    """діаграма pgfplots: масштаб картинки scale=.. розсуває підписи осей (їхні відступи в pt не масштабуються) -- розмір задають width/height осей"""
    m = re.match(r"(\\begin\{tikzpicture\})\s*\[((?:[^\[\]]|\[[^\[\]]*\])*)\](.*)", відкриття, re.S)
    if not m: return відкриття
    опції = [o for o in _опції(m.group(2)) if not re.fullmatch(r"(?:x|y)?scale\s*=\s*[-\d.]+|transform shape", o.strip())]
    return m.group(1) + ("[" + ", ".join(опції) + "]" if опції else "") + m.group(3)


ВИДАЛИТИ_З_СТОВПЧИКІВ = re.compile(r"(?:bar width|enlarge x limits|enlarge y limits|grid style|major grid style|minor grid style|minor y tick num|"
                                   r"yminorgrids|ymajorgrids|xmajorgrids|grid|fill|draw|axis lines|axis x line\*?|axis y line\*?|every axis plot/\.append style|"
                                   r"x label style|xlabel style|y label style|ylabel style|x tick label style|xticklabel style|y tick label style|ybar|ymin|ytick style|tick style|clip)\s*(?:=|$)")


def _діаграма_стовпчики(опції):
    """ybar-діаграма без легенди -> стиль nmt bars + ширина стовпця за кількістю категорій; усі ручні налаштування вигляду (кольори, сітка,
    положення підписів осей) -- геть, лишаються дані: поділки, підписи осей, межі"""
    текст = re.sub(r"%[^\n]*", "", опції)
    if "legend" in текст or "xbar" in текст or "ybar" not in текст: return опції
    список = _опції(текст.replace("\n", " "))
    ymin = next((o for o in список if re.match(r"ymin\s*=", o)), None)
    # кількість категорій: xtick / symbolic x coords / xticklabels
    n = 0
    for ключ in (r"symbolic x coords", r"xticklabels", r"xtick"):
        m = re.search(ключ + r"\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", текст)
        if m: n = len([x for x in re.split(r",", m.group(1)) if x.strip()]); break
    n = max(n, 1)
    bw = round(min(1.2, 0.45 * 11.0 / n), 2)
    нові = [o for o in список if not ВИДАЛИТИ_З_СТОВПЧИКІВ.match(o)]
    ключові = [o for o in нові if re.match(r"(?:width|height)\s*=", o)]
    решта = [o for o in нові if o not in ключові]
    return ",\n    ".join(["nmt bars", "bar width=%gcm" % bw] + ключові + ([ymin] if ymin else []) + решта)


def _розмір_діаграми(тіло, wмісця):
    """pgfplots-діаграма: розмір осей -- єдиний (ДІАГРАМА_W x ДІАГРАМА_H); у вузькому місці (minipage) -- пропорційно до місця.
    Шрифти не міняємо (діаграма з текстом), лише width/height осей"""
    w = ДІАГРАМА_W if not wмісця or wмісця >= 11 else max(5.0, wмісця - 1.8)
    h = round(w * ДІАГРАМА_H / ДІАГРАМА_W, 1)
    def фікс(m):
        опції = m.group(1)
        for ключ, знач in (("width", w), ("height", h)):
            n = re.subn(r"(?:(?<=,)|(?<=^))(\s*)%s\s*=\s*[^,\n\]]+" % ключ, lambda mm: "%s%s=%gcm" % (mm.group(1), ключ, знач), опції)
            опції = n[0] if n[1] else опції + ",\n    %s=%gcm" % (ключ, знач)
        return "\\begin{axis}[" + _діаграма_стовпчики(опції) + "]"
    нове = re.sub(r"\\begin\{axis\}\[(.*?)\]", фікс, тіло, count=1, flags=re.S)
    if "nmt bars" in нове:      # стовпці: заливку й контур задає стиль nmt bar (явна опція сильніша за палітру кольорів pgfplots)
        нове = re.sub(r"\\addplot\s*\[nmt curve\s*(?:,\s*)?([^\]]*)\]", lambda m: "\\addplot[nmt bar%s] " % ((", " + m.group(1)) if m.group(1).strip() else ""), нове)
        нове = re.sub(r"\\addplot\s+coordinates", "\\addplot[nmt bar] coordinates", нове)
    return нове


def _рисунок(відкриття, тіло, звіт, варіант=False, кольори_зміст=False, wмісця=None):
    """правила для одного рисунка (без розміру): -> (відкриття, тіло, ключ виміру або None, якщо розмір не міняємо)"""
    масштаб = _масштаб(відкриття)
    палітра = not кольори_зміст and _палітра_безпечна(тіло)
    if not палітра: звіт["кольори лишено"] += 1
    текст = інфографіка(тіло)
    if текст:
        звіт["інфографіка"] += 1
        тіло = _статементи(тіло, масштаб, звіт, палітра)
        if "\\begin{axis}" in тіло and not варіант and "#" not in тіло: тіло = _розмір_діаграми(тіло, wмісця)
        elif not варіант and "\\begin{axis}" not in тіло and "#" not in тіло and "\\includegraphics" not in тіло:
            ключ = ключ_рисунка(відкриття + тіло); ІНФО.add(ключ)         # TikZ-інфографіка: лише міряємо
            if ключ not in РОЗМІРИ: НА_ВИМІР[ключ] = відкриття + тіло + "\\end{tikzpicture}"
            return відкриття, тіло, ключ
        return відкриття, тіло, None
    # підписи -- розміру тексту умови, як у НМТ 2026 (\normalsize); у малих рисунках-варіантах -- \small
    тіло = re.sub(r"((?:tick label style|ticklabel style|every tick label/.style)\s*=\s*\{[^{}]*?)font\s*=\s*\\[a-z]+",
                  r"\1font=@@ПОДІЛКИ@@", тіло)
    підпис, шрифти = ("\\small", ШРИФТИ) if варіант else ("\\normalsize", ШРИФТИ_З_SMALL)
    тіло, n = шрифти.subn(lambda m: m.group(0) if m.group(0) == підпис else підпис, тіло); звіт["шрифти"] += n
    тіло = тіло.replace("@@ПОДІЛКИ@@", "\\footnotesize")
    відкриття, n2 = шрифти.subn(lambda m: m.group(0) if m.group(0) == підпис else підпис, відкриття); звіт["шрифти"] += n2
    # опції самої картинки: наконечники й товщини -- глобальні
    m = re.match(r"(\\begin\{tikzpicture\})\s*\[((?:[^\[\]]|\[[^\[\]]*\])*)\]", відкриття)
    if m:
        опції = [_стрілка(o) for o in _опції(m.group(2)) if not re.fullmatch(r">\s*=\s*.+", o)]
        відкриття = m.group(1) + ("[" + ", ".join(опції) + "]" if опції else "")
    тіло = _статементи(тіло, масштаб, звіт, палітра)
    if re.search(r"\bgrid\b", тіло) and "\\begin{axis}" not in тіло: тіло = _підписи_на_сітці(тіло)
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


def _розмір_елементів(елементи, звіт, одна=False):
    """елементи: [(варіант, wмісця, відкриття, тіло, ключ)] -> нові відкриття (масштаб за єдиними правилами розміру);
    наприкінці відкриття -- маркер «%@N ширинаxвисота вид» (природний розмір і вид розкладки S/C)"""
    виміряні = [РОЗМІРИ[к] for в, _, _, _, к in елементи if в and к in РОЗМІРИ]
    спільний = None
    if виміряні:
        hs = sorted(r["h"] for r in виміряні); ws = sorted(r["w"] for r in виміряні)
        місце = next((wм for в, wм, _, _, _ in елементи if в and wм), None)
        спільний = множник(ws[len(ws) // 2], hs[len(hs) // 2], True, місце)[0]
    вихід = []
    for варіант, wмісця, відкриття, тіло, ключ in елементи:
        if ключ in ІНФО and ключ in РОЗМІРИ:             # інфографіка: масштаб не міняємо, лише вид розкладки за природною шириною
            w, h = РОЗМІРИ[ключ]["w"], РОЗМІРИ[ключ]["h"]
            відкриття += "%%@N %.2fx%.2f %s\n" % (w, h, "C" if w > БІЧНИЙ_W + 0.3 else "S")
        elif ключ in РОЗМІРИ:
            w, h = РОЗМІРИ[ключ]["w"], РОЗМІРИ[ключ]["h"]
            r = множник_клітинки(відкриття, тіло, w, варіант, wмісця, одна)     # графік / папір у клітинку
            if r is None:
                k, вид = множник(w, h, варіант, wмісця, одна)
                if варіант and спільний is not None: k = спільний
                if not одна and wмісця and w * k > wмісця: k = wмісця / w
            else:
                k, вид = r
            if k != 1.0:
                відкриття = _масштабувати(відкриття, k); звіт["розмір"] += 1
            відкриття += "%%@N %.2fx%.2f %s\n" % (w, h, вид)      # природний розмір і вид: за ним розкладка вибирає бічний чи широкий
        вихід.append(відкриття)
    return вихід


def розмір_перемальованих(рисунки, тексти_до, всього, звіт=None):
    """перемальовані за оригіналом рисунки (їх малювали за правилами, але в довільному масштабі) -> той самий єдиний розмір, що й решта.
    рисунки -- повні тексти tikzpicture, тексти_до -- текст завдання перед кожним з них, всього -- скільки рисунків у завданні"""
    звіт = звіт if звіт is not None else collections.Counter()
    елементи, вихід = [], []
    for р, до in zip(рисунки, тексти_до):
        m = РИС.match(р)
        відкриття, тіло = m.group(1), m.group(2)
        # перемальовані рисунки не проходять _рисунок: числа/літери на сітці -- на білу підкладку тут (явні підкладки автора лишаються)
        if re.search(r"\bgrid\b", тіло) and "\\begin{axis}" not in тіло: тіло = _контури_на_сітці(_підписи_на_сітці(тіло))
        варіант = всього >= 3 or bool(re.search(r"&\s*(\\begin\{nmtfit\}\s*)?$", до[-60:]))
        ключ = None
        if "\\begin{axis}" in тіло and "#" not in тіло and not варіант:
            тіло = _розмір_діаграми(тіло, None if всього == 1 else ширина_місця(до))
        if not (інфографіка(тіло) or "\\begin{axis}" in тіло or "#" in тіло):
            ключ = ключ_рисунка(відкриття + тіло)
            if ключ not in РОЗМІРИ: НА_ВИМІР[ключ] = відкриття + тіло + "\\end{tikzpicture}"
        елементи.append((варіант, ширина_місця(до), відкриття, тіло, ключ))
    for (в, w, відк, тіло, к), нове in zip(елементи, _розмір_елементів(елементи, звіт, всього == 1)):
        if "\\begin{axis}" in тіло and not в and "#" not in тіло: нове = _без_масштабу(нове)
        вихід.append(нове + тіло + "\\end{tikzpicture}")
    return вихід


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
        рисунки.append((len(частини), варіант, ширина_місця(t[:m.start()])) + _рисунок(m.group(1), m.group(2), звіт, варіант, кольори_зміст, None if len(усі) == 1 else ширина_місця(t[:m.start()])))
        частини.append(None)
        i = m.end()
    частини.append(t[i:])
    # розмір за виміром; рисунки-варіанти одного завдання -- спільний множник (за медіаною), щоб лишалися однакові
    нові_відкриття = _розмір_елементів([(в, wм, відк, тіло, ключ) for _, в, wм, відк, тіло, ключ in рисунки], звіт, len(усі) == 1)
    for (місце, варіант, wмісця, відкриття, тіло, ключ), нове in zip(рисунки, нові_відкриття):
        відкриття = нове
        if "\\begin{axis}" in тіло and not варіант and "#" not in тіло: відкриття = _без_масштабу(відкриття)
        if ключ is not None:                                  # не інфографіка: підписи кутів -- біля дуги (\\nmtAngleLabel)
            тіло = кути_біля_дуги(тіло)
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


# ---------------------------------------------------------------- растрові рисунки (\\includegraphics поза TikZ)
def розмір_растрового(опції, файл, тека):
    """\\includegraphics[опції]{файл} -> нові опції (width=... см) за єдиними правилами розміру. Природний розмір -- піксельний розмір PNG
    (72 dpi, як у LaTeX без dpi), опції scale=/width=/height= враховуються, щоб знати, що зараз; -> (опції, вид S/C) або None"""
    try:
        from PIL import Image
        шлях = os.path.join(тека, файл)
        w_px, h_px = Image.open(шлях).size
    except Exception:
        return None
    cm = 2.54 / 72
    w, h = w_px * cm, h_px * cm
    опції = опції or ""
    sc = re.search(r"scale\s*=\s*([\d.]+)", опції)
    wd = re.search(r"width\s*=\s*([\d.]+)\s*(cm|\\textwidth|\\linewidth)", опції)
    ht = re.search(r"height\s*=\s*([\d.]+)\s*cm", опції)
    if sc: w, h = w * float(sc.group(1)), h * float(sc.group(1))
    elif wd:
        ціль = float(wd.group(1)) * (ШИРИНА_ТЕКСТУ if wd.group(2) != "cm" else 1)
        w, h = ціль, h * ціль / w
    elif ht:
        ціль = float(ht.group(1)); w, h = w * ціль / h, ціль
    k, вид = множник(w, h, False, None, True)
    k = k if k != 1.0 else 1.0
    return "width=%.2fcm" % (w * k), вид
