# -*- coding: utf-8 -*-
"""Звірка рисунків бази з оригіналами НМТ: для кожного завдання з рисунком -- пара «оригінал | база» (PNG).

    python3 scripts/звірка_рисунків.py ТЕКА [--id ID ...]      # -> ТЕКА/пари/<id>.png, ТЕКА/індекс.json

Оригінали: НМТ 2023--2025 -- ~/Downloads/НМТ23-25.pdf (сторінки сесій -- scripts/звірка_pdf_2023_2025/extract.py),
НМТ 2026 -- ~/Downloads/Telegram Desktop/НМТ 2026 основна сесія (22).pdf (сесію шукаємо за датою в колонтитулі).
Посилання на сесію й номер -- з каталогу (scripts/data/варіант_каталог.json: сесія_2026, довідки[].сесія/номер).
Завдання на сторінці -- від його номера «N.» біля лівого поля до номера наступного (або до кінця сторінки)."""
import os, re, sys, json, subprocess, tempfile, shutil, collections
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(HERE, "варіант_нмт")); sys.path.insert(0, os.path.join(HERE, "звірка_pdf_2023_2025"))
import спільне as SP                      # noqa: E402
import варіант as V                       # noqa: E402

PDF_23_25 = os.path.expanduser("~/Downloads/НМТ23-25.pdf")
PDF_2026 = os.path.expanduser("~/Downloads/Telegram Desktop/НМТ 2026 основна сесія (22).pdf")
МІСЯЦІ = {"05": "травня", "06": "червня"}
DPI = 110


import functools


@functools.lru_cache(maxsize=None)
def слова(pdf, p):
    t = subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), "-bbox", pdf, "-"], capture_output=True, text=True).stdout
    return [(float(a), float(b), float(c), float(d), w) for a, b, c, d, w in
            re.findall(r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)<', t)]


def сторінок(pdf):
    return int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout).group(1))


def сторінки_сесій_2023_25():
    """сесія -> (перша, остання) сторінка PDF 2023--2025"""
    src = open(os.path.join(HERE, "звірка_pdf_2023_2025", "extract.py"), encoding="utf-8").read()
    out = {}
    for назва in ("SESS_2023", "SESS_2024", "SESS_2025"):
        блок = re.search(назва + r"\s*=\s*\[(.*?)\]\n", src, re.S).group(1)
        пари = re.findall(r"\((\d+),\s*(None|\"[^\"]+\")(?:,\s*\d+)?\)", блок)
        for (p, s), (p2, _) in zip(пари, пари[1:] + [(str(int(пари[-1][0]) + 8), None)]):
            if s != "None": out[s.strip('"')] = (int(p), int(p2) - 1)
    return out


def сторінки_сесій_2026():
    """«18.06» -> список сторінок, у колонтитулі яких «18 червня 2026 року»"""
    out = collections.defaultdict(list)
    for p in range(1, сторінок(PDF_2026) + 1):
        верх = " ".join(w for x0, y0, x1, y1, w in слова(PDF_2026, p) if y0 < 60)
        m = re.search(r"(\d{1,2})\s+(травня|червня)\s+2026", верх)
        if m:
            місяць = "05" if m.group(2) == "травня" else "06"
            out["%d.%s" % (int(m.group(1)), місяць)].append(p)
    return out


def знайти_завдання(pdf, сторінки, n):
    """(сторінка, y0, y1) у pt: від «n.» біля лівого поля до «n+1.» або кінця сторінки"""
    for p in сторінки:
        ws = слова(pdf, p)
        номери = sorted((y0, w) for x0, y0, x1, y1, w in ws if x0 < 90 and re.fullmatch(r"\d{1,2}\.", w))
        for i, (y0, w) in enumerate(номери):
            if int(w[:-1]) == n:
                y1 = next((yy for yy, ww in номери[i + 1:] if int(ww[:-1]) == n + 1), None)
                низ = max((b for _, _, _, b, _ in ws if b < 805), default=800)
                return p, max(y0 - 8, 0), (y1 - 6) if y1 else низ + 6
    return None


def _норм(t):
    return re.sub(r"[^0-9a-zа-яіїєґ]+", "", t.lower())


def текст_завдання(блок):
    """умова без LaTeX-команд, рисунків і варіантів -- для пошуку на сторінці оригіналу"""
    b = re.sub(r"(?<!\\)%[^\n]*", "", блок)
    b = re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", " ", b, flags=re.S)
    b = re.split(r"\\answerTable|\\matchingLayout|\\answerListVertical|\\begin\{tabular\}", b)[0]
    b = re.sub(r"\\[A-Za-z]+", " ", b)
    return _норм(b)[:160]


