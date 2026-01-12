import random
from generators.base import MathTaskGenerator

class ArithmeticFindDifferentGenerator(MathTaskGenerator):
    def __init__(self):
        super().__init__()
        self.topic = "Arithmetic Progression: Find d"

    def generate(self):
        # Task: "В арифметичній прогресії (a_n): a_1 = 4, a_3 = 9. Визначте різницю d прогресії."
        
        a1 = random.randint(-10, 20)
        # d should be divisible by 2 if we want integers, or 0.5 step
        d = random.choice([
            random.randint(-10, 10),
            0.5 * random.randint(-20, 20)
        ])
        if d == 0: d = 2
        
        a3 = a1 + 2 * d
        
        def fmt(num):
             if isinstance(num, float) and num.is_integer():
                 return str(int(num))
             return str(num).replace('.', '{,}')
             
        question = f"В арифметичній прогресії $(a_n)$: $a_1 = {fmt(a1)}$, $a_3 = {fmt(a3)}$. Визначте різницю $d$ прогресії."
        correct_ans = f"$d = {fmt(d)}$"
        
        # Distractors
        distractors = []
        distractors.append(f"$d = {fmt(a3 - a1)}$") # Forgot /2
        distractors.append(f"$d = {fmt((a3 + a1) / 2)}$") # Mean
        distractors.append(f"$d = {fmt(-d)}$") # Sign error
        distractors.append(f"$d = {fmt(d + 1)}$") # Random
        
        result = self.get_random_options(correct_ans, distractors)
        return {
            "question": question,
            "options": result["options"],
            "correct_index": result["correct_index"],
            "correct_letter": result["correct_letter"],
            "raw_correct_value": d
        }

class ArithmeticMemberDifferenceGenerator(MathTaskGenerator):
    def __init__(self):
        super().__init__()
        self.topic = "Arithmetic Progression: Member Difference"

    def generate(self):
        # Task: "В арифметичній прогресії (a_n) відомо, що a_6 - a_1 = -30. Знайдіть значення виразу a_6 - a_4."
        # Logic: a_n - a_k = (n-k)d = Known_Delta
        # Find: a_p - a_q = (p-q)d
        
        # 1. Choose d (integer usually)
        d = random.choice([x for x in range(-10, 11) if x != 0])
        
        # 2. Choose indices for the "Given" part
        # n > k to keep it simple, or whatever
        k = random.randint(1, 5)
        n = k + random.randint(2, 6) # difference of 2 to 6 steps
        
        given_delta_val = (n - k) * d
        
        # 3. Choose indices for the "Find" part
        # p, q. 
        q = random.randint(1, n+2)
        p = q + random.randint(1, 4)
        if random.random() < 0.5:
             p, q = q, p # Swap to allow negative differences
             
        target_delta_val = (p - q) * d
        
        question = f"В арифметичній прогресії $(a_n)$ відомо, що $a_{{{n}}} - a_{{{k}}} = {given_delta_val}$. Знайдіть значення виразу $a_{{{p}}} - a_{{{q}}}$."
        
        correct_ans = str(target_delta_val)
        
        # Distractors
        distractors = set()
        
        # Error: confuse d with delta? No, usually calculation errors.
        # 1. Sign error
        distractors.add(str(-target_delta_val))
        
        # 2. Wrong multiplier (off by one d)
        distractors.add(str(target_delta_val + d))
        distractors.add(str(target_delta_val - d))
        
        # 3. Wrong scaling (using the given_delta directly?)
        distractors.add(str(given_delta_val))
        
        # 4. Proportional error? (p-q)/(n-k) reversed?
        # Let's just add random nearby integers if we need more
        while len(distractors) < 4:
            distractors.add(str(target_delta_val + random.randint(-5, 5)))
            distractors.discard(correct_ans) # Ensure we didn't add the correct answer
            
        result = self.get_random_options(correct_ans, list(distractors)[:4])
        
        return {
            "question": question,
            "options": result["options"],
            "correct_index": result["correct_index"],
            "correct_letter": result["correct_letter"],
            "raw_correct_value": target_delta_val
        }

