# -*- coding: utf-8 -*-
"""Рисунки TikZ для каталогу типів з геометрії: іменовані точки, многокутники, позначки кутів і довжин,
косокутна проєкція тіл (куб, прямокутний паралелепіпед, піраміди) з пунктиром невидимих ребер.

Мітки (назви точок, градусні міри кутів, довжини) розставляються автоматично: для кожної перебираються
положення біля її місця, і вибирається найближче, де напис не перекриває жодної лінії, дуги кута, кола,
точки чи іншого напису. Бажане положення (above, below left, ...) лише задає, з чого почати пошук.

Рисунок схематичний, як у НМТ; відповіді рахуються не з рисунка, а з даних умови (у спец.py)."""
import re
import math

ВІДСТУП = 0.05        # см: найменший проміжок між написом і лінією
НАПРЯМКИ = {"right": 0, "above right": 45, "above": 90, "above left": 135, "left": 180, "below left": 225,
            "below": 270, "below right": 315}


def назва(n):
    """A1 -> A_1 (мітка на рисунку)"""
    return re.sub(r"^([A-Za-z])(\d+)$", r"\1_\2", n)


def розмір(текст, масштаб_шрифту=1.0):
    """приблизні ширина й висота напису (см) у шрифті \\small документа 12pt"""
    t = текст.replace(r"\circ", "°")
    t = re.sub(r"\\text\{([^}]*)\}", r"\1", t)
    t = re.sub(r"\\(alpha|beta|gamma|delta|varphi|phi|theta)\b", "a", t)
    t = re.sub(r"\\[A-Za-z]+", "", t)
    t = re.sub(r"[\^_{}$~ ]", "", t)
    n = sum(0.5 if ch == "°" else 1.0 for ch in t)
    return (0.21 * n + 0.06) * масштаб_шрифту, 0.34 * масштаб_шрифту


def _кут_градуси(p, q):
    return math.degrees(math.atan2(q[1] - p[1], q[0] - p[0])) % 360


