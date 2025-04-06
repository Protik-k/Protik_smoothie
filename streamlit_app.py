# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Custom CSS for food-themed styling
st.markdown("""
    <style>
    body {
        background-color: #FFF8E1;
        font-family: 'Arial', sans-serif;
    }
    .title {
        font-size: 3em;
        color: #F57C00;
        text-align: center;
        font-weight: bold;
        margin-top: 20px;
        text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
    }
    .subheader {
        font-size: 1.5em;
        color: #D32F2F;
        margin-top: 20px;
        font-weight: bold;
    }
    .button {
        background-color: #FF9800;
        color: white;
        border: none;
        padding: 15px 30px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 18px;
        margin: 10px 5px;
        cursor: pointer;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .button:hover {
        background-color: #FB8C00;
    }
    .text-input {
        font-size: 1.3em;
        padding: 12px;
        border: 2px solid #FF5722;
        border-radius: 8px;
        width: 100%;
        margin-top: 15px;
    }
    .multiselect {
        font-size: 1.3em;
        padding: 12px;
        border: 2px solid #FF5722;
        border-radius: 8px;
        width: 100%;
        margin-top: 15px;
    }
    .success {
        font-size: 1.8em;
        color: #388E3C;
        font-weight: bold;
        text-align: center;
        margin-top: 20px;
    }
    .fruit-info {
        background-color: #FFEB3B;
        padding: 15px;
        border-radius: 8px;
        margin-top: 15px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .fruit-info h3 {
        font-size: 1.4em;
        color: #D32F2F;
    }
    </style>
""", unsafe_allow_html=True)

# Write directly to the app
st.markdown('<div class="title">🥤 Customize Your Smoothie! 🍓</div>', unsafe_allow_html=True)
st.write("Pick your favorite fruits and make your own personalized smoothie!")

cnx = st.connection("snowflake")
session = cnx.session()
name_on_smoothie = st.text_input("Name on Smoothie:", key="name_input", help="Enter the name you want on your smoothie")
st.write("Your smoothie will be personalized with the name:", name_on_smoothie)

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

ingredient_lists = st.multiselect('Choose up to 5 fruits for your smoothie:', pd_df['FRUIT_NAME'], max_selections=5, key="ingredient_select", help="Select up to 5 fruits for your smoothie")

if ingredient_lists:
    ingredients_string = " ".join(ingredient_lists)
    
    for fruit_chosen in ingredient_lists:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.markdown(f'<div class="subheader">{fruit_chosen} Nutrition Information</div>', unsafe_allow_html=True)
        
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        
        if smoothiefroot_response.status_code == 200:
            fruit_data = smoothiefroot_response.json()
            st.markdown(f'<div class="fruit-info"><h3>{fruit_chosen} Details</h3><p>{fruit_data["description"]}</p></div>', unsafe_allow_html=True)
        else:
            st.warning(f"Sorry, nutrition data for {fruit_chosen} is unavailable.")
    
    st.write(ingredients_string)
    
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_smoothie}')
    """
    
    time_to_insert = st.button('Submit Order', key="submit_button", help="Click to submit your smoothie order")
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.markdown(f'<div class="success">Your smoothie is on the way, {name_on_smoothie}!</div>', unsafe_allow_html=True)
