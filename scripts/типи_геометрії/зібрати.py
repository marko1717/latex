# -*- coding: utf-8 -*-
"""Каталог типів тестових завдань НМТ з геометрії: перевірка кожного зразка й запис у scripts/data/типи_геометрії_нмт.json
(спільна логіка -- scripts/типи_спільне/збирач.py).

    python3 scripts/типи_геометрії/зібрати.py && python3 scripts/типи_геометрії/pdf.py ВИХІД.pdf
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "типи_спільне"))
ВИХІД = os.path.join(os.path.dirname(HERE), "data", "типи_геометрії_нмт.json")
from спец import ТИПИ                                   # noqa: E402
from збирач import зібрати                             # noqa: E402

if __name__ == "__main__":
    зібрати(ТИПИ, ВИХІД)
