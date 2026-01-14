import random
import math
from generators.base import MathTaskGenerator

class TrigValueGenerator(MathTaskGenerator):
    def __init__(self):
        super().__init__()
        self.topic = "Trigonometry: Values"

    def generate(self):
        # Task: Calculate simple trig value, e.g. cos(210), sin(4pi/3)
        # Smart Distractors: SignFlip (wrong quadrant), ValueSwap (1/2 vs sqrt3/2)
        
        # Angles in degrees and their reference
        # (angle, ref_angle, name, value_sin, value_cos)
        # We'll use strings for values to keep latex pretty
        
        # Common values: 30, 45, 60, etc.
        # But we want > 90 to test signs.
        
        angles = [
            (120, 60, "\\frac{2\\pi}{3}"),
            (135, 45, "\\frac{3\\pi}{4}"),
            (150, 30, "\\frac{5\\pi}{6}"),
            (210, 30, "\\frac{7\\pi}{6}"),
            (225, 45, "\\frac{5\\pi}{4}"),
            (240, 60, "\\frac{4\\pi}{3}"),
            (300, 60, "\\frac{5\\pi}{3}"),
            (315, 45, "\\frac{7\\pi}{4}"),
            (330, 30, "\\frac{11\\pi}{6}")
        ]
        
        angle_deg, ref_deg, angle_rad = random.choice(angles)
        func = random.choice(["sin", "cos", "tg"])
        
        # Values map
        vals = {
            30: {"sin": 0.5, "cos": 0.866, "tg": 0.577, "s_str": "\\frac{1}{2}", "c_str": "\\frac{\\sqrt{3}}{2}", "t_str": "\\frac{1}{\\sqrt{3}}"},
            45: {"sin": 0.707, "cos": 0.707, "tg": 1.0, "s_str": "\\frac{\\sqrt{2}}{2}", "c_str": "\\frac{\\sqrt{2}}{2}", "t_str": "1"},
            60: {"sin": 0.866, "cos": 0.5, "tg": 1.732, "s_str": "\\frac{\\sqrt{3}}{2}", "c_str": "\\frac{1}{2}", "t_str": "\\sqrt{3}"}
        }
        ref_vals = vals[ref_deg]
        
        # Calculate Sign
        sign = 1
        if func == "sin":
            if 180 < angle_deg < 360: sign = -1
        elif func == "cos":
            if 90 < angle_deg < 270: sign = -1
        elif func == "tg":
            if 90 < angle_deg < 180 or 270 < angle_deg < 360: sign = -1
            
        # Correct Value
        val_str = ""
        val_raw = 0
        if func == "sin": 
            val_str = ref_vals["s_str"]
            val_raw = ref_vals["sin"]
        elif func == "cos": 
            val_str = ref_vals["c_str"]
            val_raw = ref_vals["cos"]
        else:
            val_str = ref_vals["t_str"]
            val_raw = ref_vals["tg"]
            
        if sign == -1:
            val_str = "-" + val_str
            val_raw = -val_raw
            
        # Question
        q_angle = f"{angle_deg}^\\circ" if random.random() < 0.5 else angle_rad
        func_tex = "\\tan" if func == "tg" else f"\\{func}"
        question = f"Обчисліть значення виразу ${func_tex} {q_angle}$."
        
        correct_ans = val_str
        distractors = set()
        
        # Smart Distractors
        # 1. SignFlip (Most common error!)
        if sign == -1:
            distractors.add(val_str.replace("-", ""))
        else:
            distractors.add("-" + val_str)
            
        # 2. Function Swap (sin vs cos)
        # e.g. if answer is 1/2, distractor is sqrt(3)/2
        wrong_raw = ""
        if ref_deg != 45: # at 45 sin=cos
            if func == "sin": wrong_raw = ref_vals["c_str"]
            elif func == "cos": wrong_raw = ref_vals["s_str"]
            elif func == "tg": 
                # tg vs ctg
                if ref_deg == 30: wrong_raw = "\\sqrt{3}"
                if ref_deg == 60: wrong_raw = "\\frac{1}{\\sqrt{3}}"
                
            if wrong_raw:
                distractors.add(wrong_raw)
                distractors.add("-" + wrong_raw)
                
        # Fill randoms
        defaults = ["0", "1", "-1", "\\frac{1}{2}", "-\\frac{1}{2}", "\\frac{\\sqrt{3}}{2}"]
        for d in defaults:
            distractors.add(d)
            
        distractors.discard(correct_ans)
        result = self.get_random_options(correct_ans, list(distractors)[:4])
        
        return {
            "question": question,
            "options": result["options"],
            "correct_index": result["correct_index"],
            "correct_letter": result["correct_letter"],
            "raw_correct_value": val_raw
        }

