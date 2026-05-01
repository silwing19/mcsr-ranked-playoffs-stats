# imports
import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from utils import filters
from utils import sidebar

st.set_page_config(layout="wide")

data = filters.load_data()[0]

params = st.query_params
game = params.get("game")
season = params.get("season")
round = params.get("round")

df = data.copy()

with st.container(
        border=True,
        width='stretch',
        #height='stretch',
    ):
    select1, select2, select3 = st.columns([0.2, 0.4, 0.4])

    # season selection ----------------------------------------------------------------------------

    seasons = sorted(df['season'].unique())
    default_season = int(season) if season else st.session_state.get("selected_season", seasons[0])
    season = select1.selectbox(
        "season",
        seasons,
        index=seasons.index(default_season)
    )
    df = df[df['season'] == season]

    # round selection ----------------------------------------------------------------------------------

    df = filters.add_round(df)
    order = ['round 1', 'round 2', 'round of 16', 'quarterfinals', 'semifinals', 'third place match', 'grand finals']
    rounds = [r for r in order if r in df['round'].unique()]
    round = round if round in rounds else ""
    default_round = round if round != "" else st.session_state.get("selected_round", rounds[0])
    round = select2.selectbox(
        "round",
        rounds,
        index=rounds.index(default_round)
    )
    df = df[df['round'] == round]

    # game selection -------------------------------------------------------------------------------------

    df = df.sort_values(by = "match")
    df = df.assign(seed=df['match'].str.split(".").str[1])
    df = df.assign(match=df['match'].str.split(".").str[0])
    matches = df['match'].unique()
    games = []
    for match in matches:
        players = sorted(df.loc[df['match'] == match, 'player'].unique())
        players = players[0] + " vs " + players[1]
        games.append(players)
    game = game if game in games else ""
    default_match = game if game != "" else st.session_state.get("selected_match", games[0])
    game = select3.selectbox(
        "match",
        games,
        index=games.index(default_match)
    )
    player1 = game.split(" ")[0]
    player2 = game.split(" vs ")[1]

df = df[(df['player'] == player1) | (df['player'] == player2)]

# st.query_params.update({
#     "season": season,
#     "round": round,
#     "game": game
# })

st.markdown("""
    <style>
    .player-link {
        text-decoration: none !important;
        color: inherit !important;
        transition: color 0.2s ease, transform 0.1s ease !important;
    }
    .player-link:hover {
        color: #00c15a !important;
        transform: scale(1.05) !important;
    }
""", unsafe_allow_html=True)

sidebar.make_sidebar()
st.set_page_config(layout="wide", page_title="mcsr ranked playoffs stats - " + player1 + " vs " + player2)
st.markdown(f"""# <a href="/player?player={player1}" target="_self" class="player-link">{player1}</a> vs <a href="/player?player={player2}" target="_self" class="player-link">{player2}</a>""", unsafe_allow_html=True)
winner = df.groupby('player')['finish'].count().idxmax()
num_won = df[df['player'] == winner]['finish'].count()
best_of = 0
if num_won == 4: best_of = 7
elif num_won == 3: best_of = 5
elif (season == 5) & (match == "SF_2"):
    best_of = 5
    winner = "hackingnoises"  # specific correction
elif num_won == 2: best_of = 3

st.markdown(f"""#### season {str(season)} {round} - best of {str(best_of)} | {winner} win""")

# for the y axis of the line plot
avg_overworld = data['overworld'].mean()
avg_to_bastion = avg_overworld + data['terrain to bastion'].mean()
avg_bastion = avg_to_bastion + data['bastion split'].mean()
avg_fort_to_blind = avg_bastion + data['fort to blind'].mean()
avg_blind_to_sh = avg_fort_to_blind + data['blind to stronghold'].mean()
avg_sh = avg_blind_to_sh + data['stronghold nav'].mean()
avg_end = avg_sh + data['end fight'].mean()

df['start'] = 0
df_long = pd.melt(df[['player', 'seed', 'seed_type', 'start', 'nether_enter', 'bastion', 'fortress', 'blind', 'stronghold', 'end_enter', 'finish']], 
                  id_vars=['player', 'seed', 'seed_type'], 
                  var_name='split', 
                  value_name='time')