def знайти_за_текстом(pdf, сторінки, текст, n=None):
    """(сторінка, y0, y1, схожість) -- область завдання, текст якої найбільше схожий на умову (номер -- лише підказка)"""
    import difflib
    найкраще = None
    for p in сторінки:
        ws = слова(pdf, p)
        номери = sorted((y0, w) for x0, y0, x1, y1, w in ws if x0 < 90 and re.fullmatch(r"\d{1,2}\.", w))
        if not номери:      # НМТ 2023: номери завдань -- графікою; біля кожного завдання на лівому полі «Відповідь» (на рядок нижче)
            номери = sorted((max(y0 - 16, 0), "0.") for x0, y0, x1, y1, w in ws if x0 < 95 and w == "Відповідь")
        низ = max((b for _, _, _, b, _ in ws if b < 805), default=800)
        for i, (y0, w) in enumerate(номери):
            y1 = номери[i + 1][0] if i + 1 < len(номери) else низ + 6
            область = _норм(" ".join(ww for x0, yy, x1, y2, ww in sorted(ws, key=lambda t: (round(t[1] / 4), t[0])) if y0 - 2 <= yy < y1))
            r = difflib.SequenceMatcher(None, текст, область[:len(текст) + 40]).ratio()
            if n and int(w[:-1]) == n: r += 0.05
            if not найкраще or r > найкраще[3]:
                найкраще = (p, max(y0 - 8, 0), y1 - 6, r, int(w[:-1]))
    return найкраще


def обрізати_оригінал(pdf, p, y0, y1, куди):
    tmp = куди + ".tmp"
    subprocess.run(["pdftoppm", "-f", str(p), "-l", str(p), "-r", str(DPI), "-singlefile", "-png", pdf, tmp], check=True)
    from PIL import Image
    im = Image.open(tmp + ".png").convert("RGB")
    k = DPI / 72.0
    im.crop((0, int(y0 * k), im.width, min(int(y1 * k), im.height))).save(куди)
    os.remove(tmp + ".png")


def наші_завдання(ids, куди_теки):
    """PDF «одне завдання на сторінку» (преамбула й макроси тем) -> PNG кожної сторінки"""
    бл = {t["id"]: t for t in SP.завдання_бази()}
    s = [V.преамбула("Звірка", "Звірка"), "\\begin{document}"] + [V.тіло_теми(f) for _, f in SP.файли_тем()]
    s.append("\\pagestyle{empty}\\setcounter{zad}{0}")
    for i in ids:
        s.append("{\\tiny\\color{white}ЗВІРКА%s}\\par\\begin{minipage}{\\textwidth}\n%s\n\\end{minipage}\\clearpage" % (i, V.чистий_блок(бл[i]["блок"], True)))
    s.append("\\end{document}")
    src = os.path.join(ROOT, "варіанти", "_звірка.tex")
    open(src, "w", encoding="utf-8").write(SP.нфк("\n".join(s)))
    tmp = tempfile.mkdtemp(prefix="звірка_")
    try:
        for _ in range(2):
            subprocess.run(["xelatex", "-interaction=nonstopmode", "-output-directory=" + tmp, "_звірка.tex"],
                           cwd=os.path.dirname(src), capture_output=True, timeout=1800)
    finally:
        os.remove(src)
    pdf = os.path.join(tmp, "_звірка.pdf")
    кадри = {}
    for p in range(1, сторінок(pdf) + 1):          # сторінка -> id за невидимою міткою (завдання на 2 сторінки -- перша)
        m = re.search(r"ЗВІРКА([0-9a-f]{12})", subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), pdf, "-"], capture_output=True, text=True).stdout)
        if m and m.group(1) not in кадри:
            f = os.path.join(куди_теки, "наше_%s" % m.group(1))
            subprocess.run(["pdftoppm", "-f", str(p), "-l", str(p), "-r", str(DPI), "-singlefile", "-png", pdf, f], check=True)
            кадри[m.group(1)] = f + ".png"
    return кадри


def зміст(im):
    from PIL import ImageOps
    b = ImageOps.invert(im.convert("L")).point(lambda v: 255 if v > 40 else 0).getbbox()
    return im.crop((max(b[0] - 8, 0), max(b[1] - 8, 0), b[2] + 8, b[3] + 8)) if b else im