class TrigReductionGenerator(MathTaskGenerator):
    def __init__(self):
        super().__init__()
        self.topic = "Trigonometry: Reduction Formulas"

    def generate(self):
        # Task: Simplify cos(pi - alpha) or sin(270 + alpha)
        
        bases = [
            ("\\pi", 180, "same"),
            ("2\\pi", 360, "same"),
            ("\\frac{\\pi}{2}", 90, "co"),
            ("\\frac{3\\pi}{2}", 270, "co")
        ]
        
        op = random.choice(["-", "+"])
        base_tex, base_deg, behavior = random.choice(bases)
        func = random.choice(["sin", "cos"])
        
        # Question: func(base op alpha)
        # Determine Quadrant
        # alpha is small acute angle
        
        quadrant = 1
        if base_deg == 90: quadrant = 2 if op=="+" else 1
        elif base_deg == 180: quadrant = 3 if op=="+" else 2
        elif base_deg == 270: quadrant = 4 if op=="+" else 3
        elif base_deg == 360: quadrant = 1 if op=="+" else 4
        
        # Original Sign
        orig_sign = 1
        if func == "sin":
            if quadrant in [3, 4]: orig_sign = -1
        else: # cos
            if quadrant in [2, 3]: orig_sign = -1
            
        # New Function
        new_func = func
        if behavior == "co":
            new_func = "cos" if func == "sin" else "sin"
            
        # Build Answer
        ans_sign = "-" if orig_sign == -1 else ""
        nf_tex = f"\\{new_func}"
        correct_ans = f"${ans_sign}{nf_tex} \\alpha$"
        
        question = f"Спростіть вираз $\\{func} ({base_tex} {op} \\alpha)$."
        
        distractors = set()
        
        # Distractor 1: SignFlip
        opp_sign = "" if ans_sign == "-" else "-"
        distractors.add(f"${opp_sign}{nf_tex} \\alpha$")
        
        # Distractor 2: Wrong Function (forgot reduction rule)
        wrong_f = "cos" if new_func=="sin" else "sin"
        wf_tex = f"\\{wrong_f}"
        distractors.add(f"${ans_sign}{wf_tex} \\alpha$")
        distractors.add(f"${opp_sign}{wf_tex} \\alpha$")
        
        # Distractor 3: Constant? rare but possible
        
        distractors.discard(correct_ans)
        result = self.get_random_options(correct_ans, list(distractors)[:4])
        
        return {
            "question": question,
            "options": result["options"],
            "correct_index": result["correct_index"],
            "correct_letter": result["correct_letter"],
            "raw_correct_value": 0
        }

class TrigEquationGenerator(MathTaskGenerator):
    def __init__(self):
        super().__init__()
        self.topic = "Trigonometry: Equations"

    def generate(self):
        # Task: Solve cos x = a
        # Smart Distractors: Wrong period (pi vs 2pi), wrong arc value
        
        # Case: cos x = 1/2
        equation_type = random.choice(["sin", "cos"])
        
        val_map = [
            (0, "0", "sin", "\\pi k", "cos", "\\frac{\\pi}{2} + \\pi k"),
            (1, "1", "sin", "\\frac{\\pi}{2} + 2\\pi k", "cos", "2\\pi k"),
            (-1, "-1", "sin", "-\\frac{\\pi}{2} + 2\\pi k", "cos", "\\pi + 2\\pi k"),
            (0.5, "\\frac{1}{2}", "sin", "(-1)^k \\frac{\\pi}{6} + \\pi k", "cos", "\\pm \\frac{\\pi}{3} + 2\\pi k"),
            (-0.5, "-\\frac{1}{2}", "sin", "(-1)^k (-\\frac{\\pi}{6}) + \\pi k", "cos", "\\pm \\frac{2\\pi}{3} + 2\\pi k") # Note: sin usually written with k+1? Or -pi/6
        ]
        
        # Let's stick to simple 0, 1, -1 for now to avoid extensive formula formatting logic
        # Or simple 1/2
        
        val_num, val_str, s_rule, s_ans, c_rule, c_ans = random.choice(val_map)
        
        correct_ans = s_ans if equation_type == "sin" else c_ans
        question = f"Розв'яжіть рівняння $\\{equation_type} x = {val_str}$."
        
        distractors = set()
        
        # Smart Distractor 1: Wrong Period
        # If correct has 2pi k, use pi k
        if "2\\pi k" in correct_ans:
            wrong_val = correct_ans.replace('2\\pi k', '\\pi k')
            distractors.add(f"${wrong_val}$")
        elif "\\pi k" in correct_ans: # e.g. for 0
             wrong_val = correct_ans.replace('\\pi k', '2\\pi k')
             distractors.add(f"${wrong_val}$")
             
        # Smart Distractor 2: Swap Sin/Cos formulas
        # e.g. for sin x = 1, giving cos answer form
        wrong_form = c_ans if equation_type == "sin" else s_ans
        distractors.add(f"${wrong_form}$")
        
        # Smart Distractor 3: Sign error in angle
        # e.g. -pi/2 instead of pi/2
        if "frac" in correct_ans:
            if "-" in correct_ans:
                distractors.add(f"${correct_ans.replace('-', '')}$")
            else:
                 # Insert minus before fraction
                 distractors.add(f"${'-' + correct_ans}$")
        
        distractors.add("$2\\pi k$")
        distractors.add("$\\frac{\\pi}{2} + \\pi k$")
        
        # Format correct as latex math
        correct_ans = f"${correct_ans}$"
        
        distractors.discard(correct_ans)
        result = self.get_random_options(correct_ans, list(distractors)[:4])
        
        return {
            "question": question,
            "options": result["options"],
            "correct_index": result["correct_index"],
            "correct_letter": result["correct_letter"],
            "raw_correct_value": 0
        }