class Рис:
    def __init__(self, scale=1.0):
        self.scale = scale
        self.s = [r"\begin{tikzpicture}[scale=%s, line join=round, line cap=round]" % scale]
        self.т = {}           # назва -> (x, y) у координатах рисунка
        self.відрізки = []    # ((x, y), (x, y), м'який) -- у координатах рисунка; м'які (пунктир) обходимо в другу чергу
        self.дуги = []        # (центр_см, радіус_см, від_град, до_град, м'який)
        self.попередження = []
        self.крапки = []      # центри точок-кружечків (см)
        self.прямокутники = []  # заборонені для написів ділянки (x0, y0, x1, y1) у см
        self.кути_мітки = []  # (a, o, b, текст, r_см)
        self.мітки = []       # (назва, де, текст)
        self.довжини = []     # (a, b, текст, де)

    # ------------------------------------------------ побудова
    def _см(self, p):
        return (p[0] * self.scale, p[1] * self.scale)

    def _xy(self, n):
        return self.т[n] if isinstance(n, str) else n

    def точки(self, d):
        """{назва: (x, y)} -> \\coordinate; назви на кшталт A1 стають мітками A_1"""
        for n, (xx, yy) in d.items():
            self.т[n] = (xx, yy)
            self.s.append(r"\coordinate (%s) at (%.3f,%.3f);" % (n, xx, yy))
        return self

    def перетин(self, n, a, b, c, d):
        """точка n -- перетин прямих ab і cd"""
        (x1, y1), (x2, y2), (x3, y3), (x4, y4) = (self._xy(q) for q in (a, b, c, d))
        дет = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / дет
        py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / дет
        return self.точки({n: (px, py)})

    def лінія(self, *назви, стиль="thick", замкнена=False):
        self.s.append(r"\draw[%s] " % стиль + " -- ".join("(%s)" % n for n in назви) + (" -- cycle;" if замкнена else ";"))
        pts = [self._xy(n) for n in назви] + ([self._xy(назви[0])] if замкнена else [])
        мякий = "dashed" in стиль or "dotted" in стиль
        self.відрізки += [(p, q, мякий) for p, q in zip(pts, pts[1:])]
        return self

    def коло(self, центр, R, стиль="thick"):
        c = self._xy(центр)
        self.s.append(r"\draw[%s] (%.3f,%.3f) circle[radius=%s];" % (стиль, c[0], c[1], R))
        self.дуги.append((self._см(c), R * self.scale, 0, 360, "dashed" in стиль or "dotted" in стиль))
        return self

    def дуга(self, центр, R, від, до, стиль="dotted"):
        """дуга кола з центром у точці (радіус у координатах рисунка, кути в градусах проти годинникової стрілки)"""
        c = self._xy(центр)
        x0, y0 = c[0] + R * math.cos(math.radians(від)), c[1] + R * math.sin(math.radians(від))
        self.s.append(r"\draw[%s] (%.3f,%.3f) arc[start angle=%s, end angle=%s, radius=%s];" % (стиль, x0, y0, від, до, R))
        self.дуги.append((self._см(c), R * self.scale, від, до, "dashed" in стиль or "dotted" in стиль))
        return self

    def кут(self, a, o, b, текст="", r=0.45, дуги=1):
        """дуга кута aob (проти годинникової стрілки від променя oa до променя ob); підпис ставиться окремо"""
        V, A, B = (self._см(self._xy(q)) for q in (o, a, b))
        φa, φb = _кут_градуси(V, A), _кут_градуси(V, B)
        for k in range(дуги):
            self.s.append(r"\pic[draw, angle radius=%.2fcm] {angle = %s--%s--%s};" % (r + 0.07 * k, a, o, b))
            self.дуги.append((V, r + 0.07 * k, φa, φa + (φb - φa) % 360, False))
        if текст: self.кути_мітки.append((a, o, b, текст, r + 0.07 * (дуги - 1)))
        return self

    def прямий(self, a, o, b):
        self.s.append(r"\pic[draw, angle radius=0.2cm] {right angle = %s--%s--%s};" % (a, o, b))
        V, A, B = (self._см(self._xy(q)) for q in (o, a, b))
        ua, ub = (_одиничний(V, A), _одиничний(V, B))
        k1 = (V[0] + 0.2 * ua[0], V[1] + 0.2 * ua[1]); k2 = (V[0] + 0.2 * ub[0], V[1] + 0.2 * ub[1])
        кут_ = (k1[0] + 0.2 * ub[0], k1[1] + 0.2 * ub[1])
        self.відрізки += [(self._з_см(k1), self._з_см(кут_), False), (self._з_см(кут_), self._з_см(k2), False)]
        return self

    def _з_см(self, p):
        return (p[0] / self.scale, p[1] / self.scale)

    def точка(self, *назви):
        for n in назви:
            self.s.append(r"\node[circle, fill, inner sep=1.3pt] at (%s) {};" % n)   # вузол не масштабується
            self.крапки.append(self._см(self._xy(n)))
        return self

    def підписи(self, d):
        """{назва: бажане положення} або {назва: (положення, текст)}"""
        for n, де in d.items():
            текст = назва(n)
            if isinstance(де, tuple): де, текст = де
            self.мітки.append((n, де, текст))
        return self

    def довжина(self, a, b, текст, де="above", зсув=0.0):
        """підпис довжини біля середини відрізка ab (зсув лишено для сумісності -- положення добирається саме)"""
        self.довжини.append((a, b, текст, де))
        return self

    def перешкода(self, x0, y0, x1, y1):
        """ділянка рисунка (у його координатах), куди не можна ставити написи"""
        (a, b), (c, d) = self._см((x0, y0)), self._см((x1, y1))
        self.прямокутники.append((min(a, c), min(b, d), max(a, c), max(b, d)))
        return self

    def осі(self, x0, x1, y0, y1):
        """сітка з осями й позначками 0 і 1 (як рисунки.осі), осі й позначки -- перешкоди для написів"""
        self.s += [r"\draw[gray!35, very thin] (%s,%s) grid (%s,%s);" % (x0, y0, x1, y1),
                   r"\draw[->] (%s,0) -- (%s,0) node[below left, font=\footnotesize] {$x$};" % (x0, x1 + 0.5),
                   r"\draw[->] (0,%s) -- (0,%s) node[below left, font=\footnotesize] {$y$};" % (y0, y1 + 0.5),
                   r"\node[below left, font=\scriptsize] at (0,0) {$0$};",
                   r"\node[below, font=\scriptsize] at (1,0) {$1$}; \node[left, font=\scriptsize] at (0,1) {$1$};"]
        self.відрізки += [((x0, 0), (x1 + 0.5, 0), False), ((0, y0), (0, y1 + 0.5), False)]
        for (cx, cy) in ((0, 0), (1, 0), (0, 1)):
            X, Y = self._см((cx, cy))
            self.прямокутники.append((X - 0.3, Y - 0.35, X + 0.05, Y + 0.05) if (cx, cy) == (0, 0) else
                                     ((X - 0.12, Y - 0.35, X + 0.12, Y - 0.02) if cx else (X - 0.35, Y - 0.12, X - 0.02, Y + 0.12)))
        for (cx, cy) in ((x1 + 0.5, 0), (0, y1 + 0.5)):
            X, Y = self._см((cx, cy))
            self.прямокутники.append((X - 0.35, Y - 0.35, X, Y))
        return self

    def сире(self, t):
        self.s.append(t)
        return self

    # ------------------------------------------------ розміщення написів
    def _зразки(self):
        """точки на всіх лініях, дугах і колах (см) через 0,04 см: (тверді, м'які) -- для перевірки перекриття"""
        тверді, мякі = [], []
        for p, q, мякий in self.відрізки:
            P, Q = self._см(p), self._см(q)
            n = max(2, int(math.dist(P, Q) / 0.04) + 2)
            (мякі if мякий else тверді).extend((P[0] + (Q[0] - P[0]) * i / (n - 1), P[1] + (Q[1] - P[1]) * i / (n - 1)) for i in range(n))
        for c, R, a0, a1, мякий in self.дуги:
            n = max(6, int(R * math.radians(a1 - a0) / 0.04) + 2)
            (мякі if мякий else тверді).extend((c[0] + R * math.cos(math.radians(a0 + (a1 - a0) * i / (n - 1))),
                                               c[1] + R * math.sin(math.radians(a0 + (a1 - a0) * i / (n - 1)))) for i in range(n))
        for c in self.крапки:
            тверді.extend([(c[0] + 0.07 * math.cos(math.radians(k)), c[1] + 0.07 * math.sin(math.radians(k))) for k in range(0, 360, 45)] + [c])
        return тверді, мякі

    def _вільно(self, c, w, h, зразки, зайняті, суворо=True):
        x0, y0, x1, y1 = c[0] - w / 2 - ВІДСТУП, c[1] - h / 2 - ВІДСТУП, c[0] + w / 2 + ВІДСТУП, c[1] + h / 2 + ВІДСТУП
        тверді, мякі = зразки
        if any(x0 < px < x1 and y0 < py < y1 for px, py in тверді): return False
        if суворо and any(x0 < px < x1 and y0 < py < y1 for px, py in мякі): return False
        return not any(x0 < b[2] and b[0] < x1 and y0 < b[3] and b[1] < y1 for b in зайняті)

    def _тверді_відрізки_см(self):
        return [(self._см(p), self._см(q)) for p, q, мякий in self.відрізки if not мякий]

    def _розмістити(self):
        """кожному написові -- положення з найменшою «ціною»: відстань від свого місця, дотик до пунктиру (+0,2),
        суцільна лінія між написом і його точкою (+1); перекриття суцільних ліній, дуг, точок і написів заборонені"""
        зразки, зайняті, вузли = self._зразки(), list(self.прямокутники), []
        тверді = self._тверді_відрізки_см()

        def поставити(c, w, h, текст, шрифт):
            зайняті.append((c[0] - w / 2, c[1] - h / 2, c[0] + w / 2, c[1] + h / 2))
            x, y = self._з_см(c)
            вузли.append(r"\node[font=%s, inner sep=0pt] at (%.3f,%.3f) {$%s$};" % (шрифт, x, y, текст))

        def найкращий(кандидати, w, h, якір, свої=()):
            """кандидати -- (центр, базова ціна); свої -- відрізки, що виходять із якоря (їх перетин не рахуємо)"""
            краще = None
            for c, ціна in кандидати:
                if краще and ціна >= краще[1]: continue
                if not self._вільно(c, w, h, зразки, зайняті, суворо=False): continue
                if not self._вільно(c, w, h, зразки, зайняті, суворо=True): ціна += 0.2
                if any(_перетинаються(якір, c, P, Q) for P, Q in тверді if not _спільний_кінець((P, Q), свої)): ціна += 1.0
                if not краще or ціна < краще[1]: краще = (c, ціна)
            return краще[0] if краще else None

        # 1) градусні міри кутів: спершу всередині кута (за дугою, ближче до бісектриси), лише потім -- поза ним
        for a, o, b, текст, r in self.кути_мітки:
            V, A, B = (self._см(self._xy(q)) for q in (o, a, b))
            φa = _кут_градуси(V, A); θ = (_кут_градуси(V, B) - φa) % 360; β = φa + θ / 2
            w, h = розмір(текст)
            всередині, ззовні = [], []
            for d in [0.06 + 0.06 * i for i in range(28)]:
                for δ in [0] + [s_ * k for k in (4, 8, 12, 16, 20, 25, 30, 40, 50, 60, 75, 90) for s_ in (1, -1)]:
                    u = (math.cos(math.radians(β + δ)), math.sin(math.radians(β + δ)))
                    відст = r + d + abs(u[0]) * w / 2 + abs(u[1]) * h / 2
                    c_ = (V[0] + відст * u[0], V[1] + відст * u[1])
                    кути_ = [(_кут_градуси(V, (c_[0] + sx * w / 2, c_[1] + sy * h / 2)) - φa) % 360 for sx in (-1, 1) for sy in (-1, 1)]
                    (всередині if max(кути_) < θ and d <= 1.3 else ззовні).append((c_, d + 0.004 * abs(δ)))
            промені = [(V, A), (V, B)]
            c = найкращий(всередині, w, h, V, промені)
            if c is None:
                c = найкращий(ззовні, w, h, V, промені)
                self.попередження.append("мітка кута %s при вершині %s -- поза кутом" % (текст, o))
            поставити(c or всередині[0][0], w, h, текст, r"\small")

        # 2) назви точок: біля точки, бажаний бік дешевший
        for n, де, текст in self.мітки:
            P = self._см(self._xy(n)); w, h = розмір(текст)
            бажаний = НАПРЯМКИ.get(де, 90)
            кандидати = []
            for d in (0.04, 0.08, 0.12, 0.17, 0.23, 0.3, 0.38):
                for q in range(0, 360, 15):
                    u = (math.cos(math.radians(q)), math.sin(math.radians(q)))
                    відст = 0.07 + d + abs(u[0]) * w / 2 + abs(u[1]) * h / 2
                    кут_від_бажаного = min((q - бажаний) % 360, (бажаний - q) % 360)
                    кандидати.append(((P[0] + відст * u[0], P[1] + відст * u[1]), d + 0.0015 * кут_від_бажаного))
            свої = [(self._см(p), self._см(q)) for p, q, _ in self.відрізки if self._см(p) == P or self._см(q) == P]
            c = найкращий(кандидати, w, h, P, свої)
            if c is None: self.попередження.append("назва точки %s не має вільного місця" % n)
            поставити(c or кандидати[0][0], w, h, текст, r"\small")

        # 3) довжини: біля середини відрізка, з бажаного боку
        for a, b, текст, де in self.довжини:
            P, Q = self._см(self._xy(a)), self._см(self._xy(b)); w, h = розмір(текст, 0.9)
            M = ((P[0] + Q[0]) / 2, (P[1] + Q[1]) / 2); t = _одиничний(P, Q); nrm = (-t[1], t[0])
            бажаний = НАПРЯМКИ.get(де, 90); ub = (math.cos(math.radians(бажаний)), math.sin(math.radians(бажаний)))
            бік = 1 if nrm[0] * ub[0] + nrm[1] * ub[1] >= 0 else -1
            кандидати = []
            for s_, штраф in ((бік, 0), (-бік, 0.3)):
                for d in (0.05, 0.1, 0.18, 0.3, 0.45):
                    for вздовж in (0, 0.2, -0.2, 0.4, -0.4, 0.6, -0.6):
                        відст = d + abs(nrm[0]) * w / 2 + abs(nrm[1]) * h / 2
                        кандидати.append(((M[0] + t[0] * вздовж + s_ * nrm[0] * відст, M[1] + t[1] * вздовж + s_ * nrm[1] * відст),
                                          d + 0.3 * abs(вздовж) + штраф))
            c = найкращий(кандидати, w, h, M, [(P, Q)])
            if c is None: self.попередження.append("довжина %s не має вільного місця" % текст)
            поставити(c or кандидати[0][0], w, h, текст, r"\footnotesize")
        return вузли

    def tex(self):
        вузли = self._розмістити()
        for q in self.попередження: print("  увага, рисунок:", q)
        return "\n".join(self.s + вузли + [r"\end{tikzpicture}"])

    def вміст(self):
        """лише команди без tikzpicture -- щоб домалювати в чужий рисунок із тим самим масштабом"""
        return "\n".join(self.s[1:] + self._розмістити())


