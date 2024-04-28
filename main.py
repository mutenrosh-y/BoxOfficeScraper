import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.express as px
from collections import defaultdict
import re

# Function to scrape movie collections
def scrape_collections(url):
    # Send HTTP GET request
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Scrape individual movie data
    movie_data = defaultdict(list)
    table = soup.find('div', class_='table1')
    if table:
        rows = table.find_all('tr')[1:]  # Skip header row
        for row in rows:
            columns = row.find_all('td')
            movie_title = columns[0].text.strip()
            india_net = columns[2].text.strip()
            india_gross = columns[3].text.strip()

            # Remove non-numeric characters
            india_net_cleaned = re.sub(r'[^\d.]', '', india_net)
            india_gross_cleaned = re.sub(r'[^\d.]', '', india_gross)

            try:
                india_net = float(india_net_cleaned)
            except ValueError:
                india_net = 0.0

            try:
                india_gross = float(india_gross_cleaned)
            except ValueError:
                india_gross = 0.0

            release_date = columns[6].text.strip()
            movie_data[release_date].append({
                'title': movie_title,
                'india_net': india_net,
                'india_gross': india_gross
            })

    return movie_data

# Streamlit UI
st.set_page_config(layout="wide")

# Page title and headers
st.title('Indian Movie Box Office Dashboard')
st.header('Box Office Collections')
st.subheader('Visualizing movie collections over time')

# URL input
url = st.text_input('Enter the URL of the source page:',
                    'https://www.example.com/box-office')

# Scrape button
if st.button('Scrape Data'):
    movie_data = scrape_collections(url)

    # Create a DataFrame for plotting
    plot_data = []
    for release_date, movies in movie_data.items():
        for movie in movies:
            plot_data.append({
                'Release Date': release_date,
                'Title': movie['title'],
                'India Net': movie['india_net'],
                'India Gross': movie['india_gross']
            })
    df = pd.DataFrame(plot_data)

    # Plot daily combined collections by movie
    st.subheader('Daily Box Office Collections by Movie')
    fig = px.bar(df, x='Release Date', y=['India Net', 'India Gross'], color='Title', 
                 title='Daily Box Office Collections by Movie',
                 labels={'value': 'Collections (INR Crores)'}, barmode='stack')
    st.plotly_chart(fig, use_container_width=True)

    # Display movie data segregated by weeks
    for release_date, movies in movie_data.items():
        if movies:  # Check if there are movies for this week
            st.subheader('Week starting from: ' + release_date)
            col1, col2, col3 = st.columns(3)
            for movie in movies:
                with col1:
                    st.write('**Title:**', movie['title'])
                with col2:
                    st.write('**India Net:**', movie['india_net'])
                with col3:
                    st.write('**India Gross:**', movie['india_gross'])
            # Add markdown divider after displaying all the attributes for the week
            st.markdown('---')
