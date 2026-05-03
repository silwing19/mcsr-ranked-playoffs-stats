import streamlit as st
from st_social_media_links import SocialMediaIcons

social_media_links = [
    "https://x.com/silwing19",
    "https://github.com/silwing19",
]

social_media_icons = SocialMediaIcons(social_media_links)

def make_sidebar():
    with st.sidebar:
        st.html(
            """<style> 
                .player-link { 
                    text-decoration: none !important; 
                    color: #30e685 !important; 
                    transition: color 0.2s ease, 
                    transform 0.1s ease !important; 
                } 
                .player-link:hover { 
                    color: #F7DC6F !important; 
                    transform: scale(1.05) !important; 
                    font-weight: bold !important 
                } """, 
            )
        st.markdown('## <a href="/" target="_self" class="player-link">mcsr ranked playoffs stats</a>', unsafe_allow_html=True)
        st.markdown('<span style="font-size:0.9em">this is a compilation of stats related to the mcsr ranked playoffs. i hope you enjoy poking around, and share this with anyone you think would be interested!</span>', unsafe_allow_html=True)
        with st.container(
            horizontal=True,
            horizontal_alignment='center'
        ):
            if st.button("home"):
                st.switch_page("main.py")
            if st.button("players"):
                st.switch_page("pages/player.py")
            if st.button("seasons"):
                st.switch_page("pages/season.py")
            if st.button("matches"):
                st.switch_page("pages/match.py")
        st.markdown("<span style='font-size:0.9em'>i'll try to update this as matches happen (at least within the day, hopefully). if i've updated it and you still can't see the changes, try this button</span>", unsafe_allow_html=True)
        with st.container(
            horizontal=True,
            horizontal_alignment='center'
        ):
            if st.button("refresh data"):
                st.cache_data.clear()
        st.markdown('<span style="font-size:0.9em">sample sizes are small for a lot of players, so interpret everything with caution.</span>', unsafe_allow_html=True)
        st.markdown('<span style="font-size:0.9em">stats don\'t tell the whole story, so please be nice + don\'t take it too seriously!</span>', unsafe_allow_html=True)
        social_media_icons.render()
        
