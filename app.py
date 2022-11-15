import streamlit as st
import pandas as pd
import pymongo

#Provide a description of the app's purpose
st.title('Pittsburgh Fellows Data Explorer')

FELLOWS_GRAD_YEAR_LIST = [year for year in range(2008,2023)]
FELLOWS_GRAD_YEAR_LIST.reverse()

EMPLOYER_LIST = []

#Follow connecting to mongo instructions: https://docs.streamlit.io/knowledge-base/tutorials/databases/mongodb
# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():
    return pymongo.MongoClient(st.secrets["DB_URI"])

client = init_connection()

# Pull data from the collection.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=600)
def get_data():
    db = client.get_database('pittsburgh_fellows')
    items =  db.fellows.find( {},
    {'name':1,'fellows_grad_year':1,'current_title':1,'current_location':1, 'experience_history':1, 'education_history':1, '_id': 0})
    items = list(items)  # make hashable for st.experimental_memo
    return items

#Get the full data set of fellows info
full_data_set = get_data()

#Get unique employers from the full dataset
for fellow in full_data_set:
    try:
        for employment_record in fellow['experience_history']:
            EMPLOYER_LIST.append(employment_record['employer'])
    except:
        pass

EMPLOYER_LIST = list(set(EMPLOYER_LIST))
EMPLOYER_LIST.sort()

#Functionality to do stuff with it
#Allow user to filter data by Fellows class or by employer
selected_filter = st.radio(
    "Filter Data By",
    ('Fellows Graduating Class Year', 'Employer'))

if selected_filter == 'Fellows Graduating Class Year':
    selected_year = st.selectbox(
        "Year",
        FELLOWS_GRAD_YEAR_LIST
    )
    data_to_write = list(filter(lambda d: d['fellows_grad_year'] == selected_year, full_data_set))
    st.write(data_to_write)
elif selected_filter == 'Employer':
    selected_employer = st.multiselect(
        "Employer",
        EMPLOYER_LIST
    )
    data_to_write = []
    for fellow in full_data_set:
        try:
            for employment_record in fellow['experience_history']:
                if employment_record['employer'] in selected_employer:
                    data_to_write.append(fellow)
                    break
        except:
            pass
    st.write(data_to_write)