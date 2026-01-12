import json
from collections import defaultdict, Counter

def analyze_structure():
    try:
        with open('nmt_database.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("nmt_database.json not found.")
        return

    # Structure: topic -> type -> count
    stats = defaultdict(Counter)

    for item in data:
        # topics is a list, usually has 1 main topic or multiple
        # let's grab the first one for now, or all
        topics = item.get('topics', [])
        if not topics:
            topics = ["Unknown"]
        
        # Determine type
        # "choices" usually implies single choice (if 4 or 5 options)
        # "matching" implies correspondence
        # "short_answer" implies numerical
        
        t_type = "short_answer"
        if item.get('choices'):
            t_type = "single_choice"
        # How do we identify matching in the json? 
        # Usually checking if 'question' text has specific keywords or struct
        # OR if the item has specific metadata.
        # Let's inspect the keys of one item to be sure.
        
        # But wait, the parser might not have flagged matching correctly yet?
        # Let's check for 'A', 'B', 'C', 'D' keys in choices usually.
        
        # Heuristic for Matching:
        # If the task text contains "Установіть відповідність"
        if "відповідність" in item.get('question', '').lower():
            t_type = "matching"
            
        for topic in topics:
            stats[topic][t_type] += 1

    print(f"{'TOPIC':<40} | {'TYPE':<15} | {'COUNT'}")
    print("-" * 70)
    
    for topic, counts in sorted(stats.items()):
        total = sum(counts.values())
        print(f"{topic:<40} | {'[TOTAL]':<15} | {total}")
        for t_type, count in counts.items():
            print(f"{'':<40} | {t_type:<15} | {count}")
        print("-" * 70)

if __name__ == "__main__":
    analyze_structure()