def _перетинаються(p1, p2, p3, p4):
    """чи перетинаються відрізки p1p2 і p3p4 (строго, без дотику кінцями)"""
    def орієнт(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    d1, d2, d3, d4 = орієнт(p3, p4, p1), орієнт(p3, p4, p2), орієнт(p1, p2, p3), орієнт(p1, p2, p4)
    return d1 * d2 < -1e-12 and d3 * d4 < -1e-12


def _спільний_кінець(відрізок, свої):
    P, Q = відрізок
    return any(math.dist(P, A) < 1e-6 and math.dist(Q, B) < 1e-6 or math.dist(P, B) < 1e-6 and math.dist(Q, A) < 1e-6
               or math.dist(P, A) < 1e-6 or math.dist(Q, A) < 1e-6 for A, B in свої)


def _одиничний(p, q):
    d = math.dist(p, q) or 1.0
    return ((q[0] - p[0]) / d, (q[1] - p[1]) / d)


# ---------------------------------------------------------------- косокутна проєкція (глибина -- вгору праворуч)
def пр(p, k=0.45, фі=40):
    x, y, z = p
    return (x + k * y * math.cos(math.radians(фі)), z + k * y * math.sin(math.radians(фі)))


def тіло(вершини, ребра, приховані, підписи, scale=1.0, пунктир_додаткові=(), додаткові=()):
    """вершини {назва: (x, y, z)}; ребра -- пари назв; приховані -- ребра пунктиром; додаткові -- (a, b) суцільні"""
    r = Рис(scale).точки({n: пр(p) for n, p in вершини.items()})
    for a, b in ребра:
        r.лінія(a, b, стиль="thick, dashed" if (a, b) in приховані or (b, a) in приховані else "thick")
    for a, b in пунктир_додаткові: r.лінія(a, b, стиль="dashed")
    for a, b in додаткові: r.лінія(a, b, стиль="thick")
    r.підписи(підписи)
    return r


КУБ = {"A": (0, 0, 0), "B": (1, 0, 0), "C": (1, 1, 0), "D": (0, 1, 0),
       "A1": (0, 0, 1), "B1": (1, 0, 1), "C1": (1, 1, 1), "D1": (0, 1, 1)}
РЕБРА_КУБА = [("A", "B"), ("B", "C"), ("C", "D"), ("D", "A"), ("A1", "B1"), ("B1", "C1"), ("C1", "D1"), ("D1", "A1"),
              ("A", "A1"), ("B", "B1"), ("C", "C1"), ("D", "D1")]


def куб(a=2.4, **kw):
    """куб ABCDA1B1C1D1: A -- спереду ліворуч унизу, D -- невидима вершина (ребра з неї пунктиром)"""
    вершини = {n: tuple(a * q for q in p) for n, p in КУБ.items()}
    return тіло(вершини, РЕБРА_КУБА, [("D", "A"), ("C", "D"), ("D", "D1")],
                {"A": "below left", "B": "below right", "C": "right", "D": "above left", "A1": "left", "B1": "above left",
                 "C1": "above right", "D1": "above left"}, **kw)


def піраміда4(a=2.6, h=2.8, **kw):
    """правильна чотирикутна піраміда SABCD з висотою SO; D -- невидима вершина основи"""
    вершини = {"A": (0, 0, 0), "B": (a, 0, 0), "C": (a, a, 0), "D": (0, a, 0), "S": (a / 2, a / 2, h), "O": (a / 2, a / 2, 0)}
    ребра = [("A", "B"), ("B", "C"), ("C", "D"), ("D", "A"), ("S", "A"), ("S", "B"), ("S", "C"), ("S", "D")]
    return тіло(вершини, ребра, [("C", "D"), ("D", "A"), ("S", "D")],
                {"A": "below left", "B": "below right", "C": "right", "D": "left", "S": "above", "O": "below right"}, **kw)


def піраміда3(a=2.8, h=2.6, **kw):
    """правильна трикутна піраміда SABC: B -- спереду, ребро AC -- позаду (пунктир)"""
    вершини = {"A": (0, 0, 0), "C": (a, 0, 0), "B": (a / 2, -a * math.sqrt(3) / 2, 0)}
    o = (a / 2, -a * math.sqrt(3) / 6, 0)
    вершини.update({"O": o, "S": (o[0], o[1], h)})
    ребра = [("A", "B"), ("B", "C"), ("C", "A"), ("S", "A"), ("S", "B"), ("S", "C")]
    return тіло(вершини, ребра, [("C", "A")], {"A": "left", "B": "below", "C": "right", "S": "above", "O": "above right"}, **kw)
