# -*- coding: utf-8 -*-
"""Структура варіанта за даними сесій: яка категорія на якій позиції (1--22) в НМТ 2023--2026.

Позиції беруться з каталогу: для 2026 -- номер у сесії з коментаря бази, для 2023--2025 --
номер у PDF-посібнику (для 2023 номери відновлено за порядком завдань, вони менш надійні).
Для кожного року порядок 15 тестових слотів підбирається так, щоб сумарна частота
«категорія на своїй позиції» була найбільшою (задача про призначення, перебір Угорським методом).

    python3 scripts/варіант_нмт/структура.py            # таблиця частот і порядок для кожного року
"""
import os, sys, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from спільне import *


def позиції(cat):
    """(рік, сесія, позиція, категорія) для всіх завдань каталогу з відомою позицією"""
    out = []
    for r in cat:
        c = r.get("категорія") or r.get("орієнтовна_категорія")
        if r.get("сесія_2026"):
            _, s, n = r["сесія_2026"].split("-"); out.append(("2026", s, int(n), c))
        for x in r.get("довідки", []):
            if x.get("сесія") and x.get("рік_pdf") == r.get("рік"):
                out.append((r["рік"], x["сесія"], x["номер"], c))
    return out


def hungarian(cost):
    """мінімальне призначення для квадратної матриці (O(n^3))"""
    n = len(cost); INF = float("inf")
    u, v, p, way = [0] * (n + 1), [0] * (n + 1), [0] * (n + 1), [0] * (n + 1)
    for i in range(1, n + 1):
        p[0] = i; j0 = 0; minv = [INF] * (n + 1); used = [False] * (n + 1)
        while True:
            used[j0] = True; i0 = p[j0]; delta = INF; j1 = 0
            for j in range(1, n + 1):
                if not used[j]:
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]: minv[j] = cur; way[j] = j0
                    if minv[j] < delta: delta = minv[j]; j1 = j
            for j in range(n + 1):
                if used[j]: u[p[j]] += delta; v[j] -= delta
                else: minv[j] -= delta
            j0 = j1
            if p[j0] == 0: break
        while True:
            j1 = way[j0]; p[j0] = p[j1]; j0 = j1
            if j0 == 0: break
    res = [0] * n
    for j in range(1, n + 1): res[p[j] - 1] = j - 1
    return res   # рядок i -> стовпець res[i]


def порядок(rows, years):
    tests = [c for c, (t, _) in КАТЕГОРІЇ.items() if t == "single"]
    cnt = collections.defaultdict(collections.Counter)
    for y, s, n, c in rows:
        if y in years and 1 <= n <= 15 and c in tests: cnt[n][c] += 1
    cost = [[-cnt[pos + 1][c] for pos in range(15)] for c in tests]
    a = hungarian(cost)
    order = [None] * 15
    for i, c in enumerate(tests): order[a[i]] = c
    return order, cnt


def main():
    cat = json.load(open(КАТАЛОГ, encoding="utf-8"))
    rows = позиції(cat)
    print("позицій із категорією:", len(rows), dict(collections.Counter(r[0] for r in rows)))
    for years in (("2026",), ("2025",), ("2024",), ("2025", "2026")):
        order, cnt = порядок(rows, set(years))
        print("\n== %s" % "+".join(years))
        for pos, c in enumerate(order, 1):
            tot = sum(cnt[pos].values())
            print("%2d %-26s %3d/%-3d   інші: %s" % (pos, c, cnt[pos][c], tot,
                  ", ".join("%s %d" % (k, v) for k, v in cnt[pos].most_common(4) if k != c)))
    # відповідності й коротка відповідь
    for n in range(16, 23):
        c = collections.Counter(r[3] for r in rows if r[2] == n and r[0] in ("2025", "2026"))
        print(n, c.most_common(4))


if __name__ == "__main__":
    main()
