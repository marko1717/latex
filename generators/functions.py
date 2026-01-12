import random
from generators.base import MathTaskGenerator

class FunctionShiftGenerator(MathTaskGenerator):
    def __init__(self):
        super().__init__()
        self.topic = "Functions: Graph Shifts"

    def generate(self):
        # Task: Given graph of y=f(x), find equation for shifted graph OR vice versa.
        # Text-based: "Graph of g(x) is obtained from f(x) by moving 3 units right. Find g(x)."
        
        # Directions
        shifts = [
            ("праворуч", "right", "-", "x"), # f(x - a)
            ("ліворуч", "left", "+", "x"),   # f(x + a)
            ("вгору", "up", "+", "y"),       # f(x) + a
            ("вниз", "down", "-", "y")       # f(x) - a
        ]
        
        name_move, direction, sign_symbol, axis = random.choice(shifts)
        units = random.randint(1, 5)
        
        question = f"Графік функції $y = f(x)$ паралельно перенесли вздовж осі $O{axis}$ на {units} одиниць {name_move}. " \
                   f"Укажіть формулу для отриманої функції $y = g(x)$."
                   
        # Logic
        correct_expr = ""
        if axis == "x":
            correct_expr = f"f(x {sign_symbol} {units})"
        else:
            correct_expr = f"f(x) {sign_symbol} {units}"
            
        correct_ans = f"$y = {correct_expr}$"
        
        distractors = set()
        
        # Smart Distractor 1: Wrong Sign (The classic trap)
        opp_sign = "+" if sign_symbol == "-" else "-"
        wrong_expr = ""
        if axis == "x":
            wrong_expr = f"f(x {opp_sign} {units})"
        else:
            wrong_expr = f"f(x) {opp_sign} {units}"
        distractors.add(f"$y = {wrong_expr}$")
        
        # Smart Distractor 2: Wrong Axis
        # if x-shift, show y-shift
        wrong_expr_axis = ""
        if axis == "x":
            # Show f(x) +/- units
            wrong_expr_axis = f"f(x) {sign_symbol} {units}"
        else:
            # Show f(x +/- units)
            wrong_expr_axis = f"f(x {sign_symbol} {units})"
        distractors.add(f"$y = {wrong_expr_axis}$")
        
        # Smart Distractor 3: Wrong Axis + Wrong Sign
        wrong_expr_axis_sign = ""
        if axis == "x":
             wrong_expr_axis_sign = f"f(x) {opp_sign} {units}"
        else:
             wrong_expr_axis_sign = f"f(x {opp_sign} {units})"
        distractors.add(f"$y = {wrong_expr_axis_sign}$")
        
        # Distractor 4: Multiplicative? f(ax)
        distractors.add(f"$y = {units}f(x)$")
        
        distractors.discard(correct_ans)
        result = self.get_random_options(correct_ans, list(distractors)[:4])
        
        return {
            "question": question,
            "options": result["options"],
            "correct_index": result["correct_index"],
            "correct_letter": result["correct_letter"],
            "raw_correct_value": 0 # Not numerical
        }

class FunctionDomainGenerator(MathTaskGenerator):
    def __init__(self):
        super().__init__()
        self.topic = "Functions: Domain"

    def generate(self):
        # Task: Find domain of function.
        # Types: sqrt(x), size/x, log(x)
        
        type_ = random.choice(["sqrt", "div", "log"])
        
        # f(x) = (Something)
        # Inside is usually linear: kx + b
        
        k = random.choice([1, -1])
        b = random.randint(1, 9)
        sign_str = "+" if b > 0 else ""
        
        inner_expr = f"{k if k!=1 else ''}x {sign_str} {b}"
        if k == -1: inner_expr = f"{b} - x"
        
        func_display = ""
        answer_interval = ""
        
        # Critical point: inner = 0 => x = -b/k
        # if k=1: x+b=0 -> x=-b. 
        # if k=-1: b-x=0 -> x=b.
        crit_val = -b if k==1 else b
        
        if type_ == "sqrt":
            func_display = f"$y = \\sqrt{{{inner_expr}}}$"
            # Require inner >= 0
            if k == 1: # x >= -b
                answer_interval = f"[{crit_val}; +\\infty)"
            else: # b - x >= 0 => x <= b
                answer_interval = f"(-\\infty; {crit_val}]"
                
        elif type_ == "div":
            num = random.randint(1, 5)
            func_display = f"$y = \\frac{{{num}}}{{{inner_expr}}}$"
            # Require inner != 0
            answer_interval = f"(-\\infty; {crit_val}) \\cup ({crit_val}; +\\infty)"
            
        elif type_ == "log":
            base = random.choice([2, 3, 5, 0.5])
            func_display = f"$y = \\log_{{{base}}} ({inner_expr})$"
            # Require inner > 0
            if k == 1: # x > -b
                answer_interval = f"({crit_val}; +\\infty)"
            else: # b - x > 0 => x < b
                answer_interval = f"(-\\infty; {crit_val})"
        
        question = f"Укажіть область визначення функції {func_display}."
        correct_ans = answer_interval
        
        distractors = set()
        
        # Smart Distractor 1: Bracket error (Exclusive vs Inclusive)
        if "[" in correct_ans:
            distractors.add(correct_ans.replace("[", "(").replace("]", ")"))
        elif "(" in correct_ans and "cup" not in correct_ans:
             # simple (a; b), make it [a; b]?
             # But domains often infinite.
             temp = correct_ans.replace("(", "[").replace(")", "]")
             # Fix infinity brackets back to parens
             temp = temp.replace("[-\\infty", "(-\\infty").replace("+\\infty]", "+\\infty)")
             distractors.add(temp)
             
        # Smart Distractor 2: Direction error (Greater vs Less)
        # e.g. instead of (2; inf), give (-inf; 2)
        if "\\cup" not in correct_ans:
            if "+\\infty" in correct_ans:
                # Make it -inf
                 # Keep bracket style
                bra =correct_ans[0]
                distractors.add(f"(-\\infty; {crit_val}{']' if bra=='[' else ')'}")
            else:
                 # It was -inf, make it +inf
                ket = correct_ans[-1]
                distractors.add(f"{'[' if ket==']' else '('}{crit_val}; +\\infty)")
        else:
             # It's a division (union). Distractor: Just one point excluded? Or just one interval?
             # D: (-inf; crit) or (crit; +inf)
             distractors.add(f"(-\\infty; {crit_val})")
             distractors.add(f"({crit_val}; +\\infty)")
             
        # Smart Distractor 3: Sign error on value
        # crit_val vs -crit_val
        wrong_val = -crit_val
        distractors.add(correct_ans.replace(str(crit_val), str(wrong_val)))
        
        distractors.discard(correct_ans)
        result = self.get_random_options(correct_ans, list(distractors)[:4])
        
        return {
            "question": question,
            "options": result["options"],
            "correct_index": result["correct_index"],
            "correct_letter": result["correct_letter"],
            "raw_correct_value": 0
        }
