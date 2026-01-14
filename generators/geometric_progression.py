import random
from generators.base import MathTaskGenerator

class GeometricFindTermGenerator(MathTaskGenerator):
    def __init__(self):
        super().__init__()
        self.topic = "Geometric Progression: Find Term (b_1, b_2 -> b_n)"

    def generate(self):
        # Task: Given b_1, b_2, find b_n
        
        b1 = random.choice([2, 3, 4, 5, 10, 16, 32, 64, 81, 27])
        q = random.choice([2, 3, 4, 0.5, 0.25, -2, -0.5])
        
        # Ensure values don't explode too much.
        if abs(q) > 2:
            n = random.randint(3, 5)
        else:
            n = random.randint(4, 7)
            
        b2 = b1 * q
        
        # Target
        bn = b1 * (q ** (n - 1))
        
        def fmt(num):
             if isinstance(num, float) and num.is_integer():
                 return str(int(num))
             return str(round(num, 4)).replace('.', '{,}')
             
        question = f"У геометричній прогресії $(b_n)$ відомо, що $b_1 = {fmt(b1)}$, $b_2 = {fmt(b2)}$. Визначте $b_{{{n}}}$."
        correct_ans = fmt(bn)
        
        distractors = set()
        # 1. Arithmetic connection (d = b2 - b1)
        d = b2 - b1
        distractors.add(fmt(b1 + (n-1)*d))
        
        # 2. q error (inverse q?)
        if q != 0:
             distractors.add(fmt(b1 * ((1/q) ** (n - 1))))
             
        # 3. Off by one power
        distractors.add(fmt(b1 * (q ** n)))
        distractors.add(fmt(b1 * (q ** (n - 2))))
        
        # 4. Sign error
        distractors.add(fmt(-bn))
        
        # Fill randoms
        while len(distractors) < 4:
            val = bn + random.choice([-1, 1, -10, 10, -0.5, 0.5])
            distractors.add(fmt(val))

        distractors.discard(correct_ans)
        
        result = self.get_random_options(correct_ans, list(distractors)[:4])
        
        return {
            "question": question,
            "options": result["options"],
            "correct_index": result["correct_index"],
            "correct_letter": result["correct_letter"],
            "raw_correct_value": bn
        }

class GeometricRatioGenerator(MathTaskGenerator):
    def __init__(self):
        super().__init__()
        self.topic = "Geometric Progression: Term Ratio"

    def generate(self):
        # Task: Find b_5 / b_7
        
        k = random.randint(3, 8)
        delta = random.randint(1, 3)
        m = k + delta
        
        # Ratio b_k / b_m = b1*q^(k-1) / b1*q^(m-1) = 1 / q^delta
        
        q_options = [2, 3, 4, 0.5, 0.2, 5, 10]
        q = random.choice(q_options)
        
        # Just to make the problem look real, give b1 and b2
        b1 = random.choice([2, 4, 5, 10, 32])
        b2 = b1 * q
        
        ans_val = 1 / (q ** delta)
        
        def fmt(num):
             if isinstance(num, float) and num.is_integer():
                 return str(int(num))
             
             # Format fractions if possible? Or decimals.
             # If ans is 1/4 -> 0,25
             if abs(num - 0.5) < 0.001: return "0{,}5"
             if abs(num - 0.25) < 0.001: return "0{,}25"
             if abs(num - 0.125) < 0.001: return "0{,}125"
             
             return str(round(num, 4)).replace('.', '{,}')

        question = f"У геометричній прогресії $(b_n)$ відомо, що $b_1 = {fmt(b1)}$, $b_2 = {fmt(b2)}$. Обчисліть $\\dfrac{{b_{{{k}}}}}{{b_{{{m}}}}}$."
        
        correct_ans = fmt(ans_val)
        
        distractors = []
        # q^delta (reciprocal)
        distractors.append(fmt(q ** delta))
        
        # q
        distractors.append(fmt(q))
        
        # 1/q
        distractors.append(fmt(1/q))
        
        # Arithmetic difference
        distractors.append(fmt(b1 * q**(k-1) - b1 * q**(m-1)))

        result = self.get_random_options(correct_ans, distractors)
        return {
            "question": question,
            "options": result["options"],
            "correct_index": result["correct_index"],
            "correct_letter": result["correct_letter"],
            "raw_correct_value": ans_val
        }

class GeometricFormulaGenerator(MathTaskGenerator):
    def __init__(self):
        super().__init__()
        self.topic = "Geometric Progression: Formula"

    def generate(self):
        # Task: b_n = A * q^n. Find b_k.
        
        A = random.choice([1, 2, 3, 4, 5, 0.5, 0.8])
        base = random.choice([2, 3, 4])
        
        # Formula types:
        # 1. A * base^n
        # 2. A * base^(n-k)
        # 3. (-1)^n / n (Not strictly GP but sequence, found in DB)
        
        type = random.choice(['standard', 'offset', 'sequence'])
        
        k = random.randint(3, 6)
        
        def fmt(num):
             if isinstance(num, float) and num.is_integer():
                 return str(int(num))
             return str(round(num, 3)).replace('.', '{,}')

        if type == 'standard':
            # b_n = A * base^n + C*n (linear term distractor from DB?)
            # DB example: 0.8 * 2^n + 3n
            linear_coeff = random.choice([0, 1, 2, 3])
            
            formula = f"{fmt(A)} \\cdot {base}^n"
            if linear_coeff != 0:
                formula += f" + {linear_coeff}n"
                
            val = A * (base ** k) + linear_coeff * k
            question = f"Послідовність задано формулою $n$-го члена $b_n = {formula}$. Визначте {k}-й член цієї послідовності."
            
        elif type == 'offset':
            # 5 * 2^(n-3)
            offset = random.randint(1, 4)
            val = A * (base ** (k - offset))
            question = f"Геометричну прогресію задано формулою $n$-го члена $b_n = {fmt(A)} \\cdot {base}^{{n-{offset}}}$. Визначте {k}-й член цієї прогресії."
            
        else: # sequence (-1)^n * n etc
            # (-1)^n * n  or (-1)^n / n
            op = random.choice(['mult', 'div'])
            if op == 'mult':
                 val = ((-1)**k) * k
                 question = f"Послідовність задано формулою $n$-го члена $b_n = (-1)^n \\cdot n$. Визначте {k}-й член цієї послідовності."
            else:
                 val = ((-1)**k) / k
                 question = f"Послідовність задано формулою $n$-го члена $b_n = \\dfrac{{(-1)^n}}{{n}}$. Визначте {k}-й член цієї послідовності."

        correct_ans = fmt(val)
        distractors = set([fmt(val + 1), fmt(val - 1), fmt(-val), fmt(val * 2)])
        while len(distractors) < 4:
            distractors.add(fmt(val + random.randint(2, 10)))
        distractors.discard(correct_ans)
        
        result = self.get_random_options(correct_ans, list(distractors)[:4])
        return {
            "question": question,
            "options": result["options"],
            "correct_index": result["correct_index"],
            "correct_letter": result["correct_letter"],
            "raw_correct_value": val
        }

