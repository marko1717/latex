# -*- coding: utf-8 -*-
"""Спільні рисунки TikZ для каталогів типів НМТ (scripts/типи_*): осі з сіткою, точки з мітками, ламана й плавна
крива через цілі точки (монотонний сплайн Фрітча -- Карлсона, записаний кривими Безьє) та її точні значення."""
from fractions import Fraction as Fr
from sympy import Rational as R


def осі(x0, x1, y0, y1, scale=0.5, одиниці=True):
    """сітка з осями й позначками 0 і 1"""
    s = [r"\begin{tikzpicture}[scale=%s]" % scale,
         r"\draw[gray!35, very thin] (%s,%s) grid (%s,%s);" % (x0, y0, x1, y1),
         r"\draw[->] (%s,0) -- (%s,0) node[below left, font=\footnotesize] {$x$};" % (x0, x1 + 0.5),
         r"\draw[->] (0,%s) -- (0,%s) node[below left, font=\footnotesize] {$y$};" % (y0, y1 + 0.5),
         r"\node[below left, font=\scriptsize] at (0,0) {$0$};"]
    if одиниці:
        s.append(r"\node[below, font=\scriptsize] at (1,0) {$1$}; \node[left, font=\scriptsize] at (0,1) {$1$};")
    return "\n".join(s)


ТОЧКА = r"\node[circle, fill, inner sep=1.5pt] at (%s,%s) {};"      # вузол не масштабується разом із рисунком


def ламана(pts, кінці=True, стиль="very thick"):
    s = r"\draw[%s] " % стиль + " -- ".join("(%s,%s)" % p for p in pts) + ";"
    if кінці:
        s += "\n" + ТОЧКА % pts[0] + " " + ТОЧКА % pts[-1]
    return s


def точки(d, де=None):
    """{назва: (x, y)} або {назва: (x, y, положення мітки)}"""
    return "\n".join(r"\node[circle, fill, inner sep=1.5pt, label={[font=\small, inner sep=1pt]%s:$%s$}] at (%s,%s) {};" % (
        xy[2] if len(xy) > 2 else (де or "above right"), n, xy[0], xy[1]) for n, xy in d.items())


КІНЕЦЬ = r"\end{tikzpicture}"


def нахили(pts):
    """нахили у вузлах монотонного кубічного сплайна (Фрітч -- Карлсон, як pchip у MATLAB і scipy)"""
    xs, ys, n = [Fr(p[0]) for p in pts], [Fr(p[1]) for p in pts], len(pts)
    h = [xs[k + 1] - xs[k] for k in range(n - 1)]
    d = [(ys[k + 1] - ys[k]) / h[k] for k in range(n - 1)]
    if n == 2: return [d[0], d[0]]
    m = [Fr(0)] * n
    for k in range(1, n - 1):
        if d[k - 1] * d[k] > 0:                  # де змінюється напрям, нахил 0: там і лише там екстремум
            w1, w2 = 2 * h[k] + h[k - 1], h[k] + 2 * h[k - 1]
            m[k] = (w1 + w2) / (w1 / d[k - 1] + w2 / d[k])

    def край(h0, h1, d0, d1):
        q = ((2 * h0 + h1) * d0 - h0 * d1) / (h0 + h1)
        if q * d0 <= 0: return Fr(0)
        return 3 * d0 if d0 * d1 < 0 and abs(q) > 3 * abs(d0) else q
    m[0], m[-1] = край(h[0], h[1], d[0], d[1]), край(h[-1], h[-2], d[-1], d[-2])
    return m


def сплайн(pts):
    """функція x -> значення монотонного сплайна через вузли (точно, дробами)"""
    m = нахили(pts)

    def f(x0):
        x0 = Fr(x0)
        for k in range(len(pts) - 1):
            (xa, ya), (xb, yb) = pts[k][:2], pts[k + 1][:2]
            if xa <= x0 <= xb:
                h = Fr(xb - xa); s = (x0 - xa) / h
                return ((2 * s ** 3 - 3 * s ** 2 + 1) * ya + (s ** 3 - 2 * s ** 2 + s) * h * m[k]
                        + (3 * s ** 2 - 2 * s ** 3) * yb + (s ** 3 - s ** 2) * h * m[k + 1])
        raise ValueError(x0)
    return f


def плавна(pts, стиль="very thick", кінці=True):
    """графік без формули: гладка крива через вузли з цілими координатами (кубічні криві Безьє з монотонного сплайна).
    Між сусідніми вузлами крива монотонна й не виходить за їхні значення, екстремуми -- лише у вузлах (там дотична
    горизонтальна), тож нулі, проміжки монотонності, екстремуми й множина значень читаються з вузлів.
    Вбудоване \\draw plot[smooth] чи hobby так не вміють: крива «перелітає» вузол, вершина зсувається з цілої точки."""
    перевірити_форму(pts)
    m = нахили(pts)

    def ч(q): return ("%.3f" % float(q)).rstrip("0").rstrip(".")
    s = r"\draw[%s] (%s,%s)" % (стиль, pts[0][0], pts[0][1])
    for k in range(len(pts) - 1):
        (xa, ya), (xb, yb) = pts[k], pts[k + 1]
        h = Fr(xb - xa) / 3
        s += r" .. controls (%s,%s) and (%s,%s) .. (%s,%s)" % (ч(xa + h), ч(ya + m[k] * h), ч(xb - h), ч(yb - m[k + 1] * h), xb, yb)
    s += ";"
    if кінці: s += "\n" + ТОЧКА % tuple(pts[0]) + " " + ТОЧКА % tuple(pts[-1])
    return s


def перевірити_форму(pts, крок=Fr(1, 40)):
    """самоперевірка: на кожному відрізку між вузлами сплайн монотонний і не виходить за значення вузлів"""
    f = сплайн(pts)
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        попереднє, x0 = Fr(ya), Fr(xa)
        while x0 < xb:
            x0 = min(x0 + крок, Fr(xb)); y0 = f(x0)
            assert min(ya, yb) <= y0 <= max(ya, yb) and (y0 - попереднє) * (yb - ya) >= 0, ("форма сплайна", pts, x0)
            попереднє = y0


def міра(f, x0, x1, умова, крок=Fr(1, 100)):
    """сумарна довжина проміжків на $[x_0;x_1]$, де умова(f(x)) справджується (межі -- у вузлах сітки)"""
    n, k = 0, 0
    while x0 + крок * (k + Fr(1, 2)) < x1:
        if умова(f(x0 + крок * (k + Fr(1, 2)))): n += 1
        k += 1
    return R((n * крок).numerator, (n * крок).denominator)
