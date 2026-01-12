import os
import re
import json
import glob

# Configuration
SOURCE_DIR = "overleaf-lessons/extracted"
OUTPUT_FILE = "nmt_database.json"

def parse_latex_file(filepath, topic_name):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    tasks = []
    
    # Split content by \task command
    # Pattern: \task{number}{text} ... content ...
    # We will use a regex to find all task starts, then slice the content
    
    # Regex to find definition of tasks
    # We use a custom parser because regex doesn't handle nested braces well
    task_start_pattern = re.compile(r'(?:\\task\s*\{(\d+)\}\s*\{)|(?:\\noindent\\makebox\[[^\]]*\]\[[^\]]*\]\{\\textbf\{(\d+)\.\}\}\\parbox\[[^\]]*\](?:\{[^}]*\})?\{)')
    
    current_pos = 0
    while True:
        match = task_start_pattern.search(content, current_pos)
        if not match:
            break
            
        if match.group(1):
            task_num = match.group(1)
        else:
            task_num = match.group(2)
            
        start_content_idx = match.end()
        
        # Extract the question text by balancing braces
        brace_count = 1
        i = start_content_idx
        task_text_end = -1
        
        while i < len(content):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
            
            if brace_count == 0:
                task_text_end = i
                break
            i += 1
            
        if task_text_end == -1:
            print(f"Error: Could not find closing brace for task {task_num}")
            current_pos = start_content_idx
            continue
            
        task_text = content[start_content_idx:task_text_end]
        
        # Now find the "body" (everything after the question curly brace until the next task or newpage)
        body_start = task_text_end + 1
        
        # Find next task to determine body end (or end of file)
        next_task_match = task_start_pattern.search(content, body_start)
        
        # Also check for \newpage or end of document
        # But simplistic approach: look for next \task
        if next_task_match:
            body_end = next_task_match.start()
        else:
            # Check for \newpage or \end{document}
            # Actually, simply taking everything till end of file or next task is fine
            # But we might want to stop at \newpage
            # Let's take 'till next task' as safest approximate, or look for specific section breaks
            body_end = len(content)
            
        task_body = content[body_start:body_end]
        
        full_task_content = task_text + task_body
        
        # Extract Year from text OR body
        year_match = re.search(r'\\nmtyear\s*\{(\d+)\}', full_task_content)
        year = year_match.group(1) if year_match else "Unknown"
        
        # Clean up text
        cleaned_text = clean_latex_text(task_text)
        
        # Extract Options
        options = []
        answer_table_match = re.search(r'\\answerTable(?:Small|Tall|Big)?\s*\{(.*?)\}\s*\{(.*?)\}\s*\{(.*?)\}\s*\{(.*?)\}\s*\{(.*?)\}', task_body, re.DOTALL)
        
        task_type = "unknown"
        
        if answer_table_match:
            task_type = "multiple_choice"
            options = [
                clean_latex_text(answer_table_match.group(1)),
                clean_latex_text(answer_table_match.group(2)),
                clean_latex_text(answer_table_match.group(3)),
                clean_latex_text(answer_table_match.group(4)),
                clean_latex_text(answer_table_match.group(5))
            ]
        elif "\\matchTable" in task_body:
            task_type = "matching"
            # TODO: matching extraction is complex, saving raw for now
            
        # Extract Images
        images = []
        img_matches = re.finditer(r'\\includegraphics(?:\[.*?\])?\s*\{(.*?)\}', full_task_content)
        for img in img_matches:
            images.append(img.group(1))
            
        # Check for TikZ
        has_tikz = "\\begin{tikzpicture}" in full_task_content

        task_id = f"{topic_name.replace(' ', '_')}_task_{task_num}_{year}"

        tasks.append({
            "id": task_id,
            "topic": topic_name,
            "task_number": task_num,
            "year": year,
            "type": task_type,
            "question": cleaned_text,
            "options": options,
            "images": images,
            "has_tikz": has_tikz,
            "raw_latex": full_task_content.strip() 
        })
        
        # Move regex search to next task
        if next_task_match:
            current_pos = next_task_match.start()
        else:
            break
            
    return tasks

def clean_latex_text(text):
    # Remove \nmtyear{...}
    text = re.sub(r'\\nmtyear\s*\{\d+\}', '', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def main():
    all_tasks = []
    
    # Find all top-level directories (Topics)
    search_path = os.path.join(SOURCE_DIR, "*")
    topic_dirs = glob.glob(search_path)
    
    print(f"Found {len(topic_dirs)} topic directories.")
    
    for topic_dir in topic_dirs:
        if not os.path.isdir(topic_dir):
            continue
            
        topic_name = os.path.basename(topic_dir)
        print(f"Processing topic: {topic_name}")
        
        # Find tex files in the directory
        tex_files = glob.glob(os.path.join(topic_dir, "*.tex"))
        
        for tex_file in tex_files:
            print(f"  Parsing {os.path.basename(tex_file)}...")
            try:
                tasks = parse_latex_file(tex_file, topic_name)
                all_tasks.extend(tasks)
                print(f"    Found {len(tasks)} tasks.")
            except Exception as e:
                print(f"    Error parsing {tex_file}: {e}")

    print(f"Total tasks pased: {len(all_tasks)}")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_tasks, f, ensure_ascii=False, indent=2)
        
    print(f"Database saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