class ArithmeticSumGenerator(MathTaskGenerator):
    def __init__(self):
        super().__init__()
        self.topic = "Arithmetic Progression: Sum"

    def generate(self):
        # Task: "Обчисліть суму перших десяти членів арифметичної прогресії (a_n), якщо a_1 + a_{10} = -12."
        # Logic: S_n = (a_1 + a_n) / 2 * n
        
        n = random.choice([10, 20, 16, 8, 12, 100])
        
        # Sum of first and last 
        # For integer result, (a1 + an) * n must be divisible by 2.
        # If n is even, any integer sum works.
        # If n is odd, sum must be even.
        
        first_plus_last = random.randint(-50, 50)
        
        # Ensure integer answer
        if n % 2 != 0 and first_plus_last % 2 != 0:
            first_plus_last += 1
            
        S_n = (first_plus_last * n) // 2
        
        question = f"Обчисліть суму перших {n}-ти членів арифметичної прогресії $(a_n)$, якщо $a_1 + a_{{{n}}} = {first_plus_last}$."
        correct_ans = str(S_n)
        
        # Distractors
        distractors = []
        
        # 1. Forgot / 2 => S = sum * n
        distractors.append(str(first_plus_last * n))
        
        # 2. Multiplied by n/2 but forgot sum? No.
        # 2. Calculation error (off by n?)
        distractors.append(str(S_n + n))
        distractors.append(str(S_n - n))
        
        # 3. Arithmetic error (wrong sign)
        distractors.append(str(-S_n))
        
        # 4. Just the sum value
        distractors.append(str(first_plus_last))
        
        result = self.get_random_options(correct_ans, distractors)
         
        return {
            "question": question,
            "options": result["options"],
            "correct_index": result["correct_index"],
            "correct_letter": result["correct_letter"],
            "raw_correct_value": S_n
        }

class ArithmeticTermPropertiesGenerator(MathTaskGenerator):
    def __init__(self):
        super().__init__()
        self.topic = "Arithmetic Progression: Count Terms"

    def generate(self):
        # Task: "В арифметичній прогресії (a_n) перший член a_1 = 18.5, різниця d = -2.5. Скільки всього додатних членів має ця прогресія?"
        # Logic: Find n such that a_n > 0 (or a_n < 0).
        # a_n = a_1 + (n-1)d > 0
        
        # Scenario 1: Decreasing seq, count positive terms.
        # Scenario 2: Increasing seq, count negative terms.
        
        scenario = random.choice(['positive', 'negative'])
        
        if scenario == 'positive':
            # Need a1 > 0, d < 0
            n_terms = random.randint(5, 15)
            d = -1 * random.choice([0.5, 1.5, 2.5, 0.4, 0.8, 1, 2, 3])
            
            # Make sure the (n_terms)-th term is positive, and (n_terms+1)-th is <= 0
            # a_n = a_1 + (n-1)d
            # We want specific count. Let's work backwards.
            # a_{n} = epsilon > 0
            # a_{n+1} = a_n + d <= 0
            
            last_pos_val = random.choice([0.1, 0.5, 1, 2, 0.2, 0.3])
            a1 = last_pos_val - (n_terms - 1) * d
            
            question_type = "додатних"
            target_count = n_terms
            
        else: # negative
            # Need a1 < 0, d > 0
            n_terms = random.randint(5, 15)
            d = random.choice([0.5, 1.5, 2.5, 0.4, 0.8, 1, 2, 3])
            
            last_neg_val = -1 * random.choice([0.1, 0.5, 1, 2, 0.2, 0.3])
            a1 = last_neg_val - (n_terms - 1) * d
            
            question_type = "від'ємних"
            target_count = n_terms

        def fmt(num):
             if isinstance(num, float) and num.is_integer():
                 return str(int(num))
             return str(round(num, 2)).replace('.', '{,}')

        question = f"В арифметичній прогресії $(a_n)$ перший член $a_1 = {fmt(a1)}$, різниця $d = {fmt(d)}$. Скільки всього \\textit{{{question_type}}} членів має ця прогресія?"
        
        correct_ans = str(target_delta_val) if 'target_delta_val' in locals() else str(target_count) # logic fix
        correct_ans = str(target_count) 

        # Distractors
        distractors = []
        distractors.append(str(target_count + 1))
        distractors.append(str(target_count - 1))
        distractors.append(str(target_count + 2))
        distractors.append(str(target_count - 2))
        
        result = self.get_random_options(correct_ans, distractors)
        
        return {
            "question": question,
            "options": result["options"],
            "correct_index": result["correct_index"],
            "correct_letter": result["correct_letter"],
            "raw_correct_value": target_count
        }

