#Importing pandas for excel-style data manipulation
import pandas as pd
import os
#argv checks command line arguments
from sys import argv
#Importing streamlit for data visualization (drawing to localhost)
import streamlit as st
#Importing pyplot to make the plots
import matplotlib.pyplot as plt

#Best tutorial: https://www.youtube.com/watch?v=Sb0A9i6d320 Turn An Excel Sheet Into An Interactive Dashboard Using Python (Streamlit)

@st.cache
def load_data(filename):
    data = pd.read_csv(filename)
    data['Date'] = pd.to_datetime(data['Date'], format='%m/%d/%Y')
    return data

#@st.cache Caching this causes issues for some reason
def plotData(data, columnsToDraw):
    fig, ax = plt.subplots()
    for i in range(len(columnsToDraw)):
        ax.plot(data['Date'], data[columnsToDraw[i]], label=columnsToDraw[i])
    ax.set_xlabel('Date')
    ax.set_ylabel('Value ($)')
    ax.tick_params(axis='x', labelrotation=45)
    fig.legend(loc='upper left')
    return fig

#Default file locations. CSV files used for the purposes of this program
portfolioComparisonFile = 'PortfolioComparisonAnalysis.csv'

#Command line arguments must be specified with -- two dashes or else streamlit uses them as its own arguments
#EDIT ^This does not seem to be true
specifiedFile = str(argv[1]) if len(argv) > 1 else ""

if (specifiedFile and os.path.exists(os.path.join(os.getcwd(), specifiedFile))):
    portfolioComparisonFile = specifiedFile

st.set_page_config(layout='wide', page_icon='bar_chart', page_title='Portfolio Visualized')
st.title("Portfolio Visualized Comparison")
st.write("Drawing from: " + portfolioComparisonFile)

showPortfolio = st.checkbox("Show Portfolio", value=True)
showComparison = st.checkbox("Show Comparison (S&P 500) Portfolio", value=True)

portfolioDf = load_data(portfolioComparisonFile)

#st.write('Data', portfolioDf)

#Separating graphs into columns
left_col, right_col = st.columns(2)

left_col.pyplot(plotData(portfolioDf, ['Account value', 'Comparison account value']))
right_col.pyplot(plotData(portfolioDf, ['Hypothetical account share price', 'Comparison price']))
left_col.pyplot(plotData(portfolioDf, ['Cumulative deposits']))
right_col.pyplot(plotData(portfolioDf, ['Account as percentage of comparison']))