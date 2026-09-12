# -*- coding: utf-8 -*-
"""Витягти завдання НМТ 2023--2025 із PDF «НМТ23-25» (bbox-розбір)."""
import json, re, os, sys, collections
S = os.path.dirname(os.path.abspath(__file__))
W = json.load(open(S + "/words.json", encoding="utf-8"))

SESS_2023 = [(5,"07.06.23-1"),(9,"07.06.23-2"),(13,"08.06.23-1"),(17,"08.06.23-2"),(21,"09.06.23-1"),(26,"09.06.23-2"),
             (30,"12.06.23-1"),(34,"12.06.23-2"),(37,"13.06.23-1"),(41,"13.06.23-2"),(45,"14.06.23-1"),(48,"14.06.23-2"),
             (52,"15.06.23-1"),(56,"15.06.23-2"),(60,"16.06.23-1"),(64,"16.06.23-2"),(68,"19.06.23-1"),(72,"19.06.23-2"),
             (77,"20.06.23-1"),(81,"20.06.23-2"),(86,None)]
SESS_2024 = [(95,"18.05.24"),(101,"25.05.24"),(108,"01.06.24"),(114,"03.06.24"),(120,"04.06.24"),(126,"05.06.24"),
             (132,"06.06.24"),(138,"07.06.24"),(145,"10.06.24"),(151,"11.06.24"),(158,"12.06.24"),(164,"13.06.24"),
             (170,"14.06.24"),(176,"17.06.24"),(182,"18.06.24"),(188,"19.06.24"),(194,"20.06.24"),(200,"21.06.24"),(206,None)]
SESS_2025 = [(214,"17.05.25",219),(220,"24.05.25",224),(226,"31.05.25",230),(232,"02.06.25",236),(238,"03.06.25",242),
             (244,"04.06.25",248),(250,"05.06.25",254),(256,"06.06.25",261),(262,"09.06.25",267),(268,"10.06.25",272),
             (274,"11.06.25",278),(280,"12.06.25",284),(286,"13.06.25",292),(293,"16.06.25",297),(299,"17.06.25",304),
             (305,"18.06.25",310),(311,"19.06.25",316)]

SKIP = ("t.me/", "instagram.com", "STUDINFO", "Телеграм-канали")
def body_words(pi):
    """слова сторінки без водяного знака, колонтитулів і кнопок"""
    res = []
    for x0, y0, x1, y1, w in W[pi-1]:
        if (y1 - y0) > 20: continue                 # водяний знак / кнопка
        if y0 < 50 or y0 > 800: continue            # колонтитули
        res.append((x0, y0, x1, y1, w))
    return res

def lines_of(pi):
    ws = sorted(body_words(pi), key=lambda t: (round(t[1] / 4), t[0]))
    out, cur, cy = [], [], None
    for x0, y0, x1, y1, w in ws:
        if cy is None or abs(y0 - cy) <= 4:
            cur.append((x0, w)); cy = y0 if cy is None else cy
        else:
            out.append((cy, cur)); cur = [(x0, w)]; cy = y0
    if cur: out.append((cy, cur))
    res = []
    for y, items in out:
        items.sort()
        txt = ""
        prevx = None
        for x, w in items:
            if prevx is not None and x - prevx > 24: txt += "   "
            elif txt: txt += " "
            txt += w
            prevx = x
        if any(s in txt for s in SKIP): continue
        res.append((y, items[0][0], txt))
    return res

WIDE_ABCD = re.compile(r"^А\s+Б\s+В\s+Г\s+Д$")
def option_header_rows(pi):
    """рядки «А Б В Г Д» одноваріантного завдання (широко рознесені), а не сітка відповідності"""
    res = []
    for y, x, t in lines_of(pi):
        if WIDE_ABCD.match(re.sub(r"\s+", " ", t).strip()):
            xs = [w[0] for w in body_words(pi) if abs(w[1] - y) <= 4]
            if xs and max(xs) - min(xs) > 250: res.append(y)
    return res

def answer_buttons(pi):
    return sorted(y0 for x0, y0, x1, y1, w in W[pi-1]
                  if "Відповід" in w and (y1 - y0) > 30 and x0 < 75)

def collect(first, last, mode):
    """повертає список текстів завдань сесії"""
    seq = []            # (page, y, x, text)
    marks = []          # (page, y) -- початок завдання
    for pi in range(first, last + 1):
        ls = lines_of(pi)
        if any("ПРАВИЛЬНІ ВІДПОВІДІ" in t.upper() for _, _, t in ls[:4]): continue
        for y, x, t in ls: seq.append((pi, y, x, t))
        if mode == "num":
            for y, x, t in ls:
                if re.match(r"^\d{1,2}\.(\s|$)", t) and x < 70: marks.append((pi, y - 2))
        else:
            for by in answer_buttons(pi): marks.append((pi, by - 12))
            # у виданні 2023 не в кожного завдання є кнопка: додатковий орієнтир --
            # перший рядок основної колонки після блоку варіантів «А Б В Г Д» або після «Відповідь:»
            ends = option_header_rows(pi) + [y for y, x, t in ls if re.fullmatch(r"Відповідь:?", t.strip())]
            for ey in ends:
                nxt = [y for y, x, t in ls if y > ey + 8 and 80 <= x <= 95]
                if nxt: marks.append((pi, nxt[0] - 2))
    marks.sort()
    ded = []                                  # орієнтири, ближчі ніж 10 pt, -- це той самий початок
    for m in marks:
        if ded and ded[-1][0] == m[0] and abs(m[1] - ded[-1][1]) < 10: continue
        ded.append(m)
    marks = ded
    tasks, spans = [], []
    for k, m in enumerate(marks):
        nxt = marks[k+1] if k+1 < len(marks) else (10**6, 0)
        body = [t for (pi, y, x, t) in seq if (pi, y) >= m and (pi, y) < nxt]
        tasks.append("\n".join(body).strip())
        ys = [y for (pi, y, x, t) in seq if (pi, y) >= m and (pi, y) < nxt and pi == m[0]]
        spans.append(dict(page=m[0], y0=m[1], y1=(nxt[1] if nxt[0] == m[0] else (max(ys) + 30 if ys else m[1] + 250))))
    return tasks, spans

def build():
    data = []
    def add(year, label, first, last, mode):
        tasks, spans = collect(first, last, mode)
        data.append(dict(year=year, session=label, pages=[first, last], tasks=tasks, spans=spans))
    for k in range(len(SESS_2023)-1): add("2023", SESS_2023[k][1], SESS_2023[k][0], SESS_2023[k+1][0]-1, "btn")
    for k in range(len(SESS_2024)-1): add("2024", SESS_2024[k][1], SESS_2024[k][0], SESS_2024[k+1][0]-1, "num")
    for k, (f, lab, ap) in enumerate(SESS_2025):
        last = SESS_2025[k+1][0] - 1 if k + 1 < len(SESS_2025) else 317
        add("2025", lab, f, last, "num")
    return data

if __name__ == "__main__":
    data = build()
    json.dump(data, open(S + "/tasks_raw.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    bad = [(d["year"], d["session"], len(d["tasks"])) for d in data if len(d["tasks"]) != 22]
    print("сесій:", len(data), "| завдань:", sum(len(d["tasks"]) for d in data))
    print("не 22 завдання:", bad if bad else "немає")
