# -*- coding: utf-8 -*-
"""Зіставлення тематичного збірника «Числа і вирази» з базою."""
import json, re, os, sys, difflib, collections
S = os.path.dirname(os.path.abspath(__file__))
P1 = os.path.join(os.path.dirname(S), "pdf23")
sys.path.insert(0, P1); sys.path.insert(0, S)
from compare import load_base, sig, words, norm
from opts import base_options, canon
from flat import flatten, tokens
from match import unit_of_path, SEC_OF

ABCD = re.compile(r"^\s*А\s+Б\s+[ВвB]\s+[ГгR]\s+[ДдA]\s*$")
def pdf2_options(text):
    ls = text.split("\n")
    for i, l in enumerate(ls):
        t = re.sub(r"\s+", " ", l).strip()
        if re.fullmatch(r"[АA]\s+[БB]\s+[ВвB]\s+[ГгRr]\s+[ДдAa]", t):
            for r in ls[i+1:i+4]:
                p = [x for x in re.split(r"\s{3,}", r.strip()) if x]
                if len(p) >= 3: return [canon(x) for x in p][:5]
    return []

def numbers(t): return set(re.findall(r"\d+(?:[.,]\d+)?", norm(t)))

def main():
    base = load_base()
    for b in base:
        b["wset"] = set(words(b["raw"])); b["nset"] = numbers(b["raw"])
        b["sigs"] = sig(b["raw"]); b["opts"] = [x for x in base_options(b["raw"]) if x]
        b["ftok"] = collections.Counter(tokens(flatten(b["raw"])))
        b["unit"] = unit_of_path(b["topic"]); b["sec"] = SEC_OF.get(b["unit"], ("?",))[0]
        b["phr"] = " ".join(re.findall(r"[а-яіїєґ']{4,}", norm(b["raw"])))
    inv = collections.defaultdict(set)
    for i, b in enumerate(base):
        for w in b["wset"] | b["nset"]: inv[w].add(i)
    tasks = json.load(open(S + "/tasks2.json", encoding="utf-8"))
    out = []
    for t in tasks:
        txt = t["text"]; ws = set(words(txt)); ns = numbers(txt); sg = sig(txt)
        po = [x for x in pdf2_options(txt) if x]
        ft = collections.Counter(tokens(flatten(txt)))
        wl = re.findall(r"[а-яіїєґ']{4,}", norm(txt))
        phr = [" ".join(wl[i:i+4]) for i in range(0, max(0, len(wl) - 3))]
        cand = collections.Counter()
        for w in ws | ns:
            for i in inv.get(w, ()): cand[i] += 1
        top = [i for i, _ in cand.most_common(80)]
        best = None
        for i in top:
            b = base[i]
            s_w = len(ws & b["wset"]) / max(1, min(len(ws), len(b["wset"]))) if ws and b["wset"] else 0.0
            s_s = difflib.SequenceMatcher(None, sg, b["sigs"]).ratio()
            s_o = len(set(po) & set(b["opts"])) / max(1, min(len(po), len(b["opts"]))) if len(po) >= 3 and len(b["opts"]) >= 3 else None
            s_f = sum((ft & b["ftok"]).values()) / max(1, sum(ft.values())) if sum(ft.values()) >= 5 else None
            s_n = len(ns & b["nset"]) / max(1, min(len(ns), len(b["nset"]))) if ns and b["nset"] else None
            s_p = 1.0 if any(p in b["phr"] for p in phr) else 0.0
            ev = []
            if s_p and (s_n is None or s_n >= 0.6 or (s_f is not None and s_f >= 0.7)): ev.append("фраза+числа")
            if s_o is not None and s_o >= 0.6: ev.append("варіанти")
            if s_f is not None and s_f >= 0.8: ev.append("формула")
            conf = 0.45 * s_w + 0.25 * s_s + 0.3 * (s_o or 0) + 0.25 * s_p + 0.2 * (s_f or 0)
            rec = dict(conf=round(conf, 3), ev=ev, topic=b["topic"], unit=b["unit"], sec=b["sec"],
                       byear=b["year"], s_o=None if s_o is None else round(s_o, 2),
                       s_f=None if s_f is None else round(s_f, 2), s_w=round(s_w, 2))
            if best is None or (len(ev), conf) > (len(best["ev"]), best["conf"]): best = rec
        out.append(dict(num=t["num"], page=t["page"], year=t["year"], sess=t["sess"], text=txt,
                        **(best or dict(conf=0, ev=[], topic=None, unit=None, sec=None, byear=None))))
    json.dump(out, open(S + "/matched2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    c = collections.Counter((o["year"], o["sess"], bool(o["ev"])) for o in out)
    print("підтверджено:", sum(1 for o in out if o["ev"]), "з", len(out))
    for k in sorted(c, key=lambda x: (str(x[0]), str(x[1]))): print("  ", k, c[k])

if __name__ == "__main__": main()
