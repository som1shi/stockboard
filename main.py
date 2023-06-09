import streamlit as st
import yfinance as finance
import pandas as pd
import altair as alt
from datetime import date
import datetime as dt

import plotly.graph_objs as go
import random

from tokenize import Double
import requests
import bs4 

from newsapi import NewsApiClient
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

Analyzer = SentimentIntensityAnalyzer()

st.title("StockBoard")


user_input = st.text_input("Stock", 'MSFT')

brk = finance.Ticker(user_input)

x = brk.info['shortName']
start = st.date_input("Date", dt.datetime(2023, 1, 1))
st.header(x)

county = st.slider('Sample Size', 1, 50, 25)



url = 'https://news.google.com/search?q='+ x
request_result=requests.get(url)
soup = bs4.BeautifulSoup(request_result.text, "html.parser")
heading_object=soup.find_all( 'h3' )

newsapi = NewsApiClient(api_key='81945b20aa7547bd8a0066b30c989955')


count = 0
init=[]
for info in heading_object:
    init.append(info.getText())
    count+=1
    if count==county:
        break

neg_confidences = []
neu_confidences = []
pos_confidences = []


def get_confidence_values(articles):

    response = []
    for article in articles:
        response.append(Analyzer.polarity_scores(article))

    for i in response:
        neg_confidences.append(i["neg"])
        neu_confidences.append(i["neu"])
        pos_confidences.append(i["pos"])
    
def get_averages(list1, list2, list3):
    print(sum(list1)/len(list1))
    print(sum(list2)/len(list2))
    print(sum(list3)/len(list3))


today = date.today().strftime("%m/%d/%Y")


starty = start.strftime("%m/%d/%Y")


res = (dt.datetime.strptime(today, "%m/%d/%Y") - dt.datetime.strptime(starty, "%m/%d/%Y")).days

hist = brk.history(period= (str(res) + "d"), auto_adjust=True)

df = pd.DataFrame()


df['Date'] = hist.index
df['Date'] = df['Date'].dt.strftime("%Y-%m-%d")
df['Stock Value'] = hist['Close'].values
df.tail()

get_confidence_values(init)

listy = [1, 2, 3]

df2 = pd.DataFrame()


kek = st.slider('Forecast Days', 0, 30, 10)

randomlist =  random.choices(listy, cum_weights= ((sum(pos_confidences)/len(pos_confidences)), (sum(neu_confidences)/len(neu_confidences)), (sum(neg_confidences)/len(neg_confidences))), k=kek)


entry = {'Date': df['Date'].iloc[-1], 'EstStock': df['Stock Value'].iloc[-1]}

df.loc[len(df.index)] = [entry['Date'], entry['EstStock']]

while randomlist:
    value = df['Stock Value'].iloc[len(df.index)-1]
    if randomlist[0] == 1:
        valy = value * (1 + random.choice(pos_confidences)*0.05)
    elif randomlist[0] == 2:
        valy = value
    elif randomlist[0] == 3:
        valy = value * (1 - random.choice(neg_confidences)*0.05)

    randomlist.pop(0)
    y = df['Date'].iloc[len(df.index)-1]
    daty =  f'{y}'
    datetime_object = dt.datetime.strptime(daty[:10], '%Y-%m-%d')
    datetime_object = datetime_object + dt.timedelta(days=1)

    df.loc[len(df.index)] = [datetime_object, valy] 


df.set_index('Date', inplace=True)

data = df.reset_index().melt('Date')
base = alt.Chart(data).mark_line().encode(
    x= alt.X('Date:T',  axis=alt.Axis( 
                                labelAngle=-45, 
                                labelOverlap=False, 
                                format = ("%b %Y"))),
    y='value',
    color='variable'
)


st.altair_chart(base, use_container_width=True)


st.header("Bear/Bull Market Indicator")
fig = go.Figure(go.Indicator(
    mode = "gauge+number+delta",
    value = (sum(pos_confidences)/len(pos_confidences))/(sum(neg_confidences)/len(neg_confidences)+sum(pos_confidences)/len(pos_confidences))*100,
    domain = {'x': [0, 1], 'y': [0, 1]},
    gauge = {
        'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
        'bar': {'color': "#cdafe3",'thickness':0.15},
        'bgcolor': "white",
        'borderwidth': 2,
        'bordercolor': "gray",
        'steps': [
            {'range': [0, 20], 'color': 'firebrick'},
            {'range': [20, 40], 'color': 'red'},
            {'range': [40, 60], 'color': 'gold'},
            {'range': [60, 80], 'color': 'limegreen'},
            {'range': [80, 100], 'color': 'forestgreen'}],
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': 490}}))

fig.add_annotation(x=0.08,y=0.9,
            text="Bear Market",
            font_size=32)

fig.add_annotation(x=0.92,y=0.9,
            text="Bull Market",
            font_size=32)

fig.update_layout(font = {'color': "#cdafe3", 'family': "monospace"})

st.plotly_chart(fig, use_column_width=True)

top_headlines = newsapi.get_everything(q= str(x),
                                          language='en',)

Articles = top_headlines['articles']
st.header("Featured Articles")
st.subheader(f"[{str(Articles[0]['title'])}]({str(Articles[0]['url'])})")
st.markdown(str(Articles[0]['description']))
st.subheader(f"[{str(Articles[1]['title'])}]({str(Articles[1]['url'])})")
st.markdown(str(Articles[1]['description']))
st.subheader(f"[{str(Articles[2]['title'])}]({str(Articles[2]['url'])})")
st.markdown(str(Articles[2]['description']))
st.subheader(f"[{str(Articles[3]['title'])}]({str(Articles[3]['url'])})")
st.markdown(str(Articles[3]['description']))
st.subheader(f"[{str(Articles[4]['title'])}]({str(Articles[4]['url'])})")
st.markdown(str(Articles[4]['description']))
