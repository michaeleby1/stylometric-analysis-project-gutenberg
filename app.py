import pandas as pd 
import streamlit as st 
import utils

st.header('Book Search')
# st.subheader('Enter a book title to see its style metrics')

df = pd.read_csv('metrics_clusters.csv')
# st.dataframe(df[['title', 'author', 'year']].style.hide_index())

path = st.text_input('Enter title:', '')
if path:
    # try:
    input_title, input_metrics, closest = utils.book_lookup(path)
    st.sidebar.dataframe(input_title.T.rename(columns={input_title.index[0]: ''}))

    st.markdown(' ')

    st.markdown('\n\n\n\n\n\n\n **Style metrics:**')
    st.dataframe(input_metrics.set_index(pd.Index([''])), height=1000)

    st.markdown(' ')
    st.markdown('\n\n **Most stylistically similar titles:**')

    st.table(closest.set_index(pd.Index(list(range(1,11)))))

    # except TypeError as e:
    #     st.write(f'{path} is not in Project Gutenberg.')