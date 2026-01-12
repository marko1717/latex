# NMT Task Generator (Math Quest)

This project automates the creation of mathematical problems for the Ukrainian NMT (National Multi-subject Test). It uses Python to generate unique versions of tasks based on templates reverse-engineered from real exam questions.

## 🎯 Goals
*   Generate **5000+ unique tasks** for training.
*   Cover all NMT math topics (Algebra, Geometry, Statistics).
*   Output ready-to-print LaTeX documents compatible with Overleaf.

## 🛠 Usage

1.  **Clone the repo**:
    ```bash
    git clone https://github.com/marko1717/latex.git
    cd latex
    ```

2.  **Generate Tasks**:
    Run the generation script. This will create clean LaTeX files in the `tex/` directory.
    ```bash
    PYTHONPATH=. python3 scripts/generate_overleaf_doc.py
    ```

3.  **View Results**:
    Open `tex/arithmetic_progression.tex` or `tex/geometric_progression.tex`. You can compile them with any LaTeX editor or upload to Overleaf.

## 📚 Topics Covered
*   **Arithmetic Progression**: $d$, $S_n$, term properties, word problems, diagrams.
*   **Geometric Progression**: $q$, $S_n$, growth problems, formulas.

## 🤝 Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for instructions on how to add new task types.
