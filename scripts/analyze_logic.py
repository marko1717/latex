import json
import re
import math
from collections import Counter

DB_FILE = "nmt_database.json"

def load_data():
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def safe_float(s):
    try:
        # Handle decimal comma
        s = s.replace(",", ".").replace("{", "").replace("}", "").replace("$", "")
        return float(s)
    except:
        return None

def analyze_task(task):
    if task["type"] != "multiple_choice":
        return None

    options = task.get("options", [])
    if not options or len(options) < 2:
        return None
        
    # We don't know the correct answer index from the parsed data explicitly 
    # unless we solve it or parsing marked it (parsing usually extracts correct letter if available).
    # In nmt_database.json, do we have 'correct_option'?
    # Checking view of latex_parser.py or json might reveal this.
    # Assuming for now we treat ALL options as a set and look for relations.
    # OR, we assume we might need to manually tag some to learn.
    
    # Let's just look for internal consistency in options.
    # e.g. is there x, -x? x, 1/x? x, x+1?
    
    nums = []
    for opt in options:
        val = safe_float(opt)
        if val is not None:
            nums.append(val)
            
    if len(nums) < 2:
        return None
        
    relations = []
    nums = sorted(nums)
    
    # Check for relations between any pair
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            a = nums[i]
            b = nums[j]
            
            if abs(a - b) < 1e-9: continue
            
            # Relation: Additive
            diff = round(b - a, 4)
            if diff in [1, 2, 10, 0.5]:
                relations.append(f"+{diff}")
            
            # Relation: Sign
            if abs(a + b) < 1e-9:
                relations.append("SignFlip")
                
            # Relation: Multiplicative (Inverse)
            if abs(a * b - 1) < 1e-9:
                relations.append("Inverse")
            
            # Relation: Power
            if a > 0 and b > 0:
                if abs(a**2 - b) < 1e-5: relations.append("Square")
                if abs(math.sqrt(a) - b) < 1e-5: relations.append("Sqrt")

    return relations

def main():
    data = load_data()
    print(f"Loaded {len(data)} tasks.")
    
    all_relations = []
    
    topic_distractors = {}
    
    for task in data:
        topic = task.get("topic", "Unknown")
        rels = analyze_task(task)
        if rels:
            all_relations.extend(rels)
            if topic not in topic_distractors:
                topic_distractors[topic] = []
            topic_distractors[topic].extend(rels)
            
    # Stats
    print("\n--- Common Distractor Patterns (Global) ---")
    print(Counter(all_relations).most_common(10))
    
    print("\n--- Patterns by Topic ---")
    for topic, rels in topic_distractors.items():
        if len(rels) > 5:
            print(f"\n{topic}:")
            print(Counter(rels).most_common(5))

if __name__ == "__main__":
    main()
