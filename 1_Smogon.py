import requests, json, math
import streamlit as st
import pandas as pd
import pokebase as pb
from collections import defaultdict

pkmn = st.text_input('Who would you like to research for your VGC Reg i team?')

# url = "https://www.smogon.com/stats/2025-05/chaos/gen9vgc2025regi-0.json"

base_url = "https://www.smogon.com/stats/{}/chaos/gen9vgc2025regi-0.json"

# Generate month strings from April 2025 to now in "YYYY-MM" format
months = pd.date_range(start="2025-04-01", end=pd.Timestamp.today(), freq="MS").strftime("%Y-%m").tolist()

urls = [base_url.format(month) for month in months]


if pkmn:
    pokemon = pb.pokemon(pkmn.lower())
    sprite = pb.SpriteResource('pokemon', pokemon.id)


## function connecting to URL
def fetch_smogon_json(urls):

    merged = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for url in urls:
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            json_data = resp.json().get('data', {})
            
            for pkmn, p_data in json_data.items():
                for category, values in p_data.items():
                    if isinstance(values, dict) and category!='Checks and Counters':  # e.g., 'Moves', 'Items'
                        for key, count in values.items():
                            merged[pkmn][category][key] += count
                    else:
                        merged[pkmn][category] = values  # e.g., 'Raw count', 'Viability Ceiling'

        except Exception as e:
            print(f"Failed to load {url}: {e}")
    
    return {'data': merged}

# Fetch the data
data = fetch_smogon_json(urls)


## function for ordering information
def usage_ordering(pkmn, nKey, top):
    pkmn=pkmn.title()
    try:
        usage = []
        total = 0
        
        nestedKey = data['data'][pkmn][nKey]
        total = sum(nestedKey.values())

        # Sort descending order
        sortedNest = sorted(nestedKey.items(), key=lambda x: x[1], reverse=True)
        
        for key_name, count in sortedNest[:top]:
            percent = round((count / total) * 100, 2)
            usage.append((key_name.title(), f"{percent:.2f}%"))

        df = pd.DataFrame(usage, columns=[nKey, 'Count'])
        return df
    
    except Exception as e:
        st.error(f"Could not find {nKey} for '{pkmn}', Please check spelling.")
        return None


##### Sprite and Type #####

if pkmn:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(sprite.url)
    with col2:
        for type_slot in pokemon.types:
            st.write(f"Type {type_slot.slot}: {type_slot.type.name.title()}")


##### Dataframes #####

abilityDF = usage_ordering(pkmn, 'Abilities', 6)
st.dataframe(abilityDF, hide_index=True)

dfs = []
topParams =  [('Items', 25), ('Moves', 20), ('Tera Types', 19)]
for nKey, top in topParams:
    tdf = usage_ordering(pkmn, nKey, top)
    if tdf is not None:
        dfs.append((nKey, tdf))

max_cols = 3
cols = st.columns(min(max_cols, len(dfs)))

for col, (title, tdf) in zip(cols, dfs):
    with col:
        st.dataframe(tdf, hide_index=True, width=3050, height=300)

dfs = []
botParams = [('Teammates', 25), ('Spreads', 15)]
for nKey, top in botParams:
    bdf = usage_ordering(pkmn, nKey, top)
    if bdf is not None:
        dfs.append((nKey, bdf))

max_cols = 2
cols = st.columns(min(max_cols, len(dfs)))

for col, (title, bdf) in zip(cols, dfs):
    with col:
        st.dataframe(bdf, hide_index=True, width=3050, height=300)


# ## function for ordering information, Returns list of tuples: (pokemon_name, raw_count)
# def usage_ordering_by_raw_count(data):

#     pokemon_usage = []
    
#     if 'data' in data:
#         for pokemon_name, pokemon_data in data['data'].items():
#             raw_count = pokemon_data.get('Raw count', 0)
#             pokemon_usage.append((pokemon_name, raw_count))
    
#     # Sort in descending order
#     return sorted(pokemon_usage, key=lambda x: x[1], reverse=True)


# if pkmn:
#     pkmn=pkmn.title()
#     try:
#         item_usage = []
        
#         if pkmn in data['data']:

#             items = data['data'][pkmn]['Items']

#             for item_name, count in items.items():
#                 item_usage.append((item_name, count))
#         else:
#             st.write("Something is ljljlwrong")
        
#         # Sort descending order
#         items_sorted = sorted(item_usage, key=lambda x: x[1], reverse=True)
#         df = pd.DataFrame(items_sorted[:10], columns=['Item', 'Count'])
#         st.write(df)
#     except Exception as e:
#         st.error(f"Could not find '{pkmn}', Please check spelling.")


# if data:
#     # Order by raw count
#     ordered_pokemon = usage_ordering_by_raw_count(data)
    
#     # Print top 10 as example
#     print("Top 10 Pokemon by usage:")
#     for i, (name, count) in enumerate(ordered_pokemon[:10], 1):
#         print(f"{i}. {name}: {count}")
