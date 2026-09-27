# -*- coding: utf-8 -*-
"""Перевірка властивостей функцій для каталогів типів НМТ (scripts/типи_*): область визначення, парність,
монотонність, знак, найбільше значення, спільні точки з прямою чи ламаною, координатні чверті. Графік без формули --
через монотонний сплайн з рисунки.py (екстремуми лише у вузлах, значення -- точні дроби)."""
from sympy import Symbol, S, Eq, FiniteSet, ImageSet, ConditionSet, Union, Interval, solveset, simplify, diff, lambdify, sympify
from sympy.calculus.util import continuous_domain
from рисунки import сплайн, Fr
X = Symbol("x", real=True)


def D(f):
    return continuous_domain(sympify(f), X, S.Reals)


def парна(f):
    return D(f.subs(X, -X)) == D(f) and simplify(f.subs(X, -X) - f) == 0


def непарна(f):
    return D(f.subs(X, -X)) == D(f) and simplify(f.subs(X, -X) + f) == 0


def _монотонна(f, I, знак):
    """строго монотонна на I: похідна не змінює знака, нулі похідної -- окремі точки"""
    if not I.is_subset(D(f)): return False
    d = diff(f, X)
    нулі = solveset(Eq(d, 0), X, I)
    return solveset(знак * d < 0, X, I).is_empty is True and (нулі.is_empty is True or isinstance(нулі, FiniteSet))


def зростає(f, I=S.Reals): return _монотонна(f, I, 1)
def спадає(f, I=S.Reals): return _монотонна(f, I, -1)


def лише_додатні(f):
    return solveset(f <= 0, X, D(f)).is_empty is True


def кількість(s):
    """кількість точок множини розв'язків: число або «безліч»"""
    if s.is_empty: return 0
    if isinstance(s, FiniteSet): return len(s)
    if isinstance(s, (ImageSet, Interval)) or (isinstance(s, Union) and any(isinstance(a, (ImageSet, Interval)) for a in s.args)):
        return "безліч"
    raise ValueError("не вдалося полічити розв'язки: %s" % s)


def корені_чисельно(h, a=-40, b=40, n=80001):
    """кількість коренів h(x)=0 на [a; b] за зміною знака (для рівнянь, які sympy не розв'язує, напр. 2^x=kx+b;
    дотик без зміни знака так не видно -- для зразків беремо лише перетини)"""
    fn, знаки = lambdify(X, h, "math"), []
    for i in range(n):
        x0 = a + (b - a) * i / (n - 1)
        try: y0 = fn(x0)
        except (ValueError, ZeroDivisionError, OverflowError): знаки.append(None); continue
        знаки.append(None if isinstance(y0, complex) else (y0 > 0) - (y0 < 0))
    k = sum(1 for u in знаки if u == 0)
    k += sum(1 for u, w in zip(знаки, знаки[1:]) if u and w and u != w)
    return k


def спільні(f, g, M=S.Reals):
    """кількість спільних точок графіків y=f і y=g (на множині M); трансцендентні рівняння -- чисельно"""
    s = solveset(Eq(f, g), X, M.intersect(D(f)).intersect(D(g)))
    if isinstance(s, ConditionSet): return корені_чисельно(f - g)
    return кількість(s)


def спільні_з_ламаною(f, вершини):
    """кількість спільних точок графіка y=f з ламаною (вершини -- цілі чи раціональні координати)"""
    точки = set()
    for (x1, y1), (x2, y2) in zip(вершини, вершини[1:]):
        if x1 == x2:                                       # вертикальна ланка
            if x1 in D(f) and min(y1, y2) <= f.subs(X, x1) <= max(y1, y2): точки.add((sympify(x1), simplify(f.subs(X, x1))))
            continue
        g = sympify(y1) + sympify(y2 - y1) / (x2 - x1) * (X - x1)
        I = Interval(min(x1, x2), max(x1, x2))
        if simplify(f - g) == 0 and I.is_subset(D(f)): return "безліч"
        s = solveset(Eq(f, g), X, I.intersect(D(f)))
        assert isinstance(s, FiniteSet) or s.is_empty, ("ланка", (x1, y1), (x2, y2), s)
        точки |= {(simplify(x0), simplify(g.subs(X, x0))) for x0 in s}
    return len(точки)


def чверті(f, a=-40, b=40, n=16001):
    """номери координатних чвертей, у яких лежать точки графіка (точки на осях не рахуються)"""
    fn, q = lambdify(X, f, "math"), set()
    for i in range(n):
        x0 = a + (b - a) * i / (n - 1)
        try: y0 = fn(x0)
        except (ValueError, ZeroDivisionError, OverflowError): continue
        if isinstance(y0, complex) or y0 != y0 or abs(x0) < 1e-9 or abs(y0) < 1e-9: continue
        q.add(1 if x0 > 0 and y0 > 0 else 2 if y0 > 0 else 3 if x0 < 0 else 4)
    return frozenset(q)


class Графік:
    """графік без формули: вузли з цілими координатами, між ними -- монотонний сплайн (рисунки.плавна)"""

    def __init__(self, pts):
        self.pts, self.f = [tuple(p) for p in pts], сплайн(pts)
        self.a, self.b = Fr(pts[0][0]), Fr(pts[-1][0])

    def сітка(self, a=None, b=None, крок=Fr(1, 20)):
        a, b = Fr(self.a if a is None else a), Fr(self.b if b is None else b)
        return [a + крок * k for k in range(int((b - a) / крок) + 1)]

    def найбільше(self): return max(y for _, y in self.pts)
    def найменше(self): return min(y for _, y in self.pts)

    def точки_екстремуму(self, вид):
        """внутрішні вузли, де зростання змінюється спаданням (max) чи навпаки (min)"""
        p = self.pts
        return [p[k][0] for k in range(1, len(p) - 1)
                if (p[k][1] > p[k - 1][1] and p[k][1] > p[k + 1][1]) == (вид == "max") and
                (p[k][1] - p[k - 1][1]) * (p[k + 1][1] - p[k][1]) < 0]

    def нулі(self):
        """нулі у вузлах і по одному на кожному відрізку між вузлами, де значення змінюють знак"""
        p, z = self.pts, [x for x, y in self.pts if y == 0]
        for (xa, ya), (xb, yb) in zip(p, p[1:]):
            if ya * yb < 0:
                lo, hi = Fr(xa), Fr(xb)
                for _ in range(40):
                    mid = (lo + hi) / 2
                    if (self.f(mid) < 0) == (ya < 0): lo = mid
                    else: hi = mid
                z.append(float(lo))
        return sorted(z)

    def зростає(self, a=None, b=None):
        v = [self.f(t) for t in self.сітка(a, b)]
        return all(u < w for u, w in zip(v, v[1:]))

    def спадає(self, a=None, b=None):
        v = [self.f(t) for t in self.сітка(a, b)]
        return all(u > w for u, w in zip(v, v[1:]))

    def парна(self):
        return self.a == -self.b and all(self.f(-t) == self.f(t) for t in self.сітка(0, self.b))

    def лише_додатні(self): return self.найменше() > 0
