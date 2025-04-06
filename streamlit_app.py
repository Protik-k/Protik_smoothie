import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

st.markdown("""
    <style>
    .title {
        font-size: 2em;
        color: #4CAF50;
        text-align: center;
    }
    .subheader {
        font-size: 1.5em;
        color: #FF5722;
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
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🥤 Customise your Smoothie! 🥤</div>', unsafe_allow_html=True)
st.write("Choose the fruits you want in your custom smoothie!")

cnx = st.connection("snowflake")
session = cnx.session()
name_on_smoothie = st.text_input("Name on Smoothie:")
st.write("Name on the smoothie will be:", name_on_smoothie)

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
if my_dataframe.count() > 0:
    pd_df = my_dataframe.to_pandas()

    ingredient_lists = st.multiselect('Choose up to 5 ingredients:', pd_df['FRUIT_NAME'], max_selections=5)
    if ingredient_lists:
        ingredients_string = " ".join(ingredient_lists)
        
        for fruit_chosen in ingredient_lists:
            search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
            st.markdown(f'<div class="subheader">{fruit_chosen} Nutrition Information</div>', unsafe_allow_html=True)
            
            try:
                smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
                smoothiefroot_response.raise_for_status()
                sfroot_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
            except requests.exceptions.RequestException as e:
                st.error(f"Error fetching data for {fruit_chosen}: {e}")
        
        st.write(ingredients_string)
        
        my_insert_stmt = """
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES (%s, %s)
        """
        time_to_insert = st.button('Submit Order')
        if time_to_insert:
            session.sql(my_insert_stmt, (ingredients_string, name_on_smoothie)).collect()
            st.success(f'Your Smoothie is ordered, {name_on_smoothie}!', icon="✅")
else:
    st.error("No data available in the table.")
