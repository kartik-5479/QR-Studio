import streamlit as st


def render_card(title, body):
    with st.container(border=True):
        st.subheader(title)
        st.write(body)
