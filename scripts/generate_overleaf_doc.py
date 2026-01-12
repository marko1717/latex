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
\pgfplotsset{compat=1.18}

\usetikzlibrary{calc,patterns,angles,quotes,intersections,babel}
\usetikzlibrary{3d}

\usepackage{xcolor}
\usepackage{array}
\usepackage{fancyhdr}
\usepackage{multirow}

% Кольори
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

% === КОМАНДИ ===

% Таблиця відповідей для відповідностей
\newcommand{\answerGrid}{
    \begingroup
    \renewcommand{\arraystretch}{1.3} 
    \setlength{\tabcolsep}{7pt} 
    \begin{tabular}{r|c|c|c|c|c|}
         \multicolumn{1}{c}{} & \multicolumn{1}{c}{\textbf{А}} & \multicolumn{1}{c}{\textbf{Б}} & \multicolumn{1}{c}{\textbf{В}} & \multicolumn{1}{c}{\textbf{Г}} & \multicolumn{1}{c}{\textbf{Д}} \\ \cline{2-6}
         \textbf{1} & & & & & \\ \cline{2-6}
         \textbf{2} & & & & & \\ \cline{2-6}
         \textbf{3} & & & & & \\ \cline{2-6}
    \end{tabular}
    \endgroup
}

% Макет для завдань на відповідність
\newcommand{\matchingLayout}[3]{
    \noindent
    \begin{minipage}[t]{0.40\textwidth}
        #1
    \end{minipage}%
    \hfill
    \begin{minipage}[t]{0.28\textwidth}
        #2
    \end{minipage}%
    \hfill
    \begin{minipage}[t]{0.30\textwidth}
        \vspace{0pt}
        \begin{flushright}
        #3
        \end{flushright}
    \end{minipage}
}

% Стандартна таблиця відповідей
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

% Таблиця для відповідей із дробами
\newcommand{\answerTableTall}[5]{
\begin{center}
\begin{tabular}{|*{5}{>{\centering\arraybackslash}m{2.8cm}|}}
\hline
\rule[-0.3cm]{0pt}{0.8cm}\textbf{А} & \textbf{Б} & \textbf{В} & \textbf{Г} & \textbf{Д} \\
\hline
\rule[-0.9cm]{0pt}{2.0cm}#1 & 
\rule[-0.9cm]{0pt}{2.0cm}#2 & 
\rule[-0.9cm]{0pt}{2.0cm}#3 & 
\rule[-0.9cm]{0pt}{2.0cm}#4 & 
\rule[-0.9cm]{0pt}{2.0cm}#5 \\
\hline
\end{tabular}
\end{center}
}

\newcommand{\nmtyear}[1]{\hfill{\small\color{yearcolor}(AI Gen)}}

\begin{document}

\vspace{1cm}

\begin{center}
{\Large\textbf{\color{headerblue}ЗГЕНЕРОВАНІ ЗАВДАННЯ (AI)}}
\end{center}

\begin{center}
{\large Тема: \textbf{PLACEHOLDER_TOPIC}}
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
    header = LATEX_HEADER.replace("PLACEHOLDER_TOPIC", topic_name)
    
    for gen in generators:
        content += f"% === {gen.topic} ===\n"
        # Generate 10 examples per type for scale? Or keep 2 for now?
        # User wants 5000 tasks eventually. Let's do 5 per type for now.
        # Generate 20 examples per type (mix of single and matching)
        for _ in range(20):
            task = gen.generate()
            
            if task.get("type") == "matching":
                # Layout for Matching Task
                # 1. Questions Block
                q_block = ""
                for i, q in enumerate(task["questions"]):
                    # Strip "Find..." text if verbose, but usually q is a math expression
                    # The user layout has "1  expr", "2 expr"
                    # clean up q: remove "Calculate" or "Solve" text? 
                    # For now just dump it.
                    # Usually generators return "Solve ..." text.
                    # We might want to strip that for matching.
                    # But let's just put it in.
                    q_block += f"\\textbf{{{i+1}}} \\quad {q}\n\n\\vspace{{0.4cm}}\n\n"
                
                # 2. Options Block
                o_block = ""
                letters = ["А", "Б", "В", "Г", "Д"]
                for i, opt in enumerate(task["options"]):
                    o_block += f"\\textbf{{{letters[i]}}} \\quad {opt}\n\n\\vspace{{0.4cm}}\n\n"
                
                # 3. Grid Block
                # We use standard \answerGrid command
                grid_block = "\\answerGrid"
                
                content += f"\\noindent\\textbf{{{task_counter}.}} Установіть відповідність між виразом (1--3) та його значенням (А--Д). \\nmtyear{{2026}}\n\\vspace{{0.3cm}}\n\n"
                content += f"\\matchingLayout{{\n\\textit{{Вираз}}\n\n{q_block}}}{{\n\\textit{{Значення}}\n\n{o_block}}}{{{grid_block}}}\n\n"
                content += "\\vspace{0.8cm}\n\n"
                
            else:
                # Standard Task
                question = task["question"]
                options = task["options"]
                
                content += f"\\noindent\\makebox[1.5em][l]{{\\textbf{{{task_counter}.}}}}\\parbox[t]{{\\dimexpr\\textwidth-1.5em}}{{{question} \\nmtyear{{2026}}}}\n\\vspace{{0.3cm}}\n\n"
                
                opts = task["options"]
                # Use answerTableTall if options are fractions? Or standard? 
                # Let's check length. If long, use Tall.
                is_tall = any("frac" in str(o) for o in opts)
                table_cmd = "answerTableTall" if is_tall else "answerTable"
                
                content += f"\\{table_cmd}{{{opts[0]}}}{{{opts[1]}}}{{{opts[2]}}}{{{opts[3]}}}{{{opts[4]}}}\n\n"
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
    from generators.matching import MatchingTaskGenerator
    
    log_gens = [
        LogValueGenerator(), # Single
        MatchingTaskGenerator(LogValueGenerator), # Matching (3 items)
        LogEquationGenerator(), # Single
        LogInequalityGenerator(),
        MatchingTaskGenerator(LogEquationGenerator) # Matching Equations? Why not.
    ]
    generate_topic_doc("Логарифмічні вирази та рівняння", log_gens, "tex/logarithms.tex")

    # 4. Trigonometry

    # 4. Trigonometry
    from generators.trigonometry import TrigValueGenerator, TrigReductionGenerator, TrigEquationGenerator
    trig_gens = [
        TrigValueGenerator(),
        MatchingTaskGenerator(TrigValueGenerator), # Matching Values
        TrigReductionGenerator(),
        MatchingTaskGenerator(TrigReductionGenerator), # Matching Reductions
        TrigEquationGenerator()
    ]
    generate_topic_doc("Тригонометричні вирази та рівняння", trig_gens, "tex/trigonometry.tex")

if __name__ == "__main__":
    generate_all()
