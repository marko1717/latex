# -*- coding: utf-8 -*-
"""Підсумкове зіставлення PDF «НМТ23-25» із базою: слова + варіанти + формули."""
import json, re, os, sys, difflib, collections
S = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, S)
from compare import load_base, sig, words, norm
from opts import pdf_options, base_options
from verify import statement
from flat import flatten, tokens, tok_sim
from classify import guess_section, guess_topic1
from match import SECTIONS, SEC_OF, unit_of_path

def numbers(t): return set(re.findall(r"\d+(?:[.,]\d+)?", norm(t)))

def prep_base():
    base = load_base()
    for b in base:
        b["wset"] = set(words(b["raw"])); b["nset"] = numbers(b["raw"])
        b["sigs"] = sig(b["raw"]); b["opts"] = base_options(b["raw"])
        b["ftok"] = collections.Counter(tokens(flatten(b["raw"])))
        b["unit"] = unit_of_path(b["topic"]); b["sec"] = SEC_OF.get(b["unit"], ("?", "?"))[0]
        b["phr"] = " ".join(re.findall(r"[а-яіїєґ']{4,}", norm(b["raw"])))
    inv = collections.defaultdict(set)
    for i, b in enumerate(base):
        for w in b["wset"] | b["nset"]: inv[w].add(i)
    return base, inv

def evaluate(t, base, inv, year):
    ws = set(words(t)); ns = numbers(t); sg = sig(t); po = [x for x in pdf_options(t) if x]
    ft = collections.Counter(tokens(flatten(statement(t))))
    phr = [" ".join(re.findall(r"[а-яіїєґ']{4,}", norm(statement(t)))[i:i+4])
           for i in range(0, max(0, len(re.findall(r"[а-яіїєґ']{4,}", norm(statement(t)))) - 3))]
    cand = collections.Counter()
    for w in ws | ns:
        for i in inv.get(w, ()): cand[i] += 1
    top = [i for i, _ in cand.most_common(80)]
    same = [i for i in top if base[i]["year"] == year]
    top = same + [i for i in top if i not in set(same)]
    best = None
    for i in top[:80]:
        b = base[i]
        s_w = len(ws & b["wset"]) / max(1, min(len(ws), len(b["wset"]))) if ws and b["wset"] else 0.0
        s_s = difflib.SequenceMatcher(None, sg, b["sigs"]).ratio()
        s_o = (len(set(po) & set(b["opts"])) / max(1, min(len(po), len([x for x in b["opts"] if x])))
               ) if len(po) >= 3 and len([x for x in b["opts"] if x]) >= 3 else None
        s_f = (sum((ft & b["ftok"]).values()) / max(1, sum(ft.values()))) if sum(ft.values()) >= 5 else None
        s_p = 1.0 if any(p in b["phr"] for p in phr) else 0.0
        s_n = len(ns & b["nset"]) / max(1, min(len(ns), len(b["nset"]))) if ns and b["nset"] else None
        ev = []
        # сама лише збіжність слів ненадійна: формулювання НМТ повторюються з іншими числами
        if s_p and (s_n is None or s_n >= 0.6 or (s_f is not None and s_f >= 0.7)): ev.append("фраза+числа")
        if s_o is not None and s_o >= 0.6: ev.append("варіанти")
        if s_f is not None and s_f >= 0.8: ev.append("формула")
        conf = (0.45 * s_w + 0.25 * s_s + 0.3 * (s_o or 0)) + 0.25 * s_p + 0.2 * (s_f or 0)
        rec = dict(i=i, conf=round(conf, 3), ev=ev, s_w=round(s_w, 2), s_s=round(s_s, 2),
                   s_n=None if s_n is None else round(s_n, 2), s_p=s_p,
                   s_o=None if s_o is None else round(s_o, 2), s_f=None if s_f is None else round(s_f, 2),
                   byear=b["year"], topic=b["topic"], unit=b["unit"], sec=b["sec"])
        if best is None or (len(ev), conf) > (len(best["ev"]), best["conf"]): best = rec
    return best

if __name__ == "__main__":
    base, inv = prep_base()
    pdf = json.load(open(S + "/tasks_raw.json", encoding="utf-8"))
    out = []
    for sess in pdf:
        for n, t in enumerate(sess["tasks"], 1):
            b = evaluate(t, base, inv, sess["year"]) or dict(i=None, conf=0, ev=[], topic=None, unit=None, sec=None, byear=None)
            out.append(dict(year=sess["year"], session=sess["session"], n=n, text=t,
                            gsec=guess_section(t), **{k: v for k, v in b.items() if k != "i"}))
    json.dump(out, open(S + "/final.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    c = collections.Counter(len(o["ev"]) for o in out)
    print("усього:", len(out), "| доказів на завдання:", dict(c))
    print("без жодного доказу:", sum(1 for o in out if not o["ev"]))