df_long = df_long.assign(
    avg_split_time=df_long['split'].case_when(
        [(df_long['split'].str.contains("start"), 0),
         (df_long['split'].str.contains("nether_enter"), avg_overworld),
         (df_long['split'].str.contains("bastion"), avg_to_bastion),
         (df_long['split'].str.contains("fortress"), avg_bastion),
         (df_long['split'].str.contains("blind"), avg_fort_to_blind),
         (df_long['split'].str.contains("stronghold"), avg_blind_to_sh),
         (df_long['split'].str.contains("end_enter"), avg_sh),
         (df_long['split'].str.contains("finish"), avg_end)]
    )
)
df_long = df_long.replace({
    'nether_enter': 'enter nether',
    'bastion': 'enter bastion',
    'fortress': 'enter fortress',
    'stronghold': 'enter stronghold',
    'end_enter': 'enter end'
})
for i in df_long['seed'].unique():
    seed_winner = df_long[df_long['seed'] == i]
    d2 = seed_winner.copy()
    seed_winner = seed_winner[seed_winner['split'] == 'finish']
    seed_type = seed_winner['seed_type'].iloc[0]
    seed_winner = seed_winner[seed_winner['time'].isna() == False]['player'].iloc[0]
    with st.container(
        border=True,
        width='stretch',
        #height='stretch',
    ):
        st.markdown(f"""##### seed {i} - {seed_type} | {seed_winner} win""")
        chart = px.line(
            df_long[df_long['seed'] == i].sort_values(['player']),
            x="time",
            y="avg_split_time",
            color="player",
            hover_data=["player", "split"],
            markers=True,
            color_discrete_map={player1: '#5499C7', player2: '#F7DC6F'}
        )
        chart.update_layout(
            height=365,
            #width=500
        )
        chart.update_layout(yaxis_title=None)
        chart.update_yaxes(showticklabels=False)
        chart.update_layout(
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.7, # Adjust this value (negative) to move lower
                xanchor="center",
                x=0.3
            )
        )
        chart.add_shape(
            type="line",
            x0=df_long[df_long['seed'] == i]["time"].min(),
            y0=df_long[df_long['seed'] == i]["time"].min(),
            x1=df_long[df_long['seed'] == i]["time"].max(),
            y1=df_long[df_long['seed'] == i]["time"].max(),
            line=dict(color="#7BF1A8", dash="dash", width=1),
        )
        col1, col2, col3 = st.columns([0.3, 0.3, 0.4])
        with col1:
            st.write("(green dashed line is average pace)")
            st.plotly_chart(chart)
        with col2:
            df = df.rename(columns={'nether_enter':'enter nether', 'bastion':'enter bastion', 'fortress':'enter fortress', 'stronghold':'enter stronghold', 'end_enter':'enter end'})
            d = df[['player', 'seed', 'enter nether', 'enter bastion', 'enter fortress', 'blind', 'enter stronghold', 'enter end', 'finish']]
            d = d.set_index('player')
            d = d[d['seed'] == i].sort_values('player').drop(columns='seed').T

            def highlight_row(row):
                if pd.isna(row[player1]) or pd.isna(row[player2]):
                    return ['', '']

                if row[player1] < row[player2]:
                    return ['color: #58D68D', 'color: #EC7063']
                elif row[player1] > row[player2]:
                    return ['color: #EC7063', 'color: #58D68D']
                else:
                    return ['color: gray', 'color: gray']

            styled = (d.style.apply(highlight_row, axis=1).format(lambda x: str(datetime.timedelta(seconds=int(x)))[2:] if pd.notna(x) else ""))

            st.write('splits')
            st.dataframe(styled)
        with col3:
            compareto = st.pills("split lengths compared to: ", ['all times', 'same season', 'same player'], default='all times', selection_mode='single', key = i)
            if not compareto: st.warning("choose an option")
            else:
                forspider = pd.melt(df[['player', 'seed', 'overworld', 'terrain to bastion', 'bastion split', 'fort to blind', 'blind to stronghold', 'stronghold nav', 'end fight', 'finish']], 
                    id_vars=['player', 'seed'], 
                    var_name='split', 
                    value_name='time')
                forspider = forspider[forspider['seed'] == i]
                if compareto == 'all times': player1_df, player2_df = filters.seed_percentiles(data, forspider)
                elif compareto == 'same player': player1_df, player2_df = filters.seed_percentiles(data, forspider, byplayer=True)
                else: player1_df, player2_df = filters.seed_percentiles(data, forspider, season=season)
                player1_df['player'] = forspider['player'].sort_values().unique()[0]
                player2_df['player'] = forspider['player'].sort_values().unique()[1]
                df_combined = pd.concat([player1_df, player2_df], ignore_index=True)
                fig = px.line_polar(df_combined, r='percentile', theta='split', color='player', line_close=True, height=300, color_discrete_map={player1: '#5499C7', player2: '#F7DC6F'})
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', polar=dict(bgcolor='rgba(0,0,0,0)'))
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            showgrid=True,
                            gridcolor='rgba(150,150,150,0.2)',
                            showticklabels=False,
                            range=[0, 100]
                        ),
                        angularaxis=dict(
                            showgrid=True,
                            gridcolor='rgba(150,150,150,0.2)'
                        )
                    )
                )
                fig.update_traces(mode='lines+markers', line=dict(width=2),marker=dict(size=6))
                fig.update_layout(
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.7, # Adjust this value (negative) to move lower
                        xanchor="center",
                        x=0.3
                    )
                )
                st.plotly_chart(fig)