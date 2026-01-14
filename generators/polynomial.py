import random
from generators.base import MathTaskGenerator

class PolynomialSimplificationGenerator(MathTaskGenerator):
    def __init__(self):
        super().__init__()
        self.topic = "Polynomials"

    def generate(self):
        # Template: A * xy^2 - (B * xy^2 - C * x^2y)
        # Or: A * x^n * y^m - (B * x^n * y^m - C * x^k * y^l)
        # Logic: Combine like terms.
        
        # Random coefficients
        A = random.randint(-10, 10)
        B = random.randint(-10, 10)
        C = random.randint(-10, 10)
        
        # Avoid 0 to keep it interesting
        if A == 0: A = 2
        if B == 0: B = 3
        if C == 0: C = 4
        
        # Powers
        n = 1
        m = 2
        # For the second part inside parenthesis
        # We need distinct variable parts to make it a polynomial
        # Original task: -2xy^2 - (3xy^2 - 2x^2y)
        # Part 1: xy^2 (coeff A)
        # Part 2: xy^2 (coeff B) -- Like term with A
        # Part 3: x^2y (coeff C) -- Unlike term
        
        # Result: (A - B) xy^2 + C x^2y
        # Note: minus before parenthesis applies to -C => +C
        
        # Construct Question LaTeX
        # Handle signs nicely
        def format_term(coeff, vars_tex, is_first=False):
            if coeff == 0: return ""
            sign = ""
            if coeff < 0:
                sign = "-"
            elif not is_first:
                sign = "+"
            
            abs_c = abs(coeff)
            c_str = str(abs_c) if abs_c != 1 else ""
            if abs_c == 1 and vars_tex == "": c_str = "1"
            
            return f"{sign}{c_str}{vars_tex}"

        # Term 1: A xy^2
        term1 = format_term(A, "xy^2", is_first=True)
        
        # Inside parens: B xy^2 - C x^2y
        # Wait, original was (3xy^2 - 2x^2y). So it was B * xy^2 + (-C) * x^2y ?
        # Let's define the expression as: Term1 - (Term2 + Term3)
        # Term1 = A xy^2
        # Term2 = B xy^2
        # Term3 = D x^2y
        
        D = -C # Let's say inner term is -C for variety
        
        inner_term1 = format_term(B, "xy^2", is_first=True)
        inner_term2 = format_term(D, "x^2y", is_first=False) 
        
        question = f"${term1} - ({inner_term1} {inner_term2}) = $"
        
        # Solution:
        # A xy^2 - B xy^2 - D x^2y
        # = (A - B) xy^2 - D x^2y
        
        res_coeff_1 = A - B
        res_coeff_2 = -D 
        
        correct_ans = format_term(res_coeff_1, "xy^2", is_first=True) + " " + format_term(res_coeff_2, "x^2y", is_first=False)
        correct_ans = correct_ans.strip()
        
        # Distractors
        distractors = []
        
        # Error 1: Forgot to distribute minus to the second term
        # Result: (A - B) xy^2 + D x^2y (Wrong sign on second term)
        err1 = format_term(A - B, "xy^2", is_first=True) + " " + format_term(D, "x^2y", is_first=False)
        distractors.append(err1.strip())
        
        # Error 2: Added B instead of subtracted (Sign error on first term)
        # Result: (A + B) xy^2 - D x^2y
        err2 = format_term(A + B, "xy^2", is_first=True) + " " + format_term(-D, "x^2y", is_first=False)
        distractors.append(err2.strip())
        
        # Error 3: Mixed up variables (treated all as like terms?) 
        # e.g., (A - B - D) xy^2
        err3 = format_term(A - B - D, "xy^2", is_first=True)
        distractors.append(err3.strip())
        
        # Error 4: Completely random signs
        err4 = format_term(- (A - B), "xy^2", is_first=True) + " " + format_term(res_coeff_2, "x^2y", is_first=False)
        distractors.append(err4.strip())

        return {
            "question": question,
            "correct_answer": correct_ans,
            "distractors": distractors
        }

if __name__ == "__main__":
    gen = PolynomialSimplificationGenerator()
    task = gen.generate()
    print("Question:", task["question"])
    print("Correct:", task["correct_answer"])
    print("Distractors:", task["distractors"])