class ArithmeticMiddleTermGenerator(MathTaskGenerator):
    def __init__(self):
        super().__init__()
        self.topic = "Arithmetic Progression: Middle Term"

    def generate(self):
        # Task: "Визначте восьмий член a_8 арифметичної прогресії (a_n), у якої a_7 = 11, a_9 = 18."
        # Logic: a_n = (a_{n-1} + a_{n+1}) / 2
        
        n = random.randint(3, 20)
        a_prev = random.randint(-20, 50)
        
        # We need a_next such that (a_prev + a_next) is divisible by 2 for integer result.
        # So a_prev and a_next must have same parity.
        delta = random.choice([2, 4, 6, 8, -2, -4, -6, 10, 12]) # even difference implies same parity
        # Or just start with d
        d = random.choice([0.5, 1.5, 2.5, 1, 2, 3, 4, 5, -1, -2, -3])
        
        a_prev_val = a_prev
        a_next_val = a_prev + 2*d
        a_target_val = a_prev + d
        
        def fmt(num):
             if isinstance(num, float) and num.is_integer():
                 return str(int(num))
             return str(round(num, 2)).replace('.', '{,}')

        question = f"Визначте {n}-й член $a_{{{n}}}$ арифметичної прогресії $(a_n)$, у якої $a_{{{n-1}}} = {fmt(a_prev_val)}$, $a_{{{n+1}}} = {fmt(a_next_val)}$."
        correct_ans = fmt(a_target_val)
        
        distractors = []
        # 1. Sum instead of mean
        distractors.append(fmt(a_prev_val + a_next_val))
        # 2. Difference
        distractors.append(fmt(abs(a_next_val - a_prev_val)))
        # 3. Just one of the neighbors
        distractors.append(fmt(a_prev_val))
        distractors.append(fmt(a_next_val))
        # 4. d
        distractors.append(fmt(d))
        
        result = self.get_random_options(correct_ans, distractors)
        
        return {
            "question": question,
            "options": result["options"],
            "correct_index": result["correct_index"],
            "correct_letter": result["correct_letter"],
            "raw_correct_value": a_target_val
        }

class ArithmeticFormulaSearchGenerator(MathTaskGenerator):
    def __init__(self):
        super().__init__()
        self.topic = "Arithmetic Progression: Formula Search"

    def generate(self):
        # Task: "Арифметичну прогресію (a_n) задано формулою n-го члена a_n = 18 - 1.5n. Визначте номер члена, значення якого дорівнює -30."
        # Logic: val = const + coeff * n  => n = (val - const) / coeff
        
        n_target = random.randint(5, 50)
        coeff = random.choice([-1.5, -2.5, -0.5, 1.5, 2.5, 3, 4, -3, -4])
        const = random.randint(10, 50)
        
        val = const + coeff * n_target
        
        def fmt(num):
             if isinstance(num, float) and num.is_integer():
                 return str(int(num))
             return str(round(num, 2)).replace('.', '{,}')
             
        # Format formula: 18 - 1.5n or 18 + 1.5n
        sign = "+" if coeff > 0 else ""
        formula = f"{const} {sign} {fmt(coeff)}n".replace(" + -", " - ")
        
        question = f"Арифметичну прогресію $(a_n)$ задано формулою $n$-го члена $a_n = {formula}$. Визначте номер члена, значення якого дорівнює ${fmt(val)}$."
        correct_ans = str(n_target)
        
        distractors = []
        # 1. Off by one error
        distractors.append(str(n_target + 1))
        distractors.append(str(n_target - 1))
        # 2. Calculation error (e.g. forgot const)
        # val = coeff * n => n = val / coeff
        try:
            wrong_n = val / coeff
            if wrong_n > 0 and wrong_n != n_target:
                distractors.append(fmt(wrong_n))
        except: pass
        
        # 3. Random reasonable numbers
        distractors.append(str(n_target + 10))
        distractors.append(str(max(1, n_target - 10)))
        
        result = self.get_random_options(correct_ans, distractors)
        
        return {
            "question": question,
            "options": result["options"],
            "correct_index": result["correct_index"],
            "correct_letter": result["correct_letter"],
            "raw_correct_value": n_target
        }

