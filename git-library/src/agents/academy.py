import os
import sys
import json
import urllib.request
import urllib.error
import datetime
import re

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

def simple_yaml_load(text):
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
            if key in ['files', 'chapter_order', 'details']:
                match = re.search(r'\[(.*?)\]', val)
                if match: 
                    val = [s.strip().strip("'").strip('"') for s in match.group(1).split(',')]
            current_item[key] = val
    if current_item: items.append(current_item)
    return items

def extract_content(text, tag="yaml"):
    pattern = f"```{tag}(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Fallback to general block
    match = re.search(r"```(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def discover_models(api_key):
    api_key = api_key.strip()
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode('utf-8'))
            models = [m['name'].split('/')[-1] for m in data.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
            return models
    except Exception as e:
        print(f"⚠️ Could not list models: {e}")
        return []

def call_llm(prompt, api_key):
    api_key = api_key.strip()
    models = discover_models(api_key)
    if not models:
        models = ["gemini-1.5-flash", "gemini-pro", "gemini-1.0-pro"]
    
    for model in models:
        # Try v1beta as default
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        headers = {'Content-Type': 'application/json'}
        payload = {'contents': [{'parts': [{'text': prompt}]}]}
        
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
        try:
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                return res_data['candidates'][0]['content']['parts'][0]['text']
        except urllib.error.HTTPError as e:
            continue # Try next model
        except Exception as e:
            continue
    
    print("💀 All model attempts failed. Please verify API Key.")
    return None

def run_academy_elite(target_path, vault_dir, api_key, language="French"):
    project_name = os.path.basename(target_path)
    print(f"🎓 Launching Elite Academy Engine for {project_name}...")

    # Context Gathering
    gemini_md_path = os.path.join(target_path, "GEMINI.md")
    gemini_json_path = os.path.join(target_path, "GEMINI.json")
    
    context_md = ""
    if os.path.exists(gemini_md_path):
        with open(gemini_md_path, 'r', encoding='utf-8') as f:
            context_md = f.read()[:8000]
    
    surgical_data = {}
    if os.path.exists(gemini_json_path):
        try:
            with open(gemini_json_path, 'r', encoding='utf-8') as f:
                surgical_data = json.load(f)
        except: pass

    symbols = surgical_data.get('symbols', 'None discovered')
    deps = surgical_data.get('dependencies', 'None discovered')

    # STEP 1: IdentifyAbstractions
    print("🧠 Node [IdentifyAbstractions]: Finding core concepts...")
    prompt_abstr = f"""
Analysez ce projet :
{context_md}

Contexte chirurgical :
Symboles : {symbols}
Dépendances : {deps}

Identifiez les 10 abstractions/concepts fondamentaux de ce projet.
Pour chaque abstraction, fournissez :
- 'name' : Nom clair.
- 'description' : Explication pédagogique (50 mots).
- 'files' : Liste des symboles ou fichiers concernés.

Sortie YAML uniquement (liste) :
- name: ...
  description: ...
  files: [...]
"""
    res_abstr = call_llm(prompt_abstr, api_key)
    if not res_abstr: return
    abstractions = yaml.safe_load(extract_content(res_abstr)) if HAS_YAML else simple_yaml_load(extract_content(res_abstr))

    # STEP 2: AnalyzeRelationships
    print("🕸️ Node [AnalyzeRelationships]: Mapping connections...")
    abstr_context = "\n".join([f"{i}: {a['name']}" for i, a in enumerate(abstractions)])
    prompt_rel = f"""
Concepts identifiés :
{abstr_context}

Analysez comment ces concepts interagissent dans le code.
Générez un résumé global du projet et une liste de relations.

Sortie YAML :
summary: "Résumé complet du projet..."
details:
  - from: index_source
    to: index_cible
    label: "Type d'interaction"
"""
    res_rel = call_llm(prompt_rel, api_key)
    if not res_rel: return
    relationships = yaml.safe_load(extract_content(res_rel)) if HAS_YAML else simple_yaml_load(extract_content(res_rel))[0]

    # STEP 3: OrderChapters
    print("🔢 Node [OrderChapters]: Sequencing tutorial flow...")
    prompt_order = f"""
Concepts : {abstr_context}
Détermine l'ordre logique d'apprentissage (du plus basique au plus complexe).

Sortie YAML :
chapter_order: [index0, index2, index1, ...]
"""
    res_order = call_llm(prompt_order, api_key)
    if not res_order: return
    order_data = yaml.safe_load(extract_content(res_order)) if HAS_YAML else simple_yaml_load(extract_content(res_order))[0]
    chapter_order = order_data.get('chapter_order', list(range(len(abstractions))))

    # STEP 4: Batch WriteChapters
    print(f"✍️ Node [Batch WriteChapters]: Generating {len(chapter_order)} chapters...")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    academy_dir = os.path.join(vault_dir, project_name, timestamp, "academy")
    os.makedirs(academy_dir, exist_ok=True)
    
    chapters = []
    for rank, idx in enumerate(chapter_order, 1):
        idx = int(idx)
        concept = abstractions[idx]
        name = concept['name']
        print(f"  > Chapitre {rank}: {name}...")
        
        prompt_chap = f"""
Projet : {project_name}
Chapitre {rank} : {name}
Description : {concept['description']}
Fichiers concernés : {concept['files']}

Rédigez un chapitre complet en Markdown ({language}).
Incluez :
- Une ANALOGIE concrète.
- Des explications simples.
- Comment ça marche techniquement.
- Un mini exemple de code.
"""
        content = call_llm(prompt_chap, api_key)
        if content:
            safe_name = "".join([c if c.isalnum() else "_" for c in name]).lower()
            filename = f"chapter_{rank:02d}_{safe_name}.md"
            with open(os.path.join(academy_dir, filename), 'w', encoding='utf-8') as f:
                f.write(content)
            chapters.append((name, filename))

    # STEP 5: CombineTutorial
    print("📚 Node [CombineTutorial]: Finalizing Academy Index...")
    index_path = os.path.join(academy_dir, "ACADEMY.md")
    
    # Building Mermaid Diagram
    mermaid = "flowchart TD\n"
    rels = relationships.get('details', [])
    if isinstance(rels, list):
        for rel in rels:
            if not isinstance(rel, dict): continue
            try:
                f_idx = int(rel.get('from', -1))
                t_idx = int(rel.get('to', -1))
                if 0 <= f_idx < len(abstractions) and 0 <= t_idx < len(abstractions):
                    f_name = abstractions[f_idx]['name'].replace('"', '')
                    t_name = abstractions[t_idx]['name'].replace('"', '')
                    label = str(rel.get('label', '')).replace('"', '')
                    mermaid += f'    A{f_idx}["{f_name}"] -- "{label}" --> A{t_idx}["{t_name}"]\n'
            except: pass

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(f"# 🎓 Academy : {project_name}\n\n")
        f.write(f"{relationships.get('summary', 'Project overview.')}\n\n")
        f.write("## 🏗️ Architecture des Concepts\n")
        f.write(f"```mermaid\n{mermaid}```\n\n")
        f.write("## 📖 Sommaire\n")
        for name, fname in chapters:
            f.write(f"- [{name}](./{fname})\n")
            
    # STEP 6: Feedback loop to GEMINI.json
    print("🔄 Updating GEMINI.json with Academy context...")
    if os.path.exists(gemini_json_path):
        try:
            with open(gemini_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            data['academy'] = {
                'summary': relationships.get('summary'),
                'pillars': [a['name'] for a in abstractions],
                'vault_path': academy_dir
            }
            with open(gemini_json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except: pass

    print(f"🎉 Elite Academy generated successfully: {academy_dir}")
    return academy_dir

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python academy.py <target_path> <vault_dir> <api_key>")
        sys.exit(1)
    run_academy_elite(sys.argv[1], sys.argv[2], sys.argv[3])
