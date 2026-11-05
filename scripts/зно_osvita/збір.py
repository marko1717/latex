# -*- coding: utf-8 -*-
"""Тести ЗНО/НМТ з математики з zno.osvita.ua -- ЛОКАЛЬНА база зразків для генератора аналогів.

Умови сайту (zno.osvita.ua/agreement.html): матеріали лише для особистого використання, без
відтворення й поширення. Тому все зібране лежить у «локальне/osvita/» (у git не йде), а кожне
завдання має позначку поширення = «ні»: у варіанти, збірники й PDF дослівно не потрапляє,
генератор бере ці завдання лише як зразки для власних (авторських) аналогів.

    python3 scripts/зно_osvita/збір.py сторінки     # індекс і сторінки тестів (кеш; пауза 3 с -- як у robots.txt)
    python3 scripts/зно_osvita/збір.py розібрати    # html -> локальне/osvita/завдання.json + підсумок
    python3 scripts/зно_osvita/збір.py рисунки      # рисунки до завдань (кеш; пауза 3 с)

Кожен запит -- з паузою; сторінки й рисунки кешуються, тож повторний запуск нічого не качає вдруге.
"""
import os, re, sys, json, time, html, collections, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ДАНІ = os.path.join(ROOT, "локальне", "osvita")
САЙТ = "https://zno.osvita.ua"
ПАУЗА = 3.0                                   # Crawl-delay: 3 (robots.txt)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
ЛІТЕРИ = dict(zip("abcde", "АБВГД"))
# 13 -- відповідність 3×5 (НМТ, ЗНО 2020--2021); 4, 5, 10 -- 4×5, 4×4, 5×4 (ЗНО 2010--2019)
ТИПИ = {"1": "single", "13": "matching", "4": "matching", "5": "matching", "10": "matching", "8": "input", "11": "input2", "12": "open"}
_останній = [0.0]


def отримати(url, binary=False):
    """GET із паузою між запитами й повторами на тимчасові збої"""
    for attempt in range(4):
        wait = ПАУЗА - (time.time() - _останній[0])
        if wait > 0: time.sleep(wait)
        _останній[0] = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
            return data if binary else data.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < 3: time.sleep(10 * (attempt + 1)); continue
            raise
        except urllib.error.URLError:
            if attempt < 3: time.sleep(10 * (attempt + 1)); continue
            raise


# ---------------------------------------------------------------- 1. сторінки
def тести_з_індексу(s):
    out, seen = [], set()
    for m in re.finditer(r'<a[^>]+href="(/mathematics/(\d+)/)"[^>]*>(.*?)</a>', s, re.S):
        tid, title = m.group(2), re.sub(r"\s+", " ", html.unescape(re.sub("<[^>]+>", "", m.group(3)))).strip()
        if tid in seen or not title: continue
        seen.add(tid); out.append(dict(id=tid, назва=title))
    return out


