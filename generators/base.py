from abc import ABC, abstractmethod
import random
import json

class MathTaskGenerator(ABC):
    def __init__(self):
        self.topic = "Unknown"
        self.task_type = "multiple_choice"

    @abstractmethod
    def generate(self):
        """
        Generates a new task instance.
        Returns a dictionary with:
        - question (str): LaTeX question
        - correct_answer (str): LaTeX correct answer
        - distractors (list): List of wrong LaTeX answers
        - explanation (str): Optional explanation
        """
        pass

    def get_random_options(self, correct, distractors, num_options=5):
        """
        Helper to shuffle correct + distractors into a final list.
        Returns (options_list, correct_index).
        Guarantees num_options items by filling with random numbers if needed (last resort) or duplicating.
        """
        options = [correct] + distractors
        # Dedupe strictly strings
        options = list(set(options))
        
        # Ensure correct is present
        if correct not in options:
            options.append(correct)
            
        # Fill if too few
        attempts = 0
        while len(options) < num_options:
            # Last resort filler
            try:
                # Try to guess type from correct answer
                if "," in correct or "." in correct:
                    val = float(correct.replace(",", "."))
                    new_val = val + random.choice([-1, 1, 0.5, -0.5, 2, -2])
                    options.append(str(round(new_val, 2)).replace(".", ","))
                else:
                     val = int(correct)
                     new_val = val + random.randint(-10, 10)
                     options.append(str(new_val))
            except:
                 # Just random string
                 options.append(str(random.randint(1, 100)))
            
            # Dedupe again
            options = list(set(options))
            attempts += 1
            if attempts > 20: 
                # If we really can't find unique distractors, just duplicate
                options.append(options[0]) 

        # If we have too many, cut it
        if len(options) > num_options:
            # Ensure we keep correct answer
            options.remove(correct)
            random.shuffle(options)
            options = options[:num_options-1]
            options.append(correct)

        random.shuffle(options)
        correct_index = options.index(correct)
        
        # Map to A, B, C, D, E...
        labels = ["А", "Б", "В", "Г", "Д"]
        return {
            "options": options,
            "correct_index": correct_index,
            "correct_letter": labels[correct_index] if correct_index < len(labels) else "?"
        }
