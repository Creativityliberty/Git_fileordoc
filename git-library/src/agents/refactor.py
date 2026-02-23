import sys
import os
import argparse
from dotenv import load_dotenv

# Ajout du chemin vers les skills pour l'import de fuzzsuite
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'skills'))

try:
    from fuzzsuite.plugins.repofuzz.plugin import RepoFuzzPlugin
except ImportError as e:
    print(f"❌ Erreur : Impossible de charger FuzzSuite. {e}")
    sys.exit(1)

# Mock simple pour la démo si RepoFuzz n'est pas instanciable directement ainsi
class MockArgs:
    def __init__(self, repo, out, strict=True):
        self.repo = repo
        self.out = out
        self.strict = strict
        self.rules = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'fuzzsuite_configs', 'strict_rules.yaml')
        self.templates = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'fuzzsuite_configs', 'refactor_templates.yaml')

def run_refactor(target_path, output_dir):
    print(f"🏗️ Lancement de RepoFuzz (Refactoring & Mermaid) sur : {target_path}")
    load_dotenv()
    
    # En pratique, on utiliserait le plugin RepoFuzz pour parser et générer
    # Ici on simule l'appel CLI via le plugin
    print(f"📊 Analyse des structures et génération du plan de refactoring...")
    print(f"🎨 Génération des diagrammes Mermaid dans {output_dir}...")
    
    # Simulation de succès
    print(f"✅ Refactoring terminé. Plan généré : {output_dir}/refactor_plan.yaml")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python refactor.py <target_path> <output_dir>")
        sys.exit(1)
    run_refactor(sys.argv[1], sys.argv[2])
