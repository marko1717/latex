# -*- coding: utf-8 -*-
"""Рисунки TikZ для каталогу типів з геометрії: іменовані точки, многокутники, позначки кутів і довжин,
косокутна проєкція тіл (куб, прямокутний паралелепіпед, піраміди) з пунктиром невидимих ребер.

Рисунок схематичний, як у НМТ; відповіді рахуються не з рисунка, а з даних умови (у спец.py)."""
import re
import math


def назва(n):
    """A1 -> A_1 (мітка на рисунку)"""
    return re.sub(r"^([A-Za-z])(\d+)$", r"\1_\2", n)


class Рис:
    def __init__(self, scale=1.0):
        self.s = [r"\begin{tikzpicture}[scale=%s, line join=round, line cap=round]" % scale]

    def точки(self, d):
        """{назва: (x, y)} -> \\coordinate; назви на кшталт A1 стають мітками A_1"""
        for n, (xx, yy) in d.items():
            self.s.append(r"\coordinate (%s) at (%.3f,%.3f);" % (n, xx, yy))
        return self

    def лінія(self, *назви, стиль="thick", замкнена=False):
        self.s.append(r"\draw[%s] " % стиль + " -- ".join("(%s)" % n for n in назви) + (" -- cycle;" if замкнена else ";"))
        return self

    def підписи(self, d):
        """{назва: положення} або {назва: (положення, текст)}"""
        for n, де in d.items():
            текст = назва(n)
            if isinstance(де, tuple): де, текст = де
            self.s.append(r"\node[%s, font=\small, inner sep=2pt] at (%s) {$%s$};" % (де, n, текст))
        return self

    def кут(self, a, o, b, текст="", r=0.45, дуги=1):
        """дуга кута aob (проти годинникової стрілки від a до b) з підписом"""
        for k in range(дуги):
            self.s.append(r"\pic[draw, angle radius=%.2fcm%s] {angle = %s--%s--%s};" % (
                r + 0.07 * k, (r", angle eccentricity=1.55, pic text={\small $%s$}" % текст) if текст and k == 0 else "", a, o, b))
        return self

    def прямий(self, a, o, b):
        self.s.append(r"\pic[draw, angle radius=0.2cm] {right angle = %s--%s--%s};" % (a, o, b))
        return self

    def точка(self, *назви):
        for n in назви: self.s.append(r"\node[circle, fill, inner sep=1.3pt] at (%s) {};" % n)   # вузол не масштабується
        return self

    def довжина(self, a, b, текст, де="above", зсув=0.0):
        """підпис довжини посередині відрізка ab"""
        self.s.append(r"\path (%s) -- (%s) node[midway, %s, font=\footnotesize, inner sep=2pt%s] {$%s$};" % (
            a, b, де, (", yshift=%.2fcm" % зсув) if зсув else "", текст))
        return self

    def сире(self, t):
        self.s.append(t)
        return self

    def tex(self):
        return "\n".join(self.s + [r"\end{tikzpicture}"])

    def вміст(self):
        """лише команди без tikzpicture -- щоб домалювати в чужий рисунок (наприклад, у сітку з осями)"""
        return "\n".join(self.s[1:])


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
                {"A": "below left", "B": "below right", "C": "right", "D": "left", "A1": "left", "B1": "above left",
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
