# -*- coding: utf-8 -*-
"""Схематичні рисунки просторових тіл без підписів, як у НМТ 2025--2026 (два тіла поруч): многогранник в
ортогональній проєкції (поворот і нахил) з автоматично визначеними невидимими ребрами (пунктир), циліндр, конус, куля, півкуля. Розміри на рисунку --
схематичні; відповідь рахують з умови, не з рисунка."""
import math

АЗИМУТ, НАХИЛ = -25, 25                                       # поворот навколо осі z і нахил погляду (градуси)


def вид(p, азимут=АЗИМУТ, нахил=НАХИЛ):
    """ортогональна проєкція: тіло повернуто на азимут навколо осі z, дивимося спереду й трохи згори"""
    a, b = math.radians(азимут), math.radians(нахил)
    x, y, z = p
    xr, yr = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
    return (xr, z * math.cos(b) + yr * math.sin(b))


def напрям(азимут=АЗИМУТ, нахил=НАХИЛ):
    """напрям погляду (від глядача в глибину) у координатах тіла: грань видима, якщо зовнішня нормаль має з ним від'ємний добуток"""
    a, b = math.radians(азимут), math.radians(нахил)
    return (math.cos(b) * math.sin(a), math.cos(b) * math.cos(a), -math.sin(b))


def ч(v):
    return ("%.3f" % v).rstrip("0").rstrip(".") if abs(v) > 5e-4 else "0"


