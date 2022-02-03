import pandas as pd
import streamlit as st
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import yfinance as yf

st.title('S&P 500 Explorer')

st.markdown("""
This app retrieves the list of the **S&P 500** (from wikipedia) and its corresponding **stock closing price** (year-to-date)!
* **Python Libraries:** base64, pandas, streamlit, seaborn, numpy, yfinance
* **Data Source:** [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies).
""")

st.sidebar.header('User Input Features')

# Webscraping of the S&P 500 data
# 
@st.cache
def load_data():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    html = pd.read_html(url, header = 0)
    df = html[0]
    return df

df = load_data()
sector = df.groupby('GICS Sector')

# Sidebar - Sector Selection
sorted_sector_unique = sorted(df['GICS Sector'].unique())
selected_sector = st.sidebar.multiselect('Sector', sorted_sector_unique, sorted_sector_unique)

# Sidebar - Filtering Data
df_selected_sector = df[(df['GICS Sector'].isin(selected_sector))]

st.header('Display Companies in Selected Sector')
st.write('Data Dimension' + str(df_selected_sector.shape[0]) + ' row and ' + str(df_selected_sector.shape[1]))
st.dataframe(df_selected_sector)

# Download S&P 500 Data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def file_download(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Download csv file</a>'
    return href
    
st.markdown(file_download(df_selected_sector), unsafe_allow_html = True)
    
# https://pypi.org/project/yfinance/

data = yf.download(
    tickers = list(df_selected_sector[:].Symbol),
    period = "ytd",
    interval = "1d",
    group_by = 'ticker',
    auto_adjust = True,
    prepost = True,
    threads = True,
    proxy = None
)
    
# Plot of the closing prices of the Queried Symbol
def price_plot(symbol):
    df = pd.dataframe(data[symbol].Close)
    df['Date'] = df.index 
    plt.fill_between(df.Data, df.Close, colors = 'skyblue', alpha  = 0.3)
    plt.plot(df.Date, df.Close, color='skyblue', alpha=0.8)
    plt.xticks(rotation=90)
    plt.title(symbol, fontweight='bold')
    plt.xlabel('Date', fontweight='bold')
    plt.ylabel('Closing Price', fontweight='bold')
    return st.pyplot()

num_company = st.sidebar.slider('Number of Companies', 1, 5)

if st.button('Show Plots'):
    st.header('Stock Closing Price')
    for i in list(df_selected_sector.Symbol)[:num_company]:
        price_plot(i)
    