import sys
import os
from dotenv import load_dotenv

# Ajout du chemin vers les skills pour l'import de fuzzsuite
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'skills'))

try:
    from fuzzsuite.tools.tickets import tickets_main
except ImportError as e:
    print(f"❌ Erreur : Impossible de charger FuzzSuite. {e}")
    sys.exit(1)

def run_tickets(plan_path, output_dir):
    print(f"🎫 Génération des tickets à partir de : {plan_path}")
    load_dotenv()
    
    if not os.path.exists(plan_path):
        print(f"❌ Erreur : Plan de refactoring non trouvé à {plan_path}")
        sys.exit(1)
        
    tickets_main(plan_path, output_dir)
    print(f"✅ Tickets générés avec succès dans {output_dir}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python tickets.py <plan_yaml> <output_dir>")
        sys.exit(1)
    run_tickets(sys.argv[1], sys.argv[2])
