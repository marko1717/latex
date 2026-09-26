# -*- coding: utf-8 -*-
"""Ключі відповідей із посібника «НМТ 2023--2025»: таблиці «Правильні відповіді» після кожної сесії 2024 і 2025 років.

У виданні 2023 року ключів немає. Таблиці читаються за координатами слів (pdftotext -bbox):
номер завдання в лівій колонці, відповідь -- у правій на тій самій висоті; водяний знак
відкидається за висотою слова.

    python3 scripts/звірка_pdf_2023_2025/ключі.py      # -> scripts/data/ключі_pdf_2024_2025.json
"""
import re, os, json, html, subprocess

PDF = os.path.expanduser("~/Desktop/НМТ23-25.pdf")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "ключі_pdf_2024_2025.json")
MON = {"травня": "05", "червня": "06"}


def words(page):
    x = subprocess.run(["pdftotext", "-bbox", "-f", str(page), "-l", str(page), PDF, "-"], capture_output=True, text=True).stdout
    return [(float(a), float(b), float(c), float(d), html.unescape(w)) for a, b, c, d, w in
            re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>', x)]


def table(page):
    ws = [w for w in words(page) if (w[3] - w[1]) < 20]          # без водяного знака (великий кегль)
    rows = {}
    for n in [w for w in ws if re.fullmatch(r"\d{1,2}", w[4]) and 100 < w[0] < 260]:
        yc = (n[1] + n[3]) / 2
        right = sorted([w for w in ws if 300 < w[0] < 470 and abs((w[1] + w[3]) / 2 - yc) < 4], key=lambda w: w[0])
        val = " ".join(w[4] for w in right).strip()
        k = int(n[4])
        if 1 <= k <= 22 and val and k not in rows: rows[k] = val
    return rows


def main():
    npages = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", PDF], capture_output=True, text=True).stdout).group(1))
    keys, cur = {}, None
    for p in range(95, npages + 1):
        t = subprocess.run(["pdftotext", "-layout", "-f", str(p), "-l", str(p), PDF, "-"], capture_output=True, text=True).stdout
        m = re.search(r"(?m)^\s*(\d{2})\.(\d{2})\.(2024)\s*$", t)
        if m: cur = "%s.%s.24" % (m.group(1), m.group(2))
        m = re.search(r"(\d{1,2})\s+(травня|червня)\s+2025\s+року", t)
        if m: cur = "%02d.%s.25" % (int(m.group(1)), MON[m.group(2)])
        if "ПРАВИЛЬНІ ВІДПОВІДІ" in t and cur and cur not in keys:
            keys[cur] = {str(k): v for k, v in sorted(table(p).items())}
            print(cur, "сторінка", p, "відповідей:", len(keys[cur]))
    json.dump(keys, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("сесій:", len(keys), "->", OUT)


if __name__ == "__main__":
    main()
