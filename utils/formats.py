import streamlit as st

def placements_block(player, placement):
    if placement == "1st":
        display = "🥇"
        font_size = "1.8rem"
    elif placement == "2nd":
        display = "🥈"
        font_size = "1.8rem"
    elif placement == "3rd":
        display = "🥉"
        font_size = "1.8rem"
    else:
        display = placement
        font_size = "1.2rem"
    st.markdown(
        f"""
        <style>
            .player-link {{
                text-decoration: none !important;
                color: inherit !important;
                transition: color 0.2s ease, transform 0.1s ease !important;
            }}
            .player-link:hover {{
                color: #00c15a !important;
                transform: scale(1.05) !important;
            }}
        </style>
        <div style="
            height:60px;
            padding:0px;
            padding-right:0px;
            padding-left:0px;
            padding-bottom:20px;
            border-radius:1px;
            text-align:center;
            line-height: 1.1;
            display:flex;
            flex-direction:column;
            justify-content:flex-end;
        ">
            <div style="font-size:{font_size};color:#00c15a;font-weight:bold">{display}</div>
            <div style="font-size:0.95rem;"><a href="/player?player={player}" target="_self" class="player-link">{player}</a></div>
        </div>
        """,
        unsafe_allow_html=True
    )

def placement_card(season, placement):
    if placement == "1st":
        display = "🥇"
        font_size = "2rem"
    elif placement == "2nd":
        display = "🥈"
        font_size = "2rem"
    elif placement == "3rd":
        display = "🥉"
        font_size = "2rem"
    else:
        display = placement
        font_size = "1.5rem"
    st.markdown(
        f"""
        <style>
            .season-link {{
                text-decoration: none !important;
                color: inherit !important;
                transition: color 0.2s ease, transform 0.1s ease !important;
            }}
            .season-link:hover {{
                color: #00c15a !important;
                transform: scale(1.05) !important;
            }}
        </style>
        <div style="
            padding:14px;
            padding-right:0;
            padding-left:0;
            border-radius:1px;
            text-align:center;
            line-height: 1.1;
        ">
            <div style="font-size:1rem;"><a href="/season?season={int(season[7:])}" target="_self" class="season-link">{season}</a></div>
            <div style="font-size:{font_size}; color: #00c15a; font-weight:bold">{display}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def stat_card(title=None, value=None, subtitle=None, subtitle2=None):
    st.html("""
        <style>
        .card-link {
            text-decoration: none !important;
            color: inherit !important;
        }

        .card-link:hover {
            color: #2ecc71 !important;  /* green on hover */
            cursor: pointer !important;
        }
        </style>
        """)
    st.markdown(
        f"""
        <div style="
            padding:10px;
            padding-right:20px;
            padding-left:20px;
            padding-bottom:20px;
            border-radius:1px;
            text-align:center;
            border:1px;
            line-height: 1.1;
        ">
            <div style="font-size:1rem;">{title or ""}</div>
            <div style="font-size:1.2rem; font-weight:bold;">{value or ""}</div>
            <div style="font-size:0.8rem;">{subtitle or ""}</div>
            <div style="font-size:0.9rem;">{subtitle2 or ""}</div>
        </div>
        """,
        unsafe_allow_html=True
    )