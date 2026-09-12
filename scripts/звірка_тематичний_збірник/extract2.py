# -*- coding: utf-8 -*-
"""Розбір тематичного збірника «Числа і вирази, 234 завдання НМТ 2022--2025»."""
import json, re, os, collections
S = os.path.dirname(os.path.abspath(__file__))
W = json.load(open(S + "/words.json", encoding="utf-8"))

SKIP = ("t.me/", "abitmath", "abitblog")
def body(pi):
    out = []
    for x0, y0, x1, y1, w in W[pi]:
        h = y1 - y0
        if h > 19: continue                    # водяний знак / заголовки
        if y0 < 45 or y0 > 790: continue
        out.append((x0, y0, x1, y1, w))
    return out

def lines(pi):
    ws = sorted(body(pi), key=lambda t: (round(t[1] / 5), t[0]))
    res, cur, cy = [], [], None
    for x0, y0, x1, y1, w in ws:
        if cy is None or abs(y0 - cy) <= 5: cur.append((x0, w)); cy = y0 if cy is None else cy
        else: res.append((cy, cur)); cur = [(x0, w)]; cy = y0
    if cur: res.append((cy, cur))
    out = []
    for y, items in res:
        items.sort(); txt = ""; px = None
        for x, w in items:
            if px is not None and x - px > 22: txt += "   "
            elif txt: txt += " "
            txt += w; px = x
        if any(s in txt for s in SKIP): continue
        out.append((y, items[0][0], txt))
    return out

LABEL = re.compile(r"НМТ\s*(20\d\d),?\s*(основна|додаткова|демоваріант)")

def task_marks():
    """номери завдань: цифри в лівому полі, відібрані як зростаюча послідовність 1..234"""
    cand = []
    for pi, p in enumerate(W):
        for x0, y0, x1, y1, w in p:
            if 50 <= x0 <= 88 and 7 <= (y1 - y0) <= 22 and re.fullmatch(r"\d{1,3}", w):
                cand.append((pi, y0, int(w)))
    cand.sort(key=lambda t: (t[0], t[1]))
    seq, exp = [], 1
    for c in cand:
        if c[2] == exp: seq.append(c); exp += 1
    return seq

def build():
    seq = []
    for pi in range(len(W)):
        for y, x, t in lines(pi): seq.append((pi, y, x, t))
    marks = task_marks()
    tasks = []
    for k, m in enumerate(marks):
        nxt = (marks[k+1][0], marks[k+1][1] - 3) if k + 1 < len(marks) else (10**6, 0)
        txt = "\n".join(t for (pi, y, x, t) in seq if (pi, y) >= (m[0], m[1] - 3) and (pi, y) < nxt)
        flat = re.sub(r"\s+", " ", txt)
        lab = LABEL.search(flat)
        tasks.append(dict(num=m[2], page=m[0] + 1, y0=m[1], y1=(nxt[1] if nxt[0] == m[0] else 800),
                          year=lab.group(1) if lab else None, sess=lab.group(2) if lab else None,
                          text=LABEL.sub(" ", txt).strip()))
    return tasks

if __name__ == "__main__":
    t = build()
    json.dump(t, open(S + "/tasks2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("знайдено завдань:", len(t))
    print("за роками/сесіями:", collections.Counter((x["year"], x["sess"]) for x in t))
