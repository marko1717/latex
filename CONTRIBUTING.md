# Contributing to NMT Task Generator

Welcome! We aim to build a database of 5000+ math tasks simulating the Ukrainian NMT exam. This project uses Python generators to create infinite variations of LaTeX-formatted math problems.

## 📁 Project Structure

*   `generators/`: Contains the logic for task generation.
    *   `base.py`: The abstract base class `MathTaskGenerator`.
    *   `arithmetic_progression.py`: Concrete generators for arithmetic patterns.
    *   `geometric_progression.py`: Concrete generators for geometric patterns.
*   `scripts/`: Utility scripts.
    *   `generate_overleaf_doc.py`: The main script to run all generators and produce `.tex` files.
    *   `latex_parser.py`: (Optional) Tools to parse existing LaTeX tasks.
*   `tex/`: The output folder where generated LaTeX files are saved.

## 🚀 How to Add a New Task Type

To add a new mathematical problem (e.g., Logarithms):

1.  **Create a New File**:
    Create `generators/logarithms.py`.

2.  **Define a Generator Class**:
    Inherit from `MathTaskGenerator` and implement the `generate()` method.

    ```python
    import random
    from generators.base import MathTaskGenerator
    
    class LogarithmBaseGenerator(MathTaskGenerator):
        def __init__(self):
            super().__init__()
            self.topic = "Logarithms: Definition"
    
        def generate(self):
            # 1. Define variables (logic)
            base = random.choice([2, 3, 5])
            power = random.randint(2, 4)
            value = base ** power
            
            # 2. Formulate Question
            question = f"Обчисліть $\\log_{{{base}}} {value}$."
            correct_ans = str(power)
            
            # 3. Create Distractors
            distractors = [str(power - 1), str(power + 1), str(base), str(value)]
            
            # 4. Shuffle Options
            result = self.get_random_options(correct_ans, distractors)
            
            # 5. Return Standard Dictionary
            return {
                "question": question,
                "options": result["options"],
                "correct_index": result["correct_index"],
                "correct_letter": result["correct_letter"],
                "raw_correct_value": power
            }
    ```

3.  **Register the Generator**:
    Open `scripts/generate_overleaf_doc.py`:
    *   Import your new class.
    *   Add it to the `generate_all()` function under a new topic section.

4.  **Run Generation**:
    ```bash
    PYTHONPATH=. python3 scripts/generate_overleaf_doc.py
    ```
    Check `tex/` folder for your new document!

## ⚠️ Guidelines

*   **Difficulty**: Adhere to NMT standards. Avoid overly complex calculations without calculators.
*   **Formatting**: Use standard LaTeX for math (`$ $`, `\frac{}{}`).
*   **Randomness**: Ensure corner cases are handled (e.g., avoid division by zero).
*   **Distractors**: Try to generate "smart" distractors (common mistakes) rather than just random numbers.
