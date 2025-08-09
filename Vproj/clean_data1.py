
import json
import pandas as pd

LOAD_PATH = r"C:\Users\kubag\Desktop\Vproj\raw_pokemon.json"
SAVE_PATH = r"C:\Users\kubag\Desktop\Vproj\cleaned_pokemon.csv"

with open(LOAD_PATH) as f:
    data = json.load(f)

df = pd.DataFrame(data)

def gender_label(rate):
    if rate == -1:
        return "Genderless"
    elif rate == 0:
        return "100% Male"
    elif rate == 8:
        return "100% Female"
    else:
        female_pct = rate * 12.5
        male_pct = 100 - female_pct
        return f"{int(male_pct)}% Male / {int(female_pct)}% Female"

df["gender_distribution"] = df["gender_rate"].apply(gender_label)

df["egg_groups"] = df["egg_groups"].fillna("")

df["base_happiness"] = df["base_happiness"].fillna(0).astype(int)
df["hatch_counter"] = df["hatch_counter"].fillna(0).astype(int)

df["evolution_stage"] = df["evolution_stage"].fillna(1).astype(int)
df["evolution_chain_id"] = df["evolution_chain_id"].fillna(df["id"]).astype(int)

df.to_csv(SAVE_PATH, index=False)
print(f" Cleaned and saved to {SAVE_PATH}")
