import json
import re

# Load the top 100 associations
with open('top100.json', 'r') as f:
    associations = json.load(f)

# Known missions lookup table (will be populated)
mission_lookup = {}

# Process each association
for i, assoc in enumerate(associations):
    name = assoc['name']
    current_mission = assoc.get('mission', '')
    siret = assoc.get('siret', '')
    
    # Check if current mission is a placeholder
    placeholder_patterns = [
        r'^Subvention',
        r'^Fonctionnement',
        r'^fonctionnement',
        r'^ACOMTE',
        r'^acompte',
        r'^Création',
        r'^Convention',
        r'^Réouverture',
        r'^Aide',
        r'^Complément',
        r'^Demande',
        r'^Projet',
        r'^Budget',
        r'^PAOMIE',
        r'^ARE',
        r'^ESI',
        r'^BBP',
        r'^VVV',
        r'^FSF',
        r'^PLATEFORME',
        r'^Opérations',
        r'^Implantation',
        r'^Saison',
        r'^Mise',
        r'^Action',
        r'^au fil des',
        r'^7 -',
        r'^BBP',
        r'^BP',
        r'^2021-',
        r'^Investissement',
        r'^Activité',
        r'^des actions',
        r'^Un parcours',
        r'^HG',
        r'^2020-',
        r'^[0-9]+ ',  # Starts with number
        r'^[A-Z]{2,4} [0-9]',  # Pattern like "PAOMIE -" or "ARE -"
        r'^[A-Z]+\s+[0-9]',  # All caps followed by number
        r'^[a-z]',  # Starts with lowercase
        r'rue\s+',  # Contains "rue" (address)
        r'Paris \(',  # Contains "Paris (arrondissement)"
        r'^[0-9]+e',  # Starts with number + e
        r'^[0-9]+,',  # Starts with number + comma
    ]
    
    is_placeholder = False
    for pattern in placeholder_patterns:
        if re.search(pattern, current_mission, re.IGNORECASE):
            is_placeholder = True
            break
    
    print(f"{i+1}. {name}")
    print(f"   Current: {current_mission[:80]}...")
    print(f"   Placeholder: {is_placeholder}")
    print(f"   SIRET: {siret}")
    print()

print(f"\nTotal associations to research: {len(associations)}")
