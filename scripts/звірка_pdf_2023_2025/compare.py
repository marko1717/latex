# -*- coding: utf-8 -*-
"""Зіставити завдання з PDF «НМТ23-25» із базою НМТ_по_темах_латех."""
import json, re, os, glob, difflib, collections, sys
S = os.path.dirname(os.path.abspath(__file__))
REPO = glob.glob(os.path.expanduser("~/Desktop/*Mac/НМТ_по_темах_латех"))[0]

# ---------- нормалізація ----------
GREEK = {"alpha":"α","beta":"β","gamma":"γ","pi":"π","varphi":"φ","phi":"φ","lambda":"λ","omega":"ω","theta":"θ"}
def norm(t):
    t = re.sub(r"%[^\n]*", " ", t)
    t = re.sub(r"\\(?:begin|end)\{[^}]*\}", " ", t)
    t = re.sub(r"\\(?:tikzpicture|includegraphics|node|draw|coordinate|fill|pic|foreach|addplot|axis)\b[^\n]*", " ", t)
    t = re.sub(r"\\(?:d?frac|sqrt|text|mathrm|mbox|textbf|textit|zadtask|zadnum|nmtyear|answerTable\w*|matchingGrid|nmtAnswerBox|solution|ifshowsolutions|fi|par|noindent|hfill|quad|nbvspace|vspace|nopagebreak|nmtnobreak|penalty|centering|flushright|flushleft|item|cdot|left|right|displaystyle|limits|lg|ln|log|sin|cos|tg|ctg|arcsin|arccos|arctg)\b", " ", t)
    for k, v in GREEK.items(): t = t.replace("\\" + k, v)
    t = re.sub(r"\\[a-zA-Z]+", " ", t)
    t = t.replace("$", " ").replace("{", " ").replace("}", " ")
    t = t.replace("«", " ").replace("»", " ").replace("<<", " ").replace(">>", " ")
    t = t.replace("’", "'").replace("'", "'").replace("–", "-").replace("—", "-").replace("−", "-")
    t = re.sub(r"[^\w\u0400-\u04FFα-ωΑ-Ω.,;:=<>+\-*/()\[\]|]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t

def words(t):
    """слова-носії змісту: українські слова довші за 3 літери + числа"""
    w = re.findall(r"[а-яіїєґ']{4,}|\d+[.,]?\d*", norm(t))
    return w

def sig(t):
    return " ".join(words(t))

# ---------- база ----------
UNIT_SECTION = json.load(open(os.path.join(S, "unit_section.json"), encoding="utf-8")) if os.path.exists(os.path.join(S, "unit_section.json")) else {}
def load_base():
    base = []
    files = sorted(glob.glob(os.path.join(REPO, "*/завдання*.tex"))) + sorted(glob.glob(os.path.join(REPO, "*/*/завдання.tex")))
    for f in files:
        s = open(f, encoding="utf-8").read()
        try: body = s[s.index("\\begin{document}"):]
        except ValueError: continue
        topic = os.path.relpath(f, REPO)
        for b in re.findall(r"\\begin\{samepage\}(.*?)\\end\{samepage\}", body, re.S):
            yr = re.search(r"\\nmtyear\{(\d{4})\}", b)
            base.append(dict(topic=topic, year=yr.group(1) if yr else "?", raw=b, sig=sig(b)))
    return base

if __name__ == "__main__":
    base = load_base()
    print("завдань у базі:", len(base), "| за роками:", collections.Counter(b["year"] for b in base))
    json.dump([{k: v for k, v in b.items() if k != "raw"} for b in base],
              open(os.path.join(S, "base_index.json"), "w", encoding="utf-8"), ensure_ascii=False)
