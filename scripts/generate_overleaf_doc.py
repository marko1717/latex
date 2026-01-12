import os
import random
from generators.arithmetic_progression import (
    ArithmeticFindDifferentGenerator,
    ArithmeticMemberDifferenceGenerator,
    ArithmeticSumGenerator,
    ArithmeticTermPropertiesGenerator,
    ArithmeticMiddleTermGenerator,
    ArithmeticFormulaSearchGenerator,
    ArithmeticWordProblemGenerator
)
from generators.geometric_progression import (
    GeometricFindTermGenerator,
    GeometricRatioGenerator,
    GeometricFormulaGenerator,
    GeometricSumGenerator,
    GeometricWordProblemGenerator
)

OUTPUT_FILE = "generated_tasks.tex"

LATEX_HEADER = r"""\documentclass[14pt]{extarticle}
\usepackage{fontspec}
\usepackage{polyglossia}
\setdefaultlanguage{ukrainian}

\defaultfontfeatures{Ligatures=TeX}
\setmainfont{Liberation Serif}
\setsansfont{Liberation Sans}
\setmonofont{Liberation Mono}

\usepackage[a4paper,margin=1.5cm,bottom=2cm,top=2cm]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{enumitem}
\usepackage{tikz}
\usepackage{pgfplots}
\pgfplotsset{compat=1.16}

\usetikzlibrary{calc,patterns,angles,quotes,intersections,babel}
\usetikzlibrary{3d}
\definecolor{woodinner}{RGB}{222, 184, 135}
\definecolor{woodouter}{RGB}{139, 69, 19}
\usepackage{xcolor}
\usepackage{array}
\usepackage{fancyhdr}
\usepackage{multirow}

\definecolor{headerblue}{RGB}{0, 102, 204}
\definecolor{yearcolor}{RGB}{128, 0, 128}

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\fancyfoot[C]{\thepage}

\setlength{\headheight}{15pt}
\setlength{\headsep}{10pt}
\setlength{\footskip}{25pt}

\widowpenalty=10000
\clubpenalty=10000

\newcommand{\answerTable}[5]{
\begin{center}
\begin{tabular}{|*{5}{>{\centering\arraybackslash}m{2.8cm}|}}
\hline
\rule[-0.3cm]{0pt}{0.8cm}\textbf{А} & \textbf{Б} & \textbf{В} & \textbf{Г} & \textbf{Д} \\
\hline
\rule[-0.4cm]{0pt}{1.0cm}#1 & \rule[-0.4cm]{0pt}{1.0cm}#2 & \rule[-0.4cm]{0pt}{1.0cm}#3 & \rule[-0.4cm]{0pt}{1.0cm}#4 & \rule[-0.4cm]{0pt}{1.0cm}#5 \\
\hline
\end{tabular}
\end{center}
}

\newcommand{\shortAnswer}{
\vspace{0.3cm}
\noindent\hspace{1cm}Відповідь: \framebox(18,18){}\framebox(18,18){}\framebox(18,18){}\framebox(18,18){}{,}\framebox(18,18){}\framebox(18,18){}\framebox(18,18){}
\vspace{0.5cm}
}

\newcommand{\nmtyear}[1]{\hfill{\small\color{yearcolor}(AI Gen)}}

\begin{document}

\begin{center}
{\Large\textbf{\color{headerblue}ЗГЕНЕРОВАНІ ЗАВДАННЯ (AI)}}
\end{center}

\begin{center}
{\large Тема: \textbf{Арифметична та Геометрична прогресії}}
\end{center}

\vspace{0.5cm}
"""

LATEX_FOOTER = r"""
\end{document}
"""

def generate_topic_doc(topic_name, generators, output_filename):
    content = ""
    task_counter = 1
    
    # Header specific to topic? Or generic?
    # Using generic header with specific title
    header = LATEX_HEADER.replace("Арифметична та Геометрична прогресії", topic_name)
    
    for gen in generators:
        content += f"% === {gen.topic} ===\n"
        # Generate 10 examples per type for scale? Or keep 2 for now?
        # User wants 5000 tasks eventually. Let's do 5 per type for now.
        for _ in range(5):
            task = gen.generate()
            question = task["question"]
            options = task["options"]
            
            content += f"\\noindent\\makebox[1.5em][l]{{\\textbf{{{task_counter}.}}}}\\parbox[t]{{\\dimexpr\\textwidth-1.5em}}{{{question} \\nmtyear{{2026}}}}\n\n"
            
            opts = task["options"]
            content += f"\\answerTable{{{opts[0]}}}{{{opts[1]}}}{{{opts[2]}}}{{{opts[3]}}}{{{opts[4]}}}\n\n"
            content += "\\vspace{0.5cm}\n\n"
            
            task_counter += 1

    full_latex = header + content + LATEX_FOOTER
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(full_latex)
    
    print(f"Generated {task_counter-1} tasks to {output_filename}")

def generate_all():
    # 1. Arithmetic
    arithmetic_gens = [
        ArithmeticFindDifferentGenerator(),
        ArithmeticMemberDifferenceGenerator(),
        ArithmeticSumGenerator(),
        ArithmeticTermPropertiesGenerator(),
        ArithmeticMiddleTermGenerator(),
        ArithmeticFormulaSearchGenerator(),
        ArithmeticWordProblemGenerator()
    ]
    generate_topic_doc("Арифметична прогресія", arithmetic_gens, "tex/arithmetic_progression.tex")
    
    # 2. Geometric
    geometric_gens = [
        GeometricFindTermGenerator(),
        GeometricRatioGenerator(),
        GeometricFormulaGenerator(),
        GeometricSumGenerator(),
        GeometricWordProblemGenerator()
    ]
    generate_topic_doc("Геометрична прогресія", geometric_gens, "tex/geometric_progression.tex")

    # 3. Logarithms
    from generators.logarithms import LogEquationGenerator, LogInequalityGenerator, LogValueGenerator
    log_gens = [
        LogValueGenerator(),
        LogEquationGenerator(),
        LogInequalityGenerator()
    ]
    generate_topic_doc("Логарифмічні вирази та рівняння", log_gens, "tex/logarithms.tex")

if __name__ == "__main__":
    generate_all()
