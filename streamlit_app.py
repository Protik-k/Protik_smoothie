# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
# import pandas as pd
# Write directly to the app
st.title(" :cup_with_straw: Customise your Smoothie! :cup_with_straw:")
st.write("Choose the fruits your want in custom smoothie!")
# option = st.selectbox('What is your favorite fruit?',('Banana', 'Strawberries', 'Peaches'))
# st.write("Your favorite fruit is:",option)

cnx = st.connection("snowflake")
session = cnx.session()
name_on_smoothie= st.text_input("Name on Smoothie: ")
st.write("Name on the smoothie will be : ", name_on_smoothie)
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
# st.dataframe(data=my_dataframe, use_container_width=True)
pd_df = my_dataframe.to_pandas()
ingredient_lists = st.multiselect('Choose upto 5 ingredients:', my_dataframe,max_selections=5)
if ingredient_lists:
    
    ingredients_string =''
    
    for fruit_chosen in ingredient_lists:
        ingredients_string += fruit_chosen +" "
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" +fruit_chosen)
# st.text(smoothiefroot_response.json())
        sfroot_df= st.dataframe(data=smoothiefroot_response.json(), use_container_width=True) 
        
    st.write(ingredients_string)
    

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','"""+name_on_smoothie+"""')"""

    # st.write(my_insert_stmt)
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered, '+name_on_smoothie+'!', icon="✅")



       

        
