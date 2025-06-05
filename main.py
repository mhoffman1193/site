import streamlit as st
import pokebase as pb
import random


x = st.text_input('Who is your favorite Pokemon?')

# Handle button click
if st.button("Don't have one? Try a random!"):
    st.session_state.random_id = random.randint(1,1024)
    st.session_state.use_random = True

# Set default use_random state
if "use_random" not in st.session_state:
    st.session_state.use_random = False

    if x:
        try:
            pkmn = pb.pokemon(x.lower())
        except:
            pkmn = None
    elif "random_id" in st.session_state:
        pkmn = pb.pokemon(st.session_state.random_id)
    else:
        pkmn = None

# Choose source of Pokémon
try:
    if st.session_state.use_random:
        pkmn = pb.pokemon(st.session_state.random_id)
        name_display = pkmn.name.title()
    elif x:
        pkmn = pb.pokemon(x.lower())
        name_display = x.title()
    else:
        pkmn = None
except:
    pkmn = None

# Reset random usage if user starts typing again
if x and st.session_state.use_random:
    st.session_state.use_random = False

# Show Pokémon data
if pkmn:
    try:

        sprite = pb.SpriteResource('pokemon', pkmn.id)

        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(sprite.url, caption=name_display)
        with col2:
            st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)
            for type_slot in pkmn.types:
                st.write(f"Type {type_slot.slot}: {type_slot.type.name.title()}")

        for ability_slot in pkmn.abilities:
            ability_info = pb.ability(ability_slot.ability.name)
            effect = next(e.effect for e in ability_info.effect_entries if e.language.name == 'en')
            st.write(f"{ability_info.name.title()}: {effect}")
            
    except Exception as e:
        st.error(f"Could not find '{x}', Please check spelling.")
        print(e)