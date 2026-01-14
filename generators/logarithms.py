import random
import math
from generators.base import MathTaskGenerator

class LogEquationGenerator(MathTaskGenerator):
    def __init__(self):
        super().__init__()
        self.topic = "Logarithms: Simple Equation"

    def generate(self):
        # Task: log_a (kx + m) = c
        # Smart Distractors: Square, Inverse, Arithmetic
        
        base = random.choice([2, 3, 4, 5, 0.5, 0.2])
        c = random.choice([1, 2, 3, -1, -2])
        k = random.choice([1, 2, -1, -2])
        
        # Calculate RHS value: base^c
        rhs = base ** c
        
        # We need x to be nice. 
        # kx + m = rhs => kx = rhs - m
        # Let's pick integer x first, then find m
        x = random.randint(-5, 10)
        # Avoid 0 if needed, but log domain matters.
        if rhs - k*x <= 0:
             # Adjust x to ensure argument is positive initially 
             # Actually, we define m such that argument IS rhs.
             pass
             
        m = rhs - k*x
        
        # To ensure readability, we prefer integers for m if possible.
        # If rhs is fraction, m might be fraction.
        # Let's force base^c to be integer for Level 1 tasks?
        if isinstance(base, float) or c < 0:
             # Maybe harder task.
             pass
        else:
             # Integer case
             pass

        # Simplification: Let's stick to integer arguments for now or simple decimals
        if random.random() < 0.5:
             # Integer base
             base = random.choice([2, 3, 5])
             c = random.randint(1, 4)
             val_pow = base ** c
             k = random.choice([1, 2])
             m = random.randint(-10, 10)
             # equation: log_base (kx + m) = c
             # kx + m = val_pow => kx = val_pow - m
             # Make sure (val_pow - m) is divisible by k
             remainder = (val_pow - m) % k
             m += remainder 
             
             x_corr = (val_pow - m) // k
             
        else:
             # Fraction base or negative power
             base_opts = [(2, -1), (2, -2), (3, -1), (5, -1), (0.5, -1), (0.2, -1)]
             b_idx, c_val = random.choice(base_opts)
             base = b_idx
             c = c_val 
             if base == 0.5: c = random.choice([-1, -2, -3])
             
             val_pow = base ** c 
             # e.g 2^-1 = 0.5. 0.5^-2 = 4.
             
             k = 1
             m = random.randint(-5, 5)
             x_corr = val_pow - m
             
             # Format floats
             if isinstance(x_corr, float) and x_corr.is_integer(): x_corr = int(x_corr)

        def fmt(num):
             if isinstance(num, float):
                 if num.is_integer(): return str(int(num))
                 return str(round(num, 3)).replace('.', '{,}')
             return str(num)

        # LaTeX construction
        arg = "x"
        if k != 1: arg = f"{k}x"
        if m > 0: arg += f"+{m}"
        elif m < 0: arg += f"{m}"
        
        question = f"Розв'яжіть рівняння $\\log_{{{fmt(base)}}} ({arg}) = {c}$."
        correct_ans = fmt(x_corr)
        
        distractors = set()
        
        # === SMART DISTRACTORS ===
        # 1. Mistake: x = base * c - m (multiply instead of power)
        try:
            wrong_val = (base * c - m) / k
            distractors.add(fmt(wrong_val))
        except: pass
        
        # 2. Mistake: Ignore m (kx = base^c)
        try:
            wrong_val = (base**c) / k
            distractors.add(fmt(wrong_val))
        except: pass
        
        # 3. Mistake: SignFlip of c (base^-c)
        try:
            wrong_val = (base**(-c) - m) / k
            distractors.add(fmt(wrong_val))
        except: pass
        
        # 4. Square Confusion: x^2 instead of base^c? Or 2^c
        
        # Fill random
        while len(distractors) < 4:
            distractors.add(fmt(x_corr + random.choice([1, -1, 2, -2, 10, -10])))
            
        distractors.discard(correct_ans)
        
        result = self.get_random_options(correct_ans, list(distractors)[:4])
        return {
            "question": question,
            "options": result["options"],
            "correct_index": result["correct_index"],
            "correct_letter": result["correct_letter"],
            "raw_correct_value": x_corr
        }

