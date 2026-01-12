import random
from generators.base import MathTaskGenerator

class MatchingTaskGenerator(MathTaskGenerator):
    """
    Adapter that runs a sub-generator 3 times to create a matching task (3 questions -> 5 options).
    """
    def __init__(self, sub_generator_class, topic_name=None):
        super().__init__()
        self.sub_gen = sub_generator_class()
        self.topic = topic_name if topic_name else f"Matching: {self.sub_gen.topic}"

    def generate(self):
        # 1. Generate 3 distinct sub-tasks
        tasks = []
        attempts = 0
        while len(tasks) < 3 and attempts < 10:
            t = self.sub_gen.generate()
            # Simple dedup strategy: check raw values
            if not any(x["raw_correct_value"] == t["raw_correct_value"] for x in tasks):
                tasks.append(t)
            attempts += 1
            
        # If we failed to get 3 unique, just duplicate (fallback)
        while len(tasks) < 3:
            tasks.append(self.sub_gen.generate())

        # 2. Collect Questions and Correct Answers
        questions = [t["question"] for t in tasks]
        correct_vals = [t["raw_correct_value"] for t in tasks] # raw values (numbers/strings)
        correct_strs = [t["correct_letter"] for t in tasks] # Wait, standard generator returns letter from its own 5 options. 
        # We need the ACTUAL correct answer string (the value).
        
        # We need to extract the CORRECT option string from the sub-task.
        # The sub-task result has 'options' (list of 5) and 'correct_index'.
        real_answers = [t["options"][t["correct_index"]] for t in tasks]
        
        # 3. Create Pool of Options (3 Correct + 2 Distractors)
        # We need 2 extra distractors that are NOT equal to any correct answer.
        # We can pick distractors from the sub-tasks themselves!
        candidate_distractors = set()
        for t in tasks:
            for opt in t["options"]:
                if opt not in real_answers:
                    candidate_distractors.add(opt)
                    
        # If not enough, generate more using sub-gen
        while len(candidate_distractors) < 2:
            extra = self.sub_gen.generate()
            for opt in extra["options"]:
                if opt not in real_answers:
                    candidate_distractors.add(opt)
                    
        # Select 2 distractors
        final_distractors = list(candidate_distractors)
        random.shuffle(final_distractors)
        final_distractors = final_distractors[:2]
        
        # 4. Final Options List (5 items)
        all_options = real_answers + final_distractors
        random.shuffle(all_options)
        
        # 5. Determine new mapping
        # We need to know which letter (A-D) corresponds to Question 1, 2, 3
        # mapping: index 0 (Q1) -> Letter X
        
        mapping = {}
        for i, ans in enumerate(real_answers):
            # Find index in all_options
            idx = all_options.index(ans)
            letter = ["А", "Б", "В", "Г", "Д"][idx]
            mapping[i+1] = letter
            
        return {
            "type": "matching",
            "questions": questions,
            "options": all_options,
            "mapping": mapping, # {1: 'A', 2: 'B', 3: 'D'}
            "raw_values": correct_vals
        }
