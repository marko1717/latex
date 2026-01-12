import random
from generators.base import MathTaskGenerator

class AlgebraSimplificationGenerator(MathTaskGenerator):
    def __init__(self):
        super().__init__()
        self.topic = "Algebra: Polynomials"

    def generate(self):
        # Task: Simplify (a - b)(a + b) or (a + b)^2
        # Variable names
        var1 = random.choice(["a", "x", "m"])
        var2 = random.choice(["b", "y", "n"])
        if var1 == var2: var2 = "y"
        
        # Coefficients/Numbers
        # Type 1: Difference of Squares (Difference of two squares) formula
        # (kx - m)(kx + m) = k^2 x^2 - m^2
        k = random.choice([1, 2, 3, 4, 5])
        m = random.choice([1, 2, 3, 4, 5, 6, 7])
        
        # Formatting
        term1 = f"{k if k>1 else ''}{var1}"
        term2 = m
        
        # Question: (term1 - term2)(term1 + term2)
        question = f"Спростіть вираз $({term1} - {term2})({term1} + {term2})$."
        
        term1_sq_coeff = k*k
        term2_sq = m*m
        
        # Correct: k^2 x^2 - m^2
        t1_sq_str = f"{term1_sq_coeff if term1_sq_coeff>1 else ''}{var1}^2"
        correct_ans = f"${t1_sq_str} - {term2_sq}$"
        
        distractors = set()
        
        # Trap 1: Sum instead of diff
        distractors.add(f"${t1_sq_str} + {term2_sq}$")
        
        # Trap 2: Forgot to square coeff
        # k x^2 - m
        weak_sq_str = f"{k if k>1 else ''}{var1}^2"
        distractors.add(f"${weak_sq_str} - {term2_sq}$")
        
        # Trap 3: Forgot to square constant
        distractors.add(f"${t1_sq_str} - {m}$")
        
        # Trap 4: Middle term? (Square of difference)
        # a^2 - 2ab + b^2
        # 2*k*m
        mid = 2*k*m
        distractors.add(f"${t1_sq_str} - {mid}{var1} + {term2_sq}$")
        
        distractors.discard(correct_ans)
        result = self.get_random_options(correct_ans, list(distractors)[:4])
        
        return {
            "question": question,
            "options": result["options"],
            "correct_index": result["correct_index"],
            "correct_letter": result["correct_letter"],
            "raw_correct_value": 0
        }

class AlgebraFractionGenerator(MathTaskGenerator):
    def __init__(self):
        super().__init__()
        self.topic = "Algebra: Rational Fractions"

    def generate(self):
        # Task: Simplify (x^2 - y^2) / (x - y)
        # Or (a^2 - 2ab + b^2) / (a - b)
        
        var1 = "a"
        var2 = random.choice(["b", random.randint(1, 9)])
        
        # Structure: (VAR1^2 - VAR2^2) / (VAR1 + VAR2) -> VAR1 - VAR2
        op_top = "-"
        op_bot = "-" # result is +
        
        # Randomize signs
        target_sign = random.choice(["+", "-"]) # result
        
        # If result is (a - b): top = a^2 - b^2, bot = a + b.  Wait: (a-b)(a+b)/(a+b) = a-b.
        # If result is (a + b): top = a^2 - b^2, bot = a - b.
        
        denom_sign = "+" if target_sign == "-" else "-"
        
        is_val = isinstance(var2, int)
        val_sq = var2*var2 if is_val else f"{var2}^2"
        
        numerator = f"{var1}^2 - {val_sq}"
        denominator = f"{var1} {denom_sign} {var2}"
        
        question = f"Скоротіть дріб $\\dfrac{{{numerator}}}{{{denominator}}}$."
        
        ans_sign = "-" if denom_sign == "+" else "+"
        correct_ans = f"${var1} {ans_sign} {var2}$"
        
        distractors = set()
        
        # Trap 1: Wrong sign
        opp_sign = "+" if ans_sign == "-" else "-"
        distractors.add(f"${var1} {opp_sign} {var2}$")
        
        # Trap 2:Squares?
        distractors.add(f"${var1}^2 {ans_sign} {var2}$" if not is_val else f"${var1}^2 {ans_sign} {val_sq}$")
        
        # Trap 3: Constant
        distractors.add("$1$")
        distractors.add("$-1$")
        
        distractors.discard(correct_ans)
        result = self.get_random_options(correct_ans, list(distractors)[:4])
        
        return {
            "question": question,
            "options": result["options"],
            "correct_index": result["correct_index"],
            "correct_letter": result["correct_letter"],
            "raw_correct_value": 0
        }

class SymbolicLogGenerator(MathTaskGenerator):
    def __init__(self):
        super().__init__()
        self.topic = "Algebra: Log Properties"

    def generate(self):
        # Task: log_a a^k, or 2^log_2 b
        
        type_ = random.choice(["expon_base", "log_power", "change_base"])
        var = "a"
        
        question = ""
        correct_ans = ""
        distractors = set()
        
        if type_ == "expon_base":
            # 5 ^ (log_5 a)
            base = random.choice([2, 3, 4, 5, 10])
            question = f"Обчисліть ${base}^{{\\log_{{{base}}} {var}}}$."
            correct_ans = f"${var}$"
            distractors = {f"${var}^2$", f"${base}{var}$", f"${base}$", "1"}
            
        elif type_ == "log_power":
            # log_3 3^a
            base = random.choice([2, 3, 5])
            question = f"Обчисліть $\\log_{{{base}}} {base}^{{{var}}}$."
            correct_ans = f"${var}$"
            distractors = {f"${base}{var}$", "1", "0", f"${base}$"}
            
        elif type_ == "change_base":
            # log_{a^k} a
            k = random.randint(2, 5)
            question = f"Обчисліть $\\log_{{{var}^{k}}} {var}$."
            correct_ans = f"$\\frac{{1}}{{{k}}}$"
            distractors = {f"${k}$", f"$-{k}$", f"$-\\frac{{1}}{{{k}}}$", "1"}
            
        distractors.discard(correct_ans)
        result = self.get_random_options(correct_ans, list(distractors)[:4])
        
        return {
            "question": question,
            "options": result["options"],
            "correct_index": result["correct_index"],
            "correct_letter": result["correct_letter"],
            "raw_correct_value": 0
        }