class LogInequalityGenerator(MathTaskGenerator):
    def __init__(self):
        super().__init__()
        self.topic = "Logarithms: Inequality"

    def generate(self):
        # Task: log_a x > b.
        # KEY LOGIC: If a < 1, sign flips! This is the #1 NMT trap.
        
        base = random.choice([2, 5, 0.5, 0.2, 0.3]) # Mixed bases
        is_fraction = base < 1
        
        b = random.randint(1, 3)
        sign = random.choice([">", "<", "\\geqslant", "\\leqslant"])
        
        # Question: log_a x [sign] b
        
        val = base ** b
        
        def fmt(num):
             if isinstance(num, float):
                 if num.is_integer(): return str(int(num))
                 return str(round(num, 3)).replace('.', '{,}')
             return str(num)
             
        question = f"Розв'яжіть нерівність $\\log_{{{fmt(base)}}} x {sign} {b}$."
        
        # Solve logic
        # 1. Domain: x > 0 always!
        # 2. If base > 1: preserve sign
        # 3. If base < 1: flip sign
        
        limit = fmt(val)
        
        # Determine interval
        # Cases: x > val, x < val
        # BUT combined with x > 0
        
        effective_sign = sign
        if is_fraction:
            # Flip logic
            if ">" in sign: effective_sign = sign.replace(">", "<")
            elif "<" in sign: effective_sign = sign.replace("<", ">")
            
        answer = ""
        
        # Construct interval notation
        # x > val -> (val; +inf)
        # x >= val -> [val; +inf)
        # x < val -> (0; val)  <-- DOMAIN CHECK
        # x <= val -> (0; val] <-- DOMAIN CHECK
        
        if ">" in effective_sign:
            left = "("
            if "=" in effective_sign: left = "["
            answer = f"{left}{limit}; +\\infty)"
        else:
            right = ")"
            if "=" in effective_sign: right = "]"
            answer = f"(0; {limit}{right}"
            
        correct_ans = answer
        
        distractors = set()
        
        # Trap 1: Forgot domain x>0 (for < cases, write (-inf; val))
        if "<" in effective_sign:
             right = ")"
             if "=" in effective_sign: right = "]"
             distractors.add(f"(-\\infty; {limit}{right}")
             
        # Trap 2: Forgot to flip sign (The BIG one)
        # Generate the answer as if base > 1 (or <1 if it was >1)
        fake_sign = sign # Don't flip
        fake_ans = ""
        if ">" in fake_sign:
            left = "("
            if "=" in fake_sign: left = "["
            fake_ans = f"{left}{limit}; +\\infty)"
        else:
            right = ")"
            if "=" in fake_sign: right = "]"
            fake_ans = f"(0; {limit}{right}"
            
        if fake_ans != correct_ans:
            distractors.add(fake_ans)
            
        # Trap 3: Wrong value (Arithmetic +/-)
        # e.g. base * b instead of base^b
        try:
             wrong_val = fmt(base * b)
             if ">" in effective_sign:
                left = "("
                if "=" in effective_sign: left = "["
                distractors.add(f"{left}{wrong_val}; +\\infty)")
        except: pass

        # Fill random intervals
        while len(distractors) < 4:
            distractors.add(f"({random.randint(-5,5)}; {random.randint(6, 10)})")

        distractors.discard(correct_ans)
        result = self.get_random_options(correct_ans, list(distractors)[:4])
        
        return {
            "question": question,
            "options": result["options"],
            "correct_index": result["correct_index"],
            "correct_letter": result["correct_letter"],
            "raw_correct_value": answer
        }

class LogValueGenerator(MathTaskGenerator):
    def __init__(self):
        super().__init__()
        self.topic = "Logarithms: Evaluate Value"
        
    def generate(self):
        # Task: Evaluate log_a b
        # Distractors: Inverse, Square
        
        # Pairs (base, value, ans)
        pairs = [
            (2, 4, 2), (2, 8, 3), (2, 16, 4), (2, 32, 5), (2, 0.5, -1), (2, 0.25, -2),
            (3, 9, 2), (3, 27, 3), (3, 81, 4), (3, 1/3, -1),
            (5, 25, 2), (5, 125, 3), (5, 0.2, -1),
            (0.5, 4, -2), (0.5, 2, -1), (0.2, 25, -2)
        ]
        
        base, val, ans = random.choice(pairs)
        
        def fmt(num):
             if isinstance(num, float):
                 if num.is_integer(): return str(int(num))
                 return str(round(num, 3)).replace('.', '{,}')
             return str(num)
             
        question = f"Обчисліть значення виразу $\\log_{{{fmt(base)}}} {fmt(val)}$."
        correct_ans = fmt(ans)
        
        distractors = set()
        
        # 1. Inverse: ans vs 1/ans
        if ans != 0:
            try:
                distractors.add(fmt(1/ans))
            except: pass
            
        # 2. Square confusion: base/val
        try:
             distractors.add(fmt(val/base))
        except: pass
        
        # 3. Sign flip
        distractors.add(fmt(-ans))
        
        # 4. Additive
        distractors.add(fmt(ans+1))
        distractors.add(fmt(ans-1))
        
        distractors.discard(correct_ans)
        result = self.get_random_options(correct_ans, list(distractors)[:4])
        
        return {
            "question": question,
            "options": result["options"],
            "correct_index": result["correct_index"],
            "correct_letter": result["correct_letter"],
            "raw_correct_value": ans
        }

if __name__ == "__main__":
    pass
