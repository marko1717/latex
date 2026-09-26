# -*- coding: utf-8 -*-
"""Бібліотека завдань-аналогів: приймання результатів генерації, компіляція, перегляд.

    python3 scripts/варіант_нмт/аналоги.py додати РЕЗУЛЬТАТ.json ЗРАЗКИ_DIR   # додати перевірені аналоги
    python3 scripts/варіант_нмт/аналоги.py перегляд [ТЕКА]                    # PDF з усіма аналогами бібліотеки

Кожен аналог перед прийняттям компілюється окремо (XeLaTeX); якщо компіляція падає,
аналог позначається «перевірено: false» з текстом помилки і у варіанти не потрапляє.
"""
import os, re, sys, json, subprocess, tempfile, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from спільне import *


def завантажити():
    return json.load(open(ЗГЕНЕРОВАНІ, encoding="utf-8")) if os.path.exists(ЗГЕНЕРОВАНІ) else []


def зберегти(lib):
    зберегти_json(ЗГЕНЕРОВАНІ, lib)


def документ(items, title):
    """LaTeX-документ з аналогами (преамбула й макроси бази як у варіанті)"""
    import варіант as V
    out = [V.преамбула(title, title), "\\begin{document}",
           V.тіло_теми(файли_тем()[0][1]) + "\n\\setcounter{zad}{0}\n", "\\chapterTitle{%s}\n" % title]
    for g in items:
        out.append("%% %s | відповідь %s\n\\begin{samepage}\n%s\n\\end{samepage}\n" % (g["id"], g["відповідь"], як_у_базі(g["latex"])))
    out.append("\\end{document}\n")
    return нфк("\n".join(out))


def компілювати(tex, workdir, name="t"):
    """(ok, текст помилки, шлях PDF); компіляція в теці варіантів, щоб шляхи до шрифтів збігалися"""
    src = os.path.join(ROOT, "варіанти", "_перевірка_%s.tex" % name)
    os.makedirs(os.path.dirname(src), exist_ok=True)
    open(src, "w", encoding="utf-8").write(tex)
    try:
        p = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "-output-directory=" + workdir, os.path.basename(src)],
                           cwd=os.path.dirname(src), capture_output=True, text=True, timeout=180)
        log = open(os.path.join(workdir, os.path.basename(src)[:-4] + ".log"), encoding="utf-8", errors="replace").read()
    finally:
        os.remove(src)
    err = re.findall(r"(?m)^! .*(?:\n.*){0,3}", log)
    over = len(re.findall(r"Overfull \\hbox \((\d{2,}|[5-9])\.\d+pt", log))
    return p.returncode == 0 and not err, "\n".join(err)[:600], os.path.join(workdir, os.path.basename(src)[:-4] + ".pdf"), over


def додати(result_path, zr_dir):
    res = json.load(open(result_path, encoding="utf-8"))
    analogs = res["analogs"] if isinstance(res, dict) else res
    lib = завантажити()
    n_by_cat = collections.Counter(g["категорія"] for g in lib)
    seen = {re.sub(r"\s+", "", g["latex"]) for g in lib}
    work = tempfile.mkdtemp(prefix="аналоги_")
    added = failed = 0
    for a in analogs:
        if re.sub(r"\s+", "", a["latex"]) in seen: continue
        c = a["category"]
        n_by_cat[c] += 1
        ex = json.load(open(os.path.join(zr_dir, c + ".json"), encoding="utf-8"))["приклади"]
        src = ex[a["source_k"] - 1] if 1 <= a["source_k"] <= len(ex) else None
        g = dict(id="ген-%s-%02d" % (c, n_by_cat[c]), категорія=c, тип=a["type"], латех_рисунок=a.get("has_figure", False),
                 latex=a["latex"].strip(), відповідь=a["answer"], розвʼязок=a["solution"], дистрактори=a["distractors"],
                 зразок=src["id"] if src else None, рік_зразка=src["рік"] if src else None, оцінки=a.get("scores"),
                 раунд=a.get("round"), теми=[], рік=None)
        ok, err, pdf, over = компілювати(документ([g], "перевірка"), work, g["id"])
        g["перевірено"] = ok
        if not ok: g["помилка_компіляції"] = err; failed += 1
        if over: g["переповнення"] = over
        lib.append(g); seen.add(re.sub(r"\s+", "", g["latex"])); added += 1
        print("%-34s %s%s" % (g["id"], "ok" if ok else "ПОМИЛКА: " + err.splitlines()[0] if err else "ПОМИЛКА", "" if not over else "  (переповнення рядка)"))
    зберегти(lib)
    print("додано:", added, "з них не компілюються:", failed, "| у бібліотеці:", len(lib))


def перегляд(out_dir):
    lib = [g for g in завантажити()]
    os.makedirs(out_dir, exist_ok=True)
    by = collections.defaultdict(list)
    for g in lib: by[g["категорія"]].append(g)
    for c, items in by.items():
        ok, err, pdf, _ = компілювати(документ(items, "Аналоги: " + c.replace("_", " ")), out_dir, c)
        print(c, len(items), "ok" if ok else "ПОМИЛКА " + err[:200], pdf)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "додати": додати(sys.argv[2], sys.argv[3])
    elif cmd == "перегляд": перегляд(sys.argv[2] if len(sys.argv) > 2 else tempfile.mkdtemp(prefix="перегляд_"))
    else: print(__doc__)