def сторінки():
    os.makedirs(os.path.join(ДАНІ, "html"), exist_ok=True)
    idx = os.path.join(ДАНІ, "html", "index.html")
    if not os.path.exists(idx): open(idx, "w", encoding="utf-8").write(отримати(САЙТ + "/mathematics/"))
    tests = тести_з_індексу(open(idx, encoding="utf-8").read())
    json.dump(tests, open(os.path.join(ДАНІ, "тести.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    new = 0
    for t in tests:
        p = os.path.join(ДАНІ, "html", t["id"] + ".html")
        if os.path.exists(p) and os.path.getsize(p) > 10000: continue
        open(p, "w", encoding="utf-8").write(отримати("%s/mathematics/%s/" % (САЙТ, t["id"])))
        new += 1
        print("  %s  %s" % (t["id"], t["назва"]))
    print("тестів у переліку: %d, завантажено нових сторінок: %d" % (len(tests), new))


# ---------------------------------------------------------------- 2. розбір
def латех(h, рис):
    """фрагмент HTML сайту -> текст у LaTeX-нотації бази; рисунки -> [РИСУНОК файл]"""
    def img(m):
        url = m.group(1)
        if url.startswith("/"): url = САЙТ + url
        рис.append(url)
        return "\n[РИСУНОК %s]\n" % локальний_файл(url)
    h = re.sub(r'<img[^>]+src="([^"]+)"[^>]*>', img, h)
    h = re.sub(r'<latex[^>]*>\s*\$\$(.*?)\$\$\s*</latex>', lambda m: "\n\\[" + m.group(1).strip() + "\\]\n", h, flags=re.S)
    h = re.sub(r'<latex[^>]*>\s*\\\((.*?)\\\)\s*</latex>', lambda m: "$" + m.group(1).strip() + "$", h, flags=re.S)
    h = re.sub(r'<latex[^>]*>(.*?)</latex>', lambda m: m.group(1), h, flags=re.S)
    h = re.sub(r'<table[^>]*>(.*?)</table>', lambda m: таблиця(m.group(1)), h, flags=re.S)
    h = re.sub(r'<b>(.*?)</b>|<strong>(.*?)</strong>', lambda m: "\\textbf{%s}" % (m.group(1) or m.group(2)), h, flags=re.S)
    h = re.sub(r'<(em|i)>(.*?)</\1>', lambda m: "\\emph{%s}" % m.group(2), h, flags=re.S)
    h = re.sub(r'<sup>(.*?)</sup>', r'$^{\1}$', h, flags=re.S)
    h = re.sub(r'<sub>(.*?)</sub>', r'$_{\1}$', h, flags=re.S)
    h = re.sub(r'<br\s*/?>|</p>|</div>|</li>', "\n", h)
    h = re.sub(r'<[^>]+>', "", h)
    h = html.unescape(h).replace("\xa0", "~")
    h = h.replace("\\gt", ">").replace("\\lt", "<")          # макроси MathJax, яких немає в LaTeX
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in h.split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def таблиця(t):
    rows = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", t, re.S):
        cells = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", tr, re.S)]
        rows.append(" & ".join(cells) + r" \\ \hline")
    n = max((r.count(" & ") + 1 for r in rows), default=1)
    return "\n\\begin{tabular}{|%s|}\\hline\n%s\n\\end{tabular}\n" % ("|".join("c" * n), "\n".join(rows))


def локальний_файл(url):
    m = re.search(r"/znotest/(.+)$", url)
    return "рисунки/" + (m.group(1) if m else os.path.basename(url))


def варіанти(block, рис):
    return [(m.group(1), латех(m.group(2), рис))
            for m in re.finditer(r'<div class="answer"><span class="marker">(.*?)</span>(.*?)</div>', block, re.S)]


def число(s):
    s = s.strip().replace(".", ",")
    return s[:-2] if s.endswith(",0") else s


def розібрати_картку(c, meta):
    num = re.search(r"Завдання (\d+) з (\d+)", c)
    tip = re.search(r'name="q\[tip\]" value="(\d+)"', c)
    qid = re.search(r'name="q\[id\]" value="(\d+)"', c)
    if not (num and tip and qid): return None
    tip = tip.group(1); рис = []
    q = re.search(r'<div class="question">(.*?)</div>\s*<div class="clear">', c, re.S)
    rec = dict(id="osvita-" + qid.group(1), тест=meta["id"], назва_тесту=meta["назва"], іспит=meta["іспит"], рік=meta["рік"],
               сесія=meta["сесія"], номер=int(num.group(1)), усього=int(num.group(2)), tip=tip, тип=ТИПИ.get(tip, "інше"),
               умова=латех(q.group(1) if q else "", рис), поширення="ні",
               джерело="%s/mathematics/%s/" % (САЙТ, meta["id"]))
    res = re.search(r'name="result" value="([^"]*)"', c)
    res = res.group(1).strip() if res else ""
    cols = re.findall(r'<div class="answers col"[^>]*>(.*?)</div>\s*(?=<div class="answers col"|<div class="clear)', c, re.S)
    if rec["тип"] == "matching" and len(cols) >= 2:
        heads = [латех(re.search(r'<div class="quest-title">(.*?)</div>', x, re.S).group(1), рис)
                 if re.search(r'<div class="quest-title">', x) else "" for x in cols[:2]]
        rec["заголовки"] = heads
        rec["пункти"] = [v for _, v in варіанти(cols[0], рис)]
        rec["варіанти"] = [v for _, v in варіанти(cols[1], рис)]
        pairs = dict(re.findall(r"(\d)([a-e])", res))
        rec["відповідь"] = "".join(ЛІТЕРИ.get(pairs.get(str(i), ""), "?") for i in range(1, len(rec["пункти"]) + 1))
    elif rec["тип"] == "single":
        ans = re.search(r'<div class="answers">(.*?)\n\s*</div>', c, re.S)
        rec["варіанти"] = [v for _, v in варіанти(ans.group(1) if ans else c, рис)]
        rec["відповідь"] = ЛІТЕРИ.get(res.lower(), res)
    elif rec["тип"] in ("input", "input2"):
        rec["відповідь"] = ";".join(число(x) for x in res.split(";"))
    elif rec["тип"] == "open":
        rec["відповідь"] = None; rec["бали"] = int(res) if res.isdigit() else res
    else:
        rec["відповідь"] = res; rec["html"] = c[:6000]
    rec["рисунки"] = [локальний_файл(u) for u in рис]
    rec["_урли_рисунків"] = рис
    return rec


def метадані(t):
    m = re.search(r"(ЗНО|НМТ)[^\d]*(\d{4})", t["назва"])
    сесія = t["назва"].split("–")[-1].strip() if "–" in t["назва"] else ""
    return dict(id=t["id"], назва=t["назва"], іспит=m.group(1) if m else "?", рік=m.group(2) if m else "?", сесія=сесія)


def розібрати():
    tests = json.load(open(os.path.join(ДАНІ, "тести.json"), encoding="utf-8"))
    out, пропущено = [], []
    for t in tests:
        p = os.path.join(ДАНІ, "html", t["id"] + ".html")
        if not os.path.exists(p): пропущено.append(t["id"]); continue
        s = open(p, encoding="utf-8", errors="replace").read()
        meta = метадані(t)
        cards = re.split(r'(?=<div class="task-card)', s)[1:]
        for c in cards:
            r = розібрати_картку(c, meta)
            if r: out.append(r)
    json.dump(out, open(os.path.join(ДАНІ, "завдання.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    типи = collections.Counter(r["тип"] for r in out)
    іспити = collections.Counter((r["іспит"], r["рік"]) for r in out)
    без_відп = sum(1 for r in out if r["тип"] != "open" and (not r.get("відповідь") or "?" in (r.get("відповідь") or "")))
    з_рис = sum(1 for r in out if r["рисунки"])
    print("завдань: %d (тестів %d, без сторінки: %s)" % (len(out), len(tests) - len(пропущено), пропущено or "немає"))
    print("типи:", dict(типи))
    print("з рисунками: %d, рисунків усього: %d; без розпізнаної відповіді: %d" % (з_рис, sum(len(r["рисунки"]) for r in out), без_відп))
    print("за роками:", ", ".join("%s %s: %d" % (e, y, n) for (e, y), n in sorted(іспити.items(), key=lambda x: (x[0][1], x[0][0]))))


# ---------------------------------------------------------------- 3. рисунки
def рисунки():
    tasks = json.load(open(os.path.join(ДАНІ, "завдання.json"), encoding="utf-8"))
    urls = sorted({u for r in tasks for u in r["_урли_рисунків"]})
    нові = [u for u in urls if not os.path.exists(os.path.join(ДАНІ, локальний_файл(u)))]
    print("рисунків: %d, ще не завантажено: %d (≈ %d хв з паузою %g с)" % (len(urls), len(нові), len(нові) * ПАУЗА // 60 + 1, ПАУЗА))
    for k, u in enumerate(нові, 1):
        p = os.path.join(ДАНІ, локальний_файл(u))
        os.makedirs(os.path.dirname(p), exist_ok=True)
        try:
            open(p, "wb").write(отримати(u, binary=True))
        except urllib.error.HTTPError as e:
            print("  ! %d %s" % (e.code, u)); continue
        if k % 50 == 0: print("  %d/%d" % (k, len(нові)))
    print("готово")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    {"сторінки": сторінки, "розібрати": розібрати, "рисунки": рисунки}.get(cmd, lambda: print(__doc__))()
