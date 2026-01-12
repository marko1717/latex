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
        Returns (options_list, correct_index)
        """
        options = [correct] + distractors
        # Ensure unique options
        options = list(set(options))
        
        # If we have too many, cut it
        if len(options) > num_options:
            options = options[:num_options]
            # Ensure correct is still there (it might have been cut if shuffle happened before, but here we just slice)
            # Actually, set is unordered, so let's be careful.
            if correct not in options:
                options[0] = correct
                
        # If we have too few, we can't really help unless we generate more. 
        # Assuming the caller provides enough distractors.

        random.shuffle(options)
        correct_index = options.index(correct)
        
        # Map to A, B, C, D, E...
        labels = ["А", "Б", "В", "Г", "Д"]
        return {
            "options": options,
            "correct_index": correct_index,
            "correct_letter": labels[correct_index] if correct_index < len(labels) else "?"
        }
