# -*- coding: utf-8 -*-
"""Зіставлення завдань PDF із базою + класифікація за розділами."""
import json, re, os, sys, glob, difflib, collections
S = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, S)
from compare import load_base, sig, words, norm, REPO
from opts import pdf_options, base_options, opt_score

SECTIONS = [("1","Числа і вирази",["1","2","3","4","5","7","26","30a"]),
            ("2","Рівняння і нерівності",["6","8","9","19","22","23","27","28a","29","31","32","43"]),
            ("3","Функції",["20","21","24","25","28b","30b","33","34"]),
            ("4","Планіметрія",["10","11","12","13","14","15","16","17"]),
            ("5","Стереометрія",["18","38","39","40","41","42"]),
            ("6","Комбінаторика, теорія ймовірності, статистика",["35","36","37"])]
def unit_of_path(p):
    m = re.match(r"^(\d+)\.", p)
    if not m: return "?"
    u = m.group(1)
    if u == "28": return "28b" if "вирази" in p else "28a"
    if u == "30": return "30a" if "вирази" in p else "30b"
    return u
SEC_OF = {u: (n, nm) for n, nm, us in SECTIONS for u in us}

def numbers(t):
    return set(re.findall(r"\d+(?:[.,]\d+)?", norm(t)))

def score(a_sig, a_words, a_nums, b, a_opts=None):
    if not a_words: 
        s_w = 0.0
    else:
        common = len(a_words & b["wset"])
        s_w = common / max(1, min(len(a_words), len(b["wset"])))
    s_n = len(a_nums & b["nset"]) / max(1, min(len(a_nums), len(b["nset"]))) if a_nums and b["nset"] else 0.0
    s_s = difflib.SequenceMatcher(None, a_sig, b["sig"]).ratio()
    base_score = 0.5 * s_w + 0.2 * s_n + 0.3 * s_s
    s_o = opt_score(a_opts or [], b["opts"]) if a_opts else None
    if s_o is None: return base_score, None
    # збіг варіантів відповіді -- найсильніший доказ тотожності завдання
    return max(base_score, 0.45 * base_score + 0.55 * s_o), s_o

def build_index(base):
    for b in base:
        b["wset"] = set(words(b["raw"])); b["nset"] = numbers(b["raw"])
        b["unit"] = unit_of_path(b["topic"]); b["sec"] = SEC_OF.get(b["unit"], ("?", "?"))[0]
        b["opts"] = base_options(b["raw"])
    inv = collections.defaultdict(set)
    for i, b in enumerate(base):
        for w in b["wset"] | b["nset"]: inv[w].add(i)
    return inv

def best_match(t, base, inv, year=None):
    ws = set(words(t)); ns = numbers(t); s = sig(t); op = pdf_options(t)
    cand = collections.Counter()
    for w in ws | ns:
        for i in inv.get(w, ()): cand[i] += 1
    top = [i for i, _ in cand.most_common(60)]
    if year: top = [i for i in top if base[i]["year"] in (year, "?")] or top
    res = []
    for i in top:
        sc, so = score(s, ws, ns, base[i], op)
        res.append((sc, so, i))
    res.sort(key=lambda r: -r[0])
    return res[:3]

if __name__ == "__main__":
    base = load_base(); inv = build_index(base)
    pdf = json.load(open(S + "/tasks_raw.json", encoding="utf-8"))
    out = []
    for sess in pdf:
        for n, t in enumerate(sess["tasks"], 1):
            m = best_match(t, base, inv, sess["year"])
            top = m[0] if m else (0.0, None, None)
            i0 = top[2]
            out.append(dict(year=sess["year"], session=sess["session"], n=n, text=t,
                            score=round(top[0], 3), opt=None if top[1] is None else round(top[1], 3),
                            topic=base[i0]["topic"] if i0 is not None else None,
                            unit=base[i0]["unit"] if i0 is not None else None,
                            sec=base[i0]["sec"] if i0 is not None else None,
                            alt=[(round(sc, 3), base[i]["topic"]) for sc, so, i in m[1:]]))
    json.dump(out, open(S + "/matched.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    h = collections.Counter()
    for o in out:
        h["0.8+" if o["score"] >= .8 else "0.65-0.8" if o["score"] >= .65 else "0.5-0.65" if o["score"] >= .5 else "<0.5"] += 1
    print("усього завдань PDF:", len(out)); print("розподіл схожості:", dict(h))