def main():
    тека = os.path.abspath(sys.argv[1]); os.makedirs(os.path.join(тека, "пари"), exist_ok=True)
    лише = set(x for x in sys.argv[sys.argv.index("--id") + 1:] if re.fullmatch(r"[0-9a-f]{12}", x)) if "--id" in sys.argv else None
    кат = {c["id"]: c for c in json.load(open(os.path.join(HERE, "data", "варіант_каталог.json"), encoding="utf-8"))}
    задачі = [t for t in {t["id"]: t for t in SP.завдання_бази()}.values() if "tikzpicture" in t["блок"] and (not лише or t["id"] in лише)]
    с2325, с2026 = сторінки_сесій_2023_25(), сторінки_сесій_2026()
    індекс, де = [], {}
    for t in задачі:
        k = кат.get(t["id"], {})
        місце = None
        if k.get("сесія_2026"):
            m = re.match(r"2026-(\d+\.\d+)-(\d+)", k["сесія_2026"])
            if m:
                d, mo = m.group(1).split(".")
                місце = ("2026", PDF_2026, с2026.get("%d.%s" % (int(d), mo), []), int(m.group(2)))
        else:
            д = next((x for x in k.get("довідки", []) if x.get("сесія") in с2325 and x.get("номер")), None)
            if д:
                a, b = с2325[д["сесія"]]
                місце = (д["сесія"], PDF_23_25, list(range(a, b + 1)), int(д["номер"]))
        if not місце:          # без посилання -- шукаємо текстом по всьому році
            рік = str(t.get("рік") or k.get("рік") or "")
            діапазон = {"2023": (5, 85), "2024": (95, 205), "2025": (214, 317)}.get(рік)
            if рік == "2026": місце = ("2026", PDF_2026, list(range(1, сторінок(PDF_2026) + 1)), None)
            elif діапазон: місце = (рік, PDF_23_25, list(range(діапазон[0], діапазон[1] + 1)), None)
        if not місце: індекс.append(dict(id=t["id"], стан="без посилання")); continue
        знайдено = знайти_за_текстом(місце[1], місце[2], текст_завдання(t["блок"]), місце[3])
        поріг = float(sys.argv[sys.argv.index("--поріг") + 1]) if "--поріг" in sys.argv else 0.45
        if not знайдено or знайдено[3] < поріг:
            індекс.append(dict(id=t["id"], стан="не знайдено на сторінках", сесія=місце[0], номер=місце[3],
                               схожість=round(знайдено[3], 2) if знайдено else None)); continue
        p, y0, y1, схожість, номер = знайдено
        f = os.path.join(тека, "пари", "ориг_%s.png" % t["id"])
        обрізати_оригінал(місце[1], p, y0, y1, f)
        де[t["id"]] = dict(сесія=місце[0], номер=номер, сторінка=p, pdf=os.path.basename(місце[1]), схожість=round(схожість, 2))
    ids = list(де)
    кадри = наші_завдання(ids, os.path.join(тека, "пари"))
    from PIL import Image, ImageDraw, ImageFont
    шрифт = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 18)
    for i in ids:
        if i not in кадри: індекс.append(dict(id=i, стан="не зібралося в нас", **де[i])); continue
        кадр = кадри[i]
        a = Image.open(os.path.join(тека, "пари", "ориг_%s.png" % i)).convert("RGB")
        b = зміст(Image.open(кадр).convert("RGB"))
        H = max(a.height, b.height) + 34
        o = Image.new("RGB", (a.width + b.width + 24, H), "white"); dr = ImageDraw.Draw(o)
        dr.text((6, 6), "ОРИГІНАЛ: %s, № %d, с. %d" % (де[i]["сесія"], де[i]["номер"], де[i]["сторінка"]), fill="#05a", font=шрифт)
        dr.text((a.width + 30, 6), "БАЗА: %s" % i, fill="#070", font=шрифт)
        o.paste(a, (0, 30)); o.paste(b, (a.width + 24, 30)); dr.line([(a.width + 12, 30), (a.width + 12, H)], fill="#c00", width=2)
        o.save(os.path.join(тека, "пари", "%s.png" % i))
        os.remove(кадр); os.remove(os.path.join(тека, "пари", "ориг_%s.png" % i))
        індекс.append(dict(id=i, стан="пара", **де[i]))
    json.dump(індекс, open(os.path.join(тека, "індекс.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("пар:", len(ids), "|", dict(collections.Counter(x["стан"] for x in індекс)))


if __name__ == "__main__":
    main()
