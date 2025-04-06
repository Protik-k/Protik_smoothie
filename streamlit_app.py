# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
# import pandas as pd

# Custom CSS for styling
st.markdown("""
    <style>
    .title {
        font-size: 2.5em;
        color: #4CAF50;
        text-align: center;
        font-weight: bold;
    }
    .subheader {
        font-size: 1.5em;
        color: #FF5722;
        margin-top: 20px;
    }
    .button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 5px;
    }
    .text-input {
        font-size: 1.2em;
        padding: 10px;
        border: 2px solid #4CAF50;
        border-radius: 5px;
        width: 100%;
    }
    .multiselect {
        font-size: 1.2em;
        padding: 10px;
        border: 2px solid #FF5722;
        border-radius: 5px;
        width: 100%;
    }
    .success {
        font-size: 1.5em;
        color: #4CAF50;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Write directly to the app
st.markdown('<div class="title">🥤 Customise your Smoothie! 🥤</div>', unsafe_allow_html=True)
st.write("Choose the fruits you want in your custom smoothie!")

cnx = st.connection("snowflake")
session = cnx.session()
name_on_smoothie = st.text_input("Name on Smoothie:", key="name_input", help="Enter the name you want on your smoothie")
st.write("Name on the smoothie will be:", name_on_smoothie)

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

ingredient_lists = st.multiselect('Choose up to 5 ingredients:', pd_df['FRUIT_NAME'], max_selections=5, key="ingredient_select", help="Select up to 5 fruits for your smoothie")
if ingredient_lists:
    ingredients_string = " ".join(ingredient_lists)
    
    for fruit_chosen in ingredient_lists:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.markdown(f'<div class="subheader">{fruit_chosen} Nutrition Information</div>', unsafe_allow_html=True)
        
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        sfroot_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    
    st.write(ingredients_string)
    
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_smoothie}')
    """
    
    time_to_insert = st.button('Submit Order', key="submit_button", help="Click to submit your smoothie order")
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.markdown(f'<div class="success">Your Smoothie is ordered, {name_on_smoothie}!</div>', unsafe_allow_html=True)
