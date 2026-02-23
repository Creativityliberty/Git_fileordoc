import sys
import os
import argparse
from dotenv import load_dotenv

# Ajout du chemin vers les skills pour l'import de fuzzsuite
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'skills'))

try:
    from fuzzsuite.tools.check import check_main
    from fuzzsuite.plugins.repofuzz.plugin import RepoFuzzPlugin
except ImportError as e:
    print(f"❌ Erreur : Impossible de charger FuzzSuite. {e}")
    sys.exit(1)

def run_audit(target_path, output_dir):
    print(f"🔍 Lancement de l'Audit de Sécurité & Qualité sur : {target_path}")
    load_dotenv()
    
    # 1. Check CI (Strict rules)
    rules_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'fuzzsuite_configs', 'strict_rules.yaml')
    if not os.path.exists(rules_path):
        print(f"⚠️ Fichier de règles non trouvé : {rules_path}")
        # On peut continuer sans ou avec des règles par défaut
    
    exit_code = check_main(repo=target_path, rules=rules_path, out_dir=output_dir)
    
    if exit_code == 0:
        print("✅ Audit terminé : Aucune violation critique détectée.")
    else:
        print(f"⚠️ Audit terminé : {exit_code} violations détectées. Voir les rapports dans {output_dir}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python audit.py <target_path> <output_dir>")
        sys.exit(1)
    run_audit(sys.argv[1], sys.argv[2])
