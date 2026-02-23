import os
import sys
import json
import urllib.request
import datetime

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    import re

def simple_yaml_load(text):
    # Basic list of dicts parser for - name: / description: / files:
    items = []
    current_item = {}
    for line in text.split('\n'):
        line = line.strip()
        if not line: continue
        if line.startswith('- '):
            if current_item: items.append(current_item)
            current_item = {}
            line = line[2:]
        if ':' in line:
            parts = line.split(':', 1)
            key = parts[0].strip()
            val = parts[1].strip() if len(parts) > 1 else ""
            if key == 'files':
                match = re.search(r'\[(.*?)\]', val)
                if match: 
                    val = [s.strip().strip("'").strip('"') for s in match.group(1).split(',')]
            current_item[key] = val
    if current_item: items.append(current_item)
    return items

def extract_yaml(text):
    if "```yaml" in text:
        return text.split("```yaml")[1].split("```")[0].strip()
    elif "```" in text:
        return text.split("```")[1].split("```")[0].strip()
    return text.strip()

def call_gemini(prompt, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        'contents': [{'parts': [{'text': prompt}]}]
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"❌ Error calling Gemini API: {e}")
        return None

def run_academy(target_path, vault_dir, api_key):
    project_name = os.path.basename(target_path)
    print(f"🎓 Starting Git-Library Academy for {project_name}...")
    
    # Load context from GEMINI.md
    gemini_md_path = os.path.join(target_path, "GEMINI.md")
    context = ""
    if os.path.exists(gemini_md_path):
        with open(gemini_md_path, 'r', encoding='utf-8') as f:
            context = f.read()[:5000] # Take first 5000 chars
    else:
        context = "Standard project structure."

    # 1. Identify Abstractions
    print("🧠 Identifying logical pillars...")
    prompt_abstr = f"""
Analyze this project based on this context:
---
{context}
---
Identify the 5 core technical concepts for a beginner.
For each concept, provide:
1. 'name': Clear name.
2. 'description': Brief pedagogical explanation (100 words) avec une ANALOGIE concrète.
3. 'files': Relevant files or symbols as a list like [file1.js, file2.js].

Formatte l'output uniquement en YAML list :
- name: ...
  description: ...
  files: [...]
"""
    res_abstr = call_gemini(prompt_abstr, api_key)
    if not res_abstr: return
    
    abstractions_yaml = extract_yaml(res_abstr)
    try:
        if HAS_YAML:
            abstractions = yaml.safe_load(abstractions_yaml)
        else:
            abstractions = simple_yaml_load(abstractions_yaml)
    except Exception as e:
        print(f"❌ Parsing Error: {e}")
        return

    # 2. Setup Directory
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M")
    academy_dir = os.path.join(vault_dir, project_name, timestamp, "academy")
    os.makedirs(academy_dir, exist_ok=True)

    # 3. Write Chapters
    chapters = []
    for i, concept in enumerate(abstractions, 1):
        name = concept.get('name', f"Concept {i}")
        desc = concept.get('description', "")
        print(f"✍️ Writing Chapter {i}: {name}...")
        
        prompt_chap = f"""
Project: {project_name}
Chapter {i}: {name}
Description: {desc}

Write a full educational tutorial chapter in Markdown.
Included: Analogy, Simple explanations, Mini code example.
Language: Français.
"""
        content = call_gemini(prompt_chap, api_key)
        if content:
            safe_name = "".join([c if c.isalnum() else "_" for c in name]).lower()
            filename = f"chapter_{i:02d}_{safe_name}.md"
            with open(os.path.join(academy_dir, filename), 'w', encoding='utf-8') as f:
                f.write(content)
            chapters.append((name, filename))

    # 4. Generate index
    index_path = os.path.join(academy_dir, "ACADEMY.md")
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(f"# 🎓 Academy : {project_name}\n\n")
        f.write(f"Généré le {datetime.datetime.now()}\n\n")
        f.write("## Sommaire\n")
        for name, fname in chapters:
            f.write(f"- [{name}](./{fname})\n")
            
    print(f"🎉 Academy generated successfully in {academy_dir}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python academy.py <target_path> <vault_dir> <api_key>")
        sys.exit(1)
    run_academy(sys.argv[1], sys.argv[2], sys.argv[3])