class ArithmeticWordProblemGenerator(MathTaskGenerator):
    def __init__(self):
        super().__init__()
        self.topic = "Arithmetic Progression: Word Problem"

    def generate(self):
        scenario = random.choice(['auditorium', 'stack', 'loan', 'training'])
        
        if scenario == 'auditorium':
            # Task: Row 1 has a1 seats. Last row (n) has an seats. Find mid row or total.
            
            n_rows = random.randint(10, 30)
            d = random.randint(1, 4)
            a1 = random.randint(15, 60)
            an = a1 + (n_rows - 1) * d
            
            target_row = random.randint(2, n_rows - 1)
            target_val = a1 + (target_row - 1) * d
            
            question = f"У залі для глядачів цирку встановлено {n_rows} рядів крісел: у першому ряду {a1} крісла, а в кожному наступному ряду кількість крісел на те саме число більше, ніж у попередньому. Визначте кількість крісел у \\textit{{{target_row}-му}} ряду, якщо в останньому ряду {an} крісла."
            correct_ans = str(target_val)
            distractors = [str(target_val + d), str(target_val - d), str(target_val + 2*d), str(target_val - 2*d)]
            
        elif scenario == 'stack':
            # Task: Bottom row a1, top row an. Total count?
            # Usually simple: top row 1, increases by 1.
            
            top_row = 1
            rows = random.randint(10, 20)
            bottom_row = top_row + (rows - 1)
            # Sum = (top + bottom) * rows / 2
            total = (top_row + bottom_row) * rows // 2
            
            question = f"На рисунку зображено (уявно) поперечний переріз стосу дерев'яних колод. У нижньому ряду стосу {bottom_row} колод, а у верхньому — {top_row}. Визначте загальну кількість колод у цьому стосі, якщо кожен наступний ряд містить на одну колоду менше, ніж попередній."
            correct_ans = str(total)
            distractors = [str(total + 10), str(total - 10), str(total + rows), str(total - rows)]

        elif scenario == 'loan':
            # Task: Pay loan in n months. Month 1 = a1. Each month -d. Total sum?
            
            months = random.choice([12, 24, 6, 10])
            d = random.choice([10, 50, 20, 100])
            # Last payment should be > 0.
            # a_n = a1 - (n-1)d > 0 => a1 > (n-1)d
            min_a1 = (months) * d 
            a1 = min_a1 + random.randint(1, 10) * 100
            
            an = a1 - (months - 1) * d
            
            total = (a1 + an) * months // 2
            
            question = f"За умовами договору позичальник повинен повернути кредит протягом {months} місяців. Першого місяця він має повернути {a1} \\textit{{грн}}, а кожного наступного місяця — на {d} \\textit{{грн}} менше, ніж попереднього. Визначте загальну суму (у \\textit{{грн}}), яку повинен позичальник повернути протягом {months} місяців."
            correct_ans = str(total)
            distractors = [str(total + 1000), str(total - 500), str(a1 * months), str((a1 + d)*months)]
            
        else: # training
            # Task: Day 1 = a1 words. Each day +d. Total in n days?
            
            days = random.randint(10, 30)
            a1 = random.randint(5, 20)
            d = random.randint(1, 5)
            
            an = a1 + (days - 1) * d
            total = (a1 + an) * days // 2
            
            question = f"Студент вивчав мову за методикою: у перший день він запам'ятав {a1} слів, а кожного наступного дня — на {d} слів більше, ніж попереднього. Скільки всього слів запам'ятав студент за {days} днів?"
            correct_ans = str(total)
            distractors = [str(total + 20), str(total - 20), str(an * days), str(a1 * days)]

        result = self.get_random_options(correct_ans, distractors)
        
        return {
            "question": question,
            "options": result["options"],
            "correct_index": result["correct_index"],
            "correct_letter": result["correct_letter"],
            "raw_correct_value": int(correct_ans)
        }

if __name__ == "__main__":
    gens = [
        ArithmeticFindDifferentGenerator(), 
        ArithmeticMemberDifferenceGenerator(),
        ArithmeticSumGenerator(),
        ArithmeticTermPropertiesGenerator(),
        ArithmeticMiddleTermGenerator(),
        ArithmeticFormulaSearchGenerator(),
        ArithmeticWordProblemGenerator()
    ]
    for gen in gens:
        # ... existing main loop ...
        # ... existing main loop ...
        # ... existing main loop ...
        print(f"--- {gen.topic} ---")
        task = gen.generate()
        print("Question:", task["question"])
        print("Correct:", task["correct_letter"], f"({task['raw_correct_value']})")
        print("Options:", task["options"])
        print()
