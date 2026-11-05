# -*- coding: utf-8 -*-
"""Каталог типів завдань НМТ з короткою відповіддю (задачі з параметром): перевірка зразків
і запис у scripts/data/типи_кв_параметр_нмт.json (спільна логіка -- scripts/типи_спільне/збирач.py).

    python3 scripts/типи_кв_параметр/зібрати.py && python3 scripts/типи_кв_параметр/pdf.py ВИХІД.pdf
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "типи_спільне"))
ВИХІД = os.path.join(os.path.dirname(HERE), "data", "типи_кв_параметр_нмт.json")
from спец import ТИПИ                                   # noqa: E402
from збирач import зібрати_відкриті                    # noqa: E402

if __name__ == "__main__":
    зібрати_відкриті(ТИПИ, ВИХІД)
