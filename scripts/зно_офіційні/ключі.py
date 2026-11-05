# -*- coding: utf-8 -*-
"""Офіційні ключі ЗНО з математики 2016--2021 (PDF УЦОЯО) -> локальне/зно_офіційні/ключі.json.

У ключі три стовпці для різних зошитів; опубліковано «Зошит № 1», тому береться перший стовпець.
    python3 scripts/зно_офіційні/ключі.py
"""
import os, re, json, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIR = os.path.join(ROOT, "локальне", "зно_офіційні")


def відповідь(s):
    s = s.strip().replace("–", "-").replace("−", "-")
    pairs = re.findall(r"(\d)\s*-\s*([АБВГД])", s)
    if len(pairs) >= 3: return "".join(l for _, l in sorted(pairs))
    return s


def main():
    перелік = json.load(open(os.path.join(DIR, "перелік.json"), encoding="utf-8"))
    out = {}
    for x in перелік:
        if x["вид"] != "ключ": continue
        txt = subprocess.run(["pdftotext", "-layout", os.path.join(DIR, "pdf", x["файл"]), "-"], capture_output=True, text=True).stdout
        зошит = x["файл"].replace("_ключ", "_зошит").replace(".pdf", "")
        k = {}
        for ln in txt.splitlines():
            cols = re.split(r"\s{2,}", ln.strip())
            if len(cols) >= 2 and re.fullmatch(r"\d{1,2}(\.\d)?", cols[0]) and cols[0] not in k:
                a = відповідь(cols[1])
                # лише рядки ключа (літера, відповідність або число), не таблиці балів
                if re.fullmatch(r"[АБВГД]|[АБВГД]{3,4}|-?\d+(,\d+)?", a): k[cols[0]] = a
        out[зошит] = k
        print("%-32s %2d відповідей: %s ..." % (зошит, len(k), ", ".join("%s=%s" % kv for kv in list(k.items())[:3])))
    json.dump(out, open(os.path.join(DIR, "ключі.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