def _різн(a, b): return tuple(x - y for x, y in zip(a, b))
def _вект(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def _скал(a, b): return sum(x * y for x, y in zip(a, b))


def многогранник(вершини, грані, стиль="thick", додаткові=(), азимут=АЗИМУТ, нахил=НАХИЛ):
    """вершини {назва: (x, y, z)}, грані -- списки назв по контуру; опуклий многогранник. Грань видима, якщо її зовнішня
    нормаль напрямлена до глядача; ребро невидиме, якщо обидві його грані невидимі.
    додаткові -- [(a, b, стиль)] відрізки поверх (висота, апофема тощо)"""
    ц = tuple(sum(p[i] for p in вершини.values()) / len(вершини) for i in range(3))
    видима, ребра = {}, {}
    for k, g in enumerate(грані):
        p0, p1, p2 = (вершини[g[0]], вершини[g[1]], вершини[g[2]])
        n = _вект(_різн(p1, p0), _різн(p2, p0))
        if _скал(n, _різн(p0, ц)) < 0: n = tuple(-x for x in n)      # зовнішня нормаль
        видима[k] = _скал(n, напрям(азимут, нахил)) < -1e-9
        for a, b in zip(g, g[1:] + g[:1]):
            ребра.setdefault(frozenset((a, b)), []).append(k)
    xy = {n: вид(p, азимут, нахил) for n, p in вершини.items()}
    s = []
    for e, fs in ребра.items():
        a, b = sorted(e)
        прихов = not any(видима[k] for k in fs)
        s.append(r"\draw[%s%s] (%s,%s) -- (%s,%s);" % (стиль, ", dashed" if прихов else "", ч(xy[a][0]), ч(xy[a][1]), ч(xy[b][0]), ч(xy[b][1])))
    for a, b, st in додаткові:
        s.append(r"\draw[%s] (%s,%s) -- (%s,%s);" % (st, ч(xy[a][0]), ч(xy[a][1]), ч(xy[b][0]), ч(xy[b][1])))
    return "\n".join(s)


def призма(основа, h, **kw):
    """пряма призма: основа -- список (x, y) у площині z = 0 по контуру"""
    n = len(основа)
    в = {"A%d" % i: (x, y, 0) for i, (x, y) in enumerate(основа)}
    в.update({"B%d" % i: (x, y, h) for i, (x, y) in enumerate(основа)})
    грані = [["A%d" % i for i in range(n)], ["B%d" % i for i in range(n)]] + \
            [["A%d" % i, "A%d" % ((i + 1) % n), "B%d" % ((i + 1) % n), "B%d" % i] for i in range(n)]
    return многогранник(в, грані, **kw)


def піраміда(основа, вершина, висота=False, **kw):
    """піраміда: основа -- (x, y) у площині z = 0, вершина -- (x, y, h); висота=True -- пунктирна висота"""
    n = len(основа)
    в = {"A%d" % i: (x, y, 0) for i, (x, y) in enumerate(основа)}
    в["S"] = вершина
    грані = [["A%d" % i for i in range(n)]] + [["A%d" % i, "A%d" % ((i + 1) % n), "S"] for i in range(n)]
    дод = ()
    if висота:
        в["O"] = (вершина[0], вершина[1], 0)
        дод = [("S", "O", "dashed")]
    return многогранник(в, грані, додаткові=дод, **kw)


def правильний(n, R, поворот=0.0):
    """вершини правильного n-кутника з центром (0, 0) і радіусом описаного кола R"""
    return [(R * math.cos(поворот + 2 * math.pi * i / n), R * math.sin(поворот + 2 * math.pi * i / n)) for i in range(n)]


def _ry(r): return r * math.sin(math.radians(НАХИЛ))       # коло в горизонтальній площині -- еліпс
def _h(h): return h * math.cos(math.radians(НАХИЛ))        # висота в тому самому масштабі, що й у многогранників (вид())


def _основа_кругла(r, ry, y=0.0):
    return (r"\draw[thick, dashed] (%s,%s) arc (180:0:%s and %s);" % (ч(-r), ч(y), ч(r), ч(ry)) + "\n" +
            r"\draw[thick] (%s,%s) arc (180:360:%s and %s);" % (ч(-r), ч(y), ч(r), ч(ry)))


def циліндр(r=1.2, h=3.0, вісь=False):
    ry, h = _ry(r), _h(h)
    s = [r"\draw[thick] (0,%s) ellipse (%s and %s);" % (ч(h), ч(r), ч(ry)), _основа_кругла(r, ry),
         r"\draw[thick] (%s,0) -- (%s,%s);" % (ч(-r), ч(-r), ч(h)), r"\draw[thick] (%s,0) -- (%s,%s);" % (ч(r), ч(r), ч(h))]
    if вісь: s.append(r"\draw[dashed] (0,0) -- (0,%s);" % ч(h))
    return "\n".join(s)


def конус(r=1.2, h=3.2, висота=False, радіус=False):
    ry, h = _ry(r), _h(h)
    s = [_основа_кругла(r, ry), r"\draw[thick] (%s,0) -- (0,%s) -- (%s,0);" % (ч(-r), ч(h), ч(r))]
    if висота: s.append(r"\draw[dashed] (0,0) -- (0,%s);" % ч(h))
    if радіус: s.append(r"\draw[dashed] (0,0) -- (%s,0);" % ч(r))
    return "\n".join(s)


def півкуля(r=1.3):
    ry = _ry(r)
    return "\n".join([_основа_кругла(r, ry), r"\draw[thick] (%s,0) arc (180:0:%s);" % (ч(-r), ч(r))])


def куля(r=1.3):
    ry = _ry(r)
    return "\n".join([r"\draw[thick] (0,0) circle (%s);" % ч(r), _основа_кругла(r, ry)])


def поруч(*тіла, крок=4.2, scale=0.6):
    """кілька тіл в одному рисунку, зліва направо; тіла -- рядки TikZ з центром основи в (0, 0) або (зсув, рядок)"""
    s = [r"\begin{tikzpicture}[scale=%s, line join=round]" % scale]
    x = 0.0
    for т in тіла:
        зсув, код = (т if isinstance(т, tuple) else (крок, т))
        s.append(r"\begin{scope}[shift={(%s,0)}]" % ч(x) + "\n" + код + "\n" + r"\end{scope}")
        x += зсув
    s.append(r"\end{tikzpicture}")
    return "\n".join(s)
