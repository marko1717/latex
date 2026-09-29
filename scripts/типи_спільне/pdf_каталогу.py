# -*- coding: utf-8 -*-
"""Спільний PDF каталогу типів НМТ (scripts/типи_*): блок на кожен тип -- назва, частота, формат, приклад із НМТ,
зразок, відповідь і пастки; заголовок розділу стоїть в одному блоці з першим завданням групи."""
import os, sys, json, shutil, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "scripts", "варіант_нмт"))
import варіант as V                                    # noqa: E402
from спільне import як_у_базі, файли_тем, нфк          # noqa: E402
from аналоги import компілювати                        # noqa: E402

БЛОК = r"""\par\noindent\begin{minipage}{\linewidth}
%s\par\vspace{0.25cm}\noindent{\bfseries\color{mainGreen}%s.~%s}\par\nopagebreak
\noindent{\footnotesize\color{gray!85!black}Частота: %s.\quad Формат питання: %s.}\par\nopagebreak
\noindent{\footnotesize\color{gray!85!black}Як у НМТ: %s}\par\nopagebreak\vspace{0.12cm}
\renewcommand{\thezad}{%s}
%s
\nopagebreak\noindent{\footnotesize Відповідь: \textbf{%s}.\quad Пастки: %s.}\par
\end{minipage}\par
"""



def показ_відповіді(t):
    v = t.get("відповідь_показ", t["відповідь"])
    return "$-$" + v[1:] if v.startswith("-") else v        # від'ємна відповідь: мінус, а не дефіс


def зробити(json_шлях, title, header, вступ, out, name):
    T = json.load(open(json_шлях, encoding="utf-8"))
    tex = [V.преамбула(title, header), "\\begin{document}", V.тіло_теми(файли_тем()[0][1]) + "\n",
           "\\chapterTitle{%s}\n" % title, вступ]
    група = None
    for t in T:
        розділ = ""
        if t["група"] != група:                          # заголовок розділу -- в одному блоці з першим завданням
            група = t["група"]; розділ = "\\sectionTitle{%s}\n" % група
        tex.append(БЛОК % (розділ, t["код"], t["назва"], t["частота"], t["формати"], t["нмт"], t["код"], як_у_базі(t["latex"]).replace(r"\par\penalty-20", ""), показ_відповіді(t), t["пастки"]))
    tex.append("\\end{document}\n")
    ok, err, pdf, over = компілювати(нфк("\n".join(tex)).replace("ʼ", "'"), tempfile.mkdtemp(), name)   # у шрифті немає U+02BC
    if not ok: raise SystemExit(err)
    shutil.copy(pdf, out)
    print("готово; рядків, що вилазять за поле:", over)