class GeometricSumGenerator(MathTaskGenerator):
    def __init__(self):
        super().__init__()
        self.topic = "Geometric Progression: Sum"

    def generate(self):
        # Task: S_4 given b_2 and q
        
        n = random.choice([3, 4, 5])
        q = random.choice([2, 3, -2, -3, 0.5])
        b2 = random.choice([4, 6, 8, 12, 18, -4, -6])
        b1 = b2 / q
        
        # S_n = b1 * (1 - q^n) / (1 - q)
        if q == 1: 
             total = b1 * n
        else:
             total = b1 * (1 - q**n) / (1 - q)
             
        def fmt(num):
             if isinstance(num, float) and num.is_integer():
                 return str(int(num))
             return str(round(num, 3)).replace('.', '{,}')
             
        question = f"Знайдіть суму {n} перших членів геометричної прогресії $(b_n)$, у якої $b_2 = {fmt(b2)}$, а знаменник $q = {fmt(q)}$."
        correct_ans = fmt(total)
        
        distractors = set() # Use set to avoid dupes automatically
        
        # Forget b1
        if q != 0: distractors.add(fmt(total / q))
        # Wrong sign
        distractors.add(fmt(-total))
        # Just b_n
        distractors.add(fmt(b1 * q**(n-1)))
        
        # Add randoms
        attempts = 0
        while len(distractors) < 4 and attempts < 20:
            attempts += 1
            val = total + random.randint(-50, 50)
            if val != total:
                distractors.add(fmt(val))
            
        # Ensure we don't have the correct answer in distractors
        distractors.discard(correct_ans)
            
        result = self.get_random_options(correct_ans, list(distractors)[:4])
        return {
            "question": question,
            "options": result["options"],
            "correct_index": result["correct_index"],
            "correct_letter": result["correct_letter"],
            "raw_correct_value": total
        }

class GeometricWordProblemGenerator(MathTaskGenerator):
    def __init__(self):
        super().__init__()
        self.topic = "Geometric Progression: Word Problem"

    def generate(self):
        # Scenario: Virus/Views/Bacteria growth.
        # "Day 1 = A. Each day doubles. When > Limit?"
        
        start_val = random.choice([10, 50, 100, 5])
        multiplier = 2
        
        limit = random.choice([1000, 2000, 5000, 500])
        if limit < start_val * 4: limit = start_val * 8
        
        # Find n such that start * 2^(n-1) > limit? 
        # Usually "Day 1", so on Day k, val = start * 2^(k-1).
        # OR "Next day increases BY 2 times" -> geometric.
        # "Total views sum > limit" OR "Views on day k > limit"?
        # DB example says "SUMMARNE chislo pereglyadiv" -> Sum > Limit.
        
        type = "sum"
        
        current_sum = 0
        current_val = start_val
        days = 0
        
        while current_sum <= limit:
            days += 1
            current_sum += current_val
            current_val *= multiplier
            
        target_days = days
        
        scenarios = [
            ("Марійка викладала відео", "відео набрало", "переглядів"),
            ("Бактерія ділиться", "колонія налічувала", "бактерій"),
            ("Інвестор вклав гроші", "прибуток склав", "доларів")
        ]
        sc = random.choice(scenarios)
        
        question = f"{sc[0]}. Першого дня {sc[1]} {start_val} {sc[2]}. Кожного наступного дня кількість збільшувалася вдвічі. За яку \\textit{{найменшу}} кількість днів сумарна кількість {sc[2]} перевищить {limit}?"
        
        correct_ans = str(target_days)
        distractors = [str(target_days - 1), str(target_days + 1), str(target_days + 2), str(target_days - 2)]
        
        result = self.get_random_options(correct_ans, distractors)
        return {
            "question": question,
            "options": result["options"],
            "correct_index": result["correct_index"],
            "correct_letter": result["correct_letter"],
            "raw_correct_value": target_days
        }

if __name__ == "__main__":
    gens = [
        GeometricFindTermGenerator(),
        GeometricRatioGenerator(),
        GeometricFormulaGenerator(),
        GeometricSumGenerator(),
        GeometricWordProblemGenerator()
    ]
    for gen in gens:
        print(f"--- {gen.topic} ---")
        task = gen.generate()
        print("Question:", task["question"])
        print("Correct:", task["correct_letter"], f"({task['raw_correct_value']})")
        print("Options:", task["options"])
        print()
