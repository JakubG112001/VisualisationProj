
import requests
import json
from time import sleep
import os

API_URL = "https://pokeapi.co/api/v2/pokemon/"
SPECIES_URL = "https://pokeapi.co/api/v2/pokemon-species/"
MAX_POKEMON = 250
DATA_FILE = r"C:\Users\kubag\Desktop\Vproj\raw_pokemon.json"


def get_evolution_stages(chain, stage=1, mapping=None):
    if mapping is None:
        mapping = {}
    name = chain["species"]["name"]
    mapping[name] = stage
    for evo in chain.get("evolves_to", []):
        get_evolution_stages(evo, stage + 1, mapping)
    return mapping

def fetch_pokemon():
    all_pokemon = []
    for i in range(1, MAX_POKEMON + 1):
        print(f"Fetching Pokémon ID: {i}")
        p = requests.get(API_URL + str(i)).json()
        s = requests.get(SPECIES_URL + str(i)).json()

        types = [t['type']['name'] for t in p['types']]
        stats = {s['stat']['name']: s['base_stat'] for s in p['stats']}

        evolution_chain_url = s.get("evolution_chain", {}).get("url", "")
        evolution_chain_id = None
        evo_stage = 1

        if evolution_chain_url:
            try:
                evolution_chain_id = int(evolution_chain_url.strip("/").split("/")[-1])
                chain_data = requests.get(evolution_chain_url).json()
                evo_map = get_evolution_stages(chain_data["chain"])
                evo_stage = evo_map.get(p["name"], 1)
            except:
                evo_stage = 1

        all_pokemon.append({
            'id': p['id'],
            'name': p['name'],
            'base_experience': p['base_experience'],
            'height': p['height'],
            'weight': p['weight'],
            'type_1': types[0] if len(types) > 0 else None,
            'type_2': types[1] if len(types) > 1 else None,
            'hp': stats['hp'],
            'attack': stats['attack'],
            'defense': stats['defense'],
            'special-attack': stats['special-attack'],
            'special-defense': stats['special-defense'],
            'speed': stats['speed'],
            'abilities': ', '.join([a['ability']['name'] for a in p['abilities']]),
            'sprite_url': p['sprites']['other']['official-artwork']['front_default'],
            'gender_rate': s['gender_rate'],
            'capture_rate': s['capture_rate'],
            'is_legendary': s['is_legendary'],
            'base_happiness': s['base_happiness'],
            'hatch_counter': s['hatch_counter'],
            'egg_groups': ', '.join([eg['name'] for eg in s['egg_groups']]),
            'evolution_chain_id': evolution_chain_id,
            'evolution_stage': evo_stage
        })

        sleep(0.5)

    with open(DATA_FILE, "w") as f:
        json.dump(all_pokemon, f, indent=2)
    print(f" Saved {len(all_pokemon)} pokemon to {DATA_FILE}")

if __name__ == "__main__":
    fetch_pokemon()
