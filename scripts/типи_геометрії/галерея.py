# -*- coding: utf-8 -*-
"""Галерея всіх рисунків каталогу геометрії на 1--2 сторінках: код типу + рисунок, по 4 в ряд.
Щоб швидко переглянути, чи не налазять мітки на лінії:

    python3 scripts/типи_геометрії/галерея.py ВИХІД.pdf
"""
import os, sys, tempfile, shutil, io, contextlib
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts", "варіант_нмт")); sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts", "типи_спільне"))
import варіант as V                                    # noqa: E402
from спільне import нфк                                # noqa: E402
from аналоги import компілювати                        # noqa: E402

журнал = io.StringIO()
with contextlib.redirect_stdout(журнал):
    import спец                                        # noqa: E402
if журнал.getvalue().strip(): print(журнал.getvalue().rstrip())   # попередження про мітки, якщо є
клітинки = [r"\begin{minipage}[t]{0.24\textwidth}\centering{\bfseries %s}\par\vspace{2pt}\begin{nmtfit}%s\end{nmtfit}\end{minipage}" % (t["код"], t["рисунок"])
            for t in спец.ТИПИ if t.get("рисунок")]
рядки = ["\\noindent" + "\\hfill".join(клітинки[i:i + 4]) + "\\par\\vspace{0.4cm}" for i in range(0, len(клітинки), 4)]
tex = "\n".join([V.преамбула("Галерея рисунків", "Галерея рисунків каталогу геометрії"), r"\pagestyle{empty}\begin{document}"] + рядки + [r"\end{document}"])
ok, err, pdf, over = компілювати(нфк(tex), tempfile.mkdtemp(), "галерея")
if not ok: raise SystemExit(err)
shutil.copy(pdf, sys.argv[1] if len(sys.argv) > 1 else "Галерея_рисунків_геометрії.pdf")
print("рисунків:", len(клітинки))
