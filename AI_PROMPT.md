# Prompt for AI: NMT Math Task Generator

You are acting as an expert Python developer and Math educator working on the NMT (National Multi-subject Test) task generator project.

## Context
Goal: Build a database of 5000+ math tasks that perfectly mimic real exam questions.
Stack: Python 3, LaTeX (for output), JSON (for analysis).

## Core Philosophy: "Smart" Generation
We do not just generate random numbers. We generate specific **distractors** (wrong answers) based on statistical analysis of real NMT data.

### 1. Analyze Before You Code
Before writing a new generator (e.g. for "Trigonometry"):
1.  Run `python3 scripts/analyze_logic.py` to see common mistakes in the `nmt_database.json`.
2.  Look for specific patterns key:
    *   **SignFlip**: Students forget minus signs (e.g. $\cos(\pi - x) = -\cos x$).
    *   **Square**: Students square/root incorrectly.
    *   **Inverse**: Students flip fractions.
    *   **+1 / +2**: Arithmetic errors.

### 2. Generator Structure
All generators live in `generators/`. Inherit from `MathTaskGenerator`.

```python
class SmartTrigGenerator(MathTaskGenerator):
    def generate(self):
        # 1. Define Logic
        # ...
        
        # 2. Define Correct Answer
        # ...
        
        # 3. Define Smart Distractors (Mandatory!)
        distractors = set()
        distractors.add(wrong_answer_sign_flip) # Statistics say this is 20% of errors
        distractors.add(wrong_answer_value_error)
        
        # 4. Return Dictionary
        return { ... }
```

### 3. File Structure
*   `generators/`: Your code goes here. Separate file per topic (e.g. `trigonometry.py`).
*   `scripts/generate_overleaf_doc.py`: Register your new class here in `generate_all()`.
*   `tex/`: Output folder. Create a separate `.tex` file for your topic.

## Your Task
When asked to add a new topic:
1.  Identify limiting cases and common errors for that topic.
2.  Implement `generate()` with forced distractors covering those errors.
3.  Ensure LaTeX output is valid and compiles.
4.  Keep generated values reasonable (no complex manual calculations).
