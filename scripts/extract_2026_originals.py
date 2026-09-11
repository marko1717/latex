#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Витягує ОРИГІНАЛЬНІ завдання НМТ-2026 (17 сесій x 22) у scripts/data/originals_2026.json.

Джерела (копії в archive/джерела_2026/):
  збірник/оригінали/Оригінали_Розділ_1..6.tex  -- тиждень 1 (23.05-5.06), лише оригінали, відповіді в кінці файла
  збірник/розділи/Розділ_1..6.tex               -- звідти беремо короткі розв'язки (розділ «РОЗВ'ЯЗКИ ОРИГІНАЛЬНИХ ЗАДАЧ»)
  збірник/збірник_НМТ_тиждень.tex               -- звідти 3.06 №5 (відсутнє в Розділах)
  збірник/nmt_2026_bank.json                    -- банк: перевірка відповідей, назви тем
  сесії/<дата>/завдання.tex (+ завдання_key.tex) -- повні варіанти 8.06-19.06
Запуск: python3 scripts/extract_2026_originals.py
"""
import re, json, os, sys, glob, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "archive", "джерела_2026")
ZBD = os.path.join(SRC, "збірник")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "scripts", "data", "originals_2026.json")
WEEK1 = ["23.05","30.05","1.06","2.06","3.06","4.06","5.06"]
ORDER = WEEK1 + ["8.06","9.06","10.06","11.06","12.06","15.06","16.06","17.06","18.06","19.06"]

def balanced(s, i):
    d = 0; j = i
    while j < len(s):
        c = s[j]
        if c == '\\': j += 2; continue
        if c == '{': d += 1
        elif c == '}':
            d -= 1
            if d == 0: return j
        j += 1
    raise ValueError("unbalanced")

def clean_chunk(t):
    out = []
    for l in t.split("\n"):
        ls = l.strip()
        if ls in ("\\newpage", "\\clearpage"): continue
        if re.fullmatch(r"%\s*[=\-]{3,}\s*", ls): continue
        if re.fullmatch(r"%\s*={3,}\s*(№\s*\d+|Завдання\s*\d+|ЗАВДАННЯ\s*\d+)\s*={3,}\s*", ls): continue
        out.append(l.rstrip())
    t = "\n".join(out).strip("\n")
    return re.sub(r"\n{3,}", "\n\n", t)

def plain(t):
    p = re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", " [РИС] ", t, flags=re.S)
    p = re.sub(r"\\nmtyear\{\d+\}", "", p)
    p = re.sub(r"\\(answerTable|answerTableTall)\{", " | ОПЦІЇ: {", p)
    p = re.sub(r"\\(begin|end)\{[a-z*]+\}(\[[^\]]*\])?(\{[0-9.]*\\textwidth\})?", " ", p)
    p = re.sub(r"\\(vspace|hspace)\*?\{[^}]*\}", " ", p)
    p = re.sub(r"\\[a-zA-Z]+\*?", "", p)
    p = re.sub(r"[{}$&~^_]", " ", p)
    p = re.sub(r"\[[0-9.]+(cm|pt|em)\]", " ", p)
    p = re.sub(r"%.*", "", p)
    return re.sub(r"\s+", " ", p).strip()

def task_type(n): return "single" if n <= 15 else ("matching" if n <= 18 else "input")

TITLE_RE = re.compile(r"сесія\s+([0-9.]+),\s*завдання\s*№\s*(\d+)")

def blocks_of(body):
    """[(title, block_text)] для кожного \\taskBlock{...}"""
    starts = list(re.finditer(r"^\\taskBlock\{([^\n]*)\}\s*$", body, flags=re.M))
    bounds = [m.start() for m in starts] + [len(body)]
    res = []
    for k, m in enumerate(starts):
        block = body[m.end():bounds[k+1]]
        cut = re.search(r"^\\(typeTitle|chapterTitle|sectionTitle)\{", block, flags=re.M)
        if cut: block = block[:cut.start()]
        res.append((m.group(1), block))
    return res

# ---------------- тиждень 1: оригінали
def parse_originals(path):
    s = open(path, encoding="utf-8").read().split("\\begin{document}", 1)[1]
    body, _, anstext = s.partition("\\chapterTitle{ВІДПОВІДІ}")
    answers = {int(m.group(1)): m.group(2).strip() for m in re.finditer(r"\\textbf\{(\d+)\.\}~(.+?)\s*(?:\\\\)?\s*$", anstext, flags=re.M)}
    ansitems = re.findall(r"\\ansitem\{([^}]*)\}", anstext)   # розділ 6: відповіді у порядку блоків
    res = {}
    for k, (title, block) in enumerate(blocks_of(body)):
        mm = TITLE_RE.search(title)
        if not mm: continue
        key = (mm.group(1), int(mm.group(2)))
        topic = re.sub(r"\s*---\s*сесія.*$", "", title).strip()
        sb = re.search(r"\\solbtn\{(\d+)\}", block)
        sol = None
        if sb:
            orig = block[:sb.start()]; N = int(sb.group(1)); ans = answers.get(N)
        else:   # блок без кнопки: оригінал + inline \solution{}, відповідь -- k-тий \ansitem
            si = block.find("\\solution{")
            if si >= 0:
                j = balanced(block, si + len("\\solution")); sol = block[si+len("\\solution{"):j].strip(); orig = block[:si]
            else: orig = block
            N = None; ans = ansitems[k] if k < len(ansitems) else None
        if key in res: print("  пропущено повторний блок:", title); continue
        res[key] = dict(latex=clean_chunk(orig), topic=topic, answer=ans, solution=sol, src=os.path.basename(path), N=N)
    return res

# ---------------- тиждень 1: розв'язки з Розділів
def parse_rozdily_solutions(path):
    s = open(path, encoding="utf-8").read().split("\\begin{document}", 1)[1]
    body, _, tail = s.partition("\\chapterTitle{РОЗВ")
    num_of = {}
    for title, block in blocks_of(body):
        mm = TITLE_RE.search(title); t = re.search(r"\\hypertarget\{task:(\d+)\}", block)
        if mm and t: num_of.setdefault((mm.group(1), int(mm.group(2))), int(t.group(1)))
    sols = {}
    for m in re.finditer(r"\\hypertarget\{sol:(\d+)\}\{\}(.*?)\\end\{tcolorbox\}", tail, flags=re.S):
        N = int(m.group(1)); box = m.group(2)
        q = re.search(r"\\textbf\{Задача №\d+\.\}\\quad\s*(.*?)\s*\\par\\vspace\{0\.1cm\}\\hfill\\hyperlink", box, flags=re.S)
        if q: sols[N] = re.sub(r"\s+", " ", q.group(1)).strip()
    return {key: sols[N] for key, N in num_of.items() if N in sols}

# ---------------- тиждень 1: збірник (для 3.06 №5)
def parse_zbirnyk(path):
    s = open(path, encoding="utf-8").read().split("\\begin{document}", 1)[1].split("\\chapterTitle{ВІДПОВІДІ}")[0]
    res = {}
    for title, block in blocks_of(s):
        mm = TITLE_RE.search(title)
        if not mm: continue
        key = (mm.group(1), int(mm.group(2)))
        si = block.find("\\solution{")
        if si < 0: continue
        j = balanced(block, si + len("\\solution"))
        if key in res: continue
        res[key] = dict(latex=clean_chunk(block[:si]), topic=re.sub(r"\s*---\s*сесія.*$", "", title).strip(),
                        solution=block[si+len("\\solution{"):j].strip(), src=os.path.basename(path))
    return res

# ---------------- тижні 2-3: файли сесій (новий формат)
STD_NAMES = {"answerTable","answerTableTall","instructionBox","sectionTitle","task","nmtAnswerBox","matchingGrid","taskBlock",
             "zadtask","zadnum","ansitem","nmtyear","solution","chapterTitle","typeTitle","ansTheme","ansType","solbtn","answerBox"}
STD_COLORS = {"mainGreen","yearOrange","yearcolor","titleBg","instrBg","instrBorder","headerblue","titlecolor","answercolor","tablecolor"}
def session_extras(path):
    """нестандартні \\definecolor / \\newcommand / \\def з преамбули файла сесії (потрібні рисункам)"""
    pre = open(path, encoding="utf-8").read().split("\\begin{document}", 1)[0]
    out = []
    for m in re.finditer(r"\\definecolor\{([^}]*)\}\{[^}]*\}\{[^}]*\}", pre):
        if m.group(1) not in STD_COLORS: out.append(m.group(0))
    for m in re.finditer(r"\\(newcommand|renewcommand|def)\*?\s*\{?\\([a-zA-Z0-9]+)\}?", pre):
        name = m.group(2)
        if name in STD_NAMES or name in ("arraystretch", "tabcolsep"): continue
        j = m.end()
        while True:
            k = re.match(r"\s*\[[^\]]*\]", pre[j:])
            if k: j += k.end()
            else: break
        k = pre.find("{", j)
        if k < 0: continue
        out.append(pre[m.start():balanced(pre, k)+1])
    return out

def parse_answers(text):
    ans = {}
    for m in re.finditer(r"\\textbf\{(\d+)\.\}[\\~\s]*(?:quad)?\s*(.+?)\s*(?:\\\\(\[[^\]]*\])?)?\s*$", text, flags=re.M):
        ans[int(m.group(1))] = m.group(2).strip()
    return ans

def parse_session(sess):
    path = os.path.join(SRC, "сесії", sess, "завдання.tex")
    full = open(path, encoding="utf-8").read()
    body = full.split("\\begin{document}", 1)[1]
    answers = {}
    if "% ===== ВІДПОВІДІ" in body:
        body, anstext = body.split("% ===== ВІДПОВІДІ", 1); answers = parse_answers(anstext)
    keyp = os.path.join(SRC, "сесії", sess, "завдання_key.tex")
    if os.path.exists(keyp):
        kt = open(keyp, encoding="utf-8").read()
        if "% ===== ВІДПОВІДІ" in kt: answers.update(parse_answers(kt.split("% ===== ВІДПОВІДІ", 1)[1]))
    body = body.split("\\end{document}")[0]
    keep = [l for l in body.split("\n") if not l.strip().startswith(("\\instructionBox{","\\chapterTitle{","\\sectionTitle{","\\thispagestyle","\\vspace*{"))]
    body = "\n".join(keep)
    starts = []
    for m in re.finditer(r"\\zadtask\{|\\zadnum\b", body):
        pos = m.start(); ls = body.rfind("\n", 0, pos) + 1; start = ls
        if m.group(0) == "\\zadnum":
            pe = ls - 1; pls = body.rfind("\n", 0, pe) + 1 if pe > 0 else 0
            prev = body[pls:pe].strip() if pe > 0 else ""
            if prev.startswith("\\begin{minipage}"):
                start = pls; pe2 = pls - 1; pls2 = body.rfind("\n", 0, pe2) + 1 if pe2 > 0 else 0
                prev2 = body[pls2:pe2].strip() if pe2 > 0 else ""
                if prev2.rstrip("%").strip() == "\\noindent": start = pls2
        starts.append(start)
    chunks = [body[starts[i]:(starts[i+1] if i+1 < len(starts) else len(body))] for i in range(len(starts))]
    if len(chunks) != 22: print(f"УВАГА {sess}: знайдено {len(chunks)} завдань")
    ex = session_extras(path)
    res = []
    for i, c in enumerate(chunks, 1):
        c = clean_chunk(c)
        extras = [d for d in ex if ("tikzpicture" in c) or
                  (re.search(r"\\(?:definecolor|newcommand|renewcommand|def)\*?\s*\{?\\?([a-zA-Z0-9]+)", d).group(1) in c)]
        res.append((i, c, answers.get(i), extras))
    return res

def norm_answer(a):
    if a is None: return None
    a = re.sub(r"[\$~\s]", "", a); a = a.replace("--", "-").replace("\\,", "").replace("{,}", ",")
    return a

def main():
    tasks = []
    bank = json.load(open(os.path.join(ZBD, "nmt_2026_bank.json"), encoding="utf-8"))
    bk = {(e["session"], e["position"]): e for e in bank if e["role"] == "original"}
    orig = {}
    for f in sorted(glob.glob(os.path.join(ZBD, "оригінали", "*.tex"))): orig.update(parse_originals(f))
    sols = {}
    for f in sorted(glob.glob(os.path.join(ZBD, "розділи", "*.tex"))): sols.update(parse_rozdily_solutions(f))
    zb = parse_zbirnyk(os.path.join(ZBD, "збірник_НМТ_тиждень.tex"))
    print("оригінали:", len(orig), " розв'язків із Розділів:", len(sols), " у збірнику:", len(zb))
    mism = []
    for sess in WEEK1:
        for n in range(1, 23):
            key = (sess, n); e = bk.get(key, {})
            if key in orig:
                v = orig[key]; ans = v["answer"]; sol = sols.get(key) or v.get("solution") or e.get("solution_latex"); src = v["src"]
                if ans and e.get("answer") and norm_answer(ans) != norm_answer(e["answer"]): mism.append((key, ans, e["answer"]))
                if not ans: ans = e.get("answer")
            elif key in zb:
                v = zb[key]; ans = e.get("answer"); sol = v["solution"]; src = v["src"]; print("взято зі збірника:", key, v["topic"])
            else:
                print("ВІДСУТНЄ:", key); continue
            tasks.append(dict(id=f"2026-{sess}-{n:02d}", session=sess, n=n, type=task_type(n), latex=v["latex"], answer=ans, solution=sol,
                              json_topic=e.get("topic"), json_section=e.get("section"), json_section_name=e.get("section_name"),
                              topic_zb=v["topic"], restored=False, source=src, has_figure="tikzpicture" in v["latex"], plain=plain(v["latex"]), extra_defs=[]))
    if mism:
        print("Відповіді оригіналів, що не збігаються з банком (узято з оригіналів):")
        for k, a, b in mism: print("   ", k, "оригінали:", a, "| банк:", b)
    for sess in ORDER[7:]:
        for i, c, a, extras in parse_session(sess):
            tasks.append(dict(id=f"2026-{sess}-{i:02d}", session=sess, n=i, type=task_type(i), latex=c, answer=a, solution=None,
                              json_topic=None, json_section=None, json_section_name=None, topic_zb=None, restored=False,
                              source=f"сесії/{sess}/завдання.tex", has_figure="tikzpicture" in c, plain=plain(c), extra_defs=extras))
    json.dump(tasks, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("разом:", len(tasks), dict(collections.Counter(t["session"] for t in tasks)))
    print("з відповіддю:", sum(1 for t in tasks if t["answer"]), " з розв'язком:", sum(1 for t in tasks if t["solution"]), " з рисунком:", sum(1 for t in tasks if t["has_figure"]))

if __name__ == "__main__":
    main()
