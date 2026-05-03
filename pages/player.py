import streamlit as st
from utils import filters
from utils import formats
import plotly.express as px
import pandas as pd
import datetime
from utils import sidebar
import numpy as np
import math

df, placements = filters.load_data()

# selecting a player
params = st.query_params
player = params.get("player")
players = placements.sort_values('player')['player'].unique().tolist()
default_player = player if player else st.session_state.get("selected_player", players[0])
player = st.selectbox(
    "choose a player",
    players,
    index=players.index(default_player),
)
st.set_page_config(layout="wide", page_title="mcsr ranked playoffs stats")
st.title(player)

sidebar.make_sidebar()

# top section with each season and placement ------------------------------------------------------------
player_placements = placements[placements['player'] == player]
with st.container(
    #border=True,
    width='stretch',
    height='stretch',
    horizontal=True,
    horizontal_alignment='left'
):
    for season in player_placements['season'].sort_values(): 
        placement = filters.ordinal(player_placements[player_placements['season'] == season]['placement'].iloc[0])
        season = "season " + str(season)
        formats.placement_card(season, placement)

st.markdown(
        """<style> 
            .player-link { 
                text-decoration: none !important; 
                color: #30e685 !important; 
                transition: color 0.2s ease, 
                transform 0.1s ease !important; 
            } 
            .player-link:hover { 
                color: #D8F999 !important; 
                transform: scale(1.05) !important; 
                font-weight: bold !important 
            } """, 
        unsafe_allow_html=True)

# second section with stats and the comparison to other players ------------------------------------------------

if player not in df['players'].unique():
    st.write("coming soon!")

else:
    stats, comparison = st.columns([0.5, 0.5])

    with stats:
        with st.container(
            border=True,
            width='stretch',
            height='stretch',
            horizontal_alignment='left',
            vertical_alignment='top'
        ):
            st.markdown("""#### stats""", help="compared to all other players")
            # second section with individual stats --------------------------------------------------------------------------------

            # average time
            average_times = filters.average_time(df.rename(columns={'finish':'time'})).reset_index()
            average_times = average_times[average_times['player'] == player]
            player_avgtime = average_times['average_time'].iloc[0] if player in average_times['player'].values else np.nan
            avgtime_percentile = ((100 * average_times['average_time_percentile'].iloc[0]) if pd.isna(player_avgtime) == False else 100) if player in average_times['player'].values else 100

            # fastest time
            fastest_times = filters.fastest_time(df.rename(columns={'finish':'time'})).reset_index()
            fastest_times = fastest_times[fastest_times['player'] == player]
            player_fastest_time = fastest_times['fastest_time'].iloc[0] if player in fastest_times['player'].values else np.nan
            fastest_time_percentile = ((100 * fastest_times['fastest_time_percentile'].iloc[0]) if pd.isna(player_fastest_time) == False else 100) if player in fastest_times['player'].values else 100

            # seeds played
            seeds_played = filters.winrate(df)
            seeds_played = seeds_played[seeds_played['player'] == player]
            player_seeds_played = seeds_played['played'].iloc[0]
            seeds_played_percentile = 100 - (100 * seeds_played['played_percentile'].iloc[0]) if pd.isna(player_seeds_played) == False else 100

            # seeds won
            player_seeds_won = seeds_played['won'].iloc[0]
            seeds_won_percentile = 100 - (100 * seeds_played['won_percentile'].iloc[0]) if pd.isna(player_seeds_played) == False else 100

            # by seed winrate
            player_winrate = seeds_played['winrate'].iloc[0]
            winrate_percentile = 100 - (100 * seeds_played['winrate_percentile'].iloc[0]) if pd.isna(player_seeds_played) == False else 100

            # average placement
            avg_placements = filters.playoffsplacements(placements)
            player_avg_placement = avg_placements[avg_placements['player'] == player]['average_placement'].iloc[0]
            avg_placement_percentile = avg_placements[avg_placements['player'] == player]['average_placement_percentile'].iloc[0] * 100

            with st.container(
                #border=True,
                width='stretch',
                #height='stretch',
                horizontal_alignment='left',
                vertical_alignment='center'
            ):
                with st.container(
                    #border=True,
                    width='stretch',
                    #height='stretch',
                    horizontal=True,
                    horizontal_alignment='center',
                    vertical_alignment='center'
                ):
                    formats.stat_card("average time", str(datetime.timedelta(seconds=round(player_avgtime)))[2:] if pd.isna(player_avgtime) == False else "N/A", "top " + str(round(avgtime_percentile, 2)) + "%")
                    formats.stat_card("fastest time", str(datetime.timedelta(seconds=round(player_fastest_time)))[2:] if pd.isna(player_fastest_time) == False else "N/A", "top " + str(round(fastest_time_percentile, 2)) + "%")
                    formats.stat_card("seeds played", str(player_seeds_played), "top " + str(round(seeds_played_percentile, 2)) + "%")
                    formats.stat_card("seeds won", str(player_seeds_won), "top " + str(round(seeds_won_percentile, 2)) + "%")
                    formats.stat_card("win rate", str(round((player_winrate * 100), 2)) + "%", "top " + str(round(winrate_percentile, 2)) + "%")
                    formats.stat_card("average placement", str(round(player_avg_placement, 2)), "top " + str(round(avg_placement_percentile, 2)) + "%")
                st.write(" ")
                st.write(" ")
        
        with st.container(
            border=True,
            width='stretch',
            height='stretch',
            horizontal_alignment='left',
            vertical_alignment='top'
        ):
            st.markdown("""#### seeding and placements""")
            placements2 = placements[placements['player'] == player]
            st.dataframe(placements2[['player', 'season', 'seed', 'placement']], height = 150)

    with comparison:
        with st.container(
            border=True,
            width='stretch',
            height='stretch',
        ):
            st.markdown("""#### split percentiles""")
            season_toinclude = st.pills("include seasons:", ["all"] + list(df[df['player'] == player]['season'].unique().sort_values()), default = "all", help="all compares all this player's times to all times over all seasons, if you choose a season it compares this player's times in that season to the other times in that season")
            if not season_toinclude: st.warning("choose an option")
            else: 
                d = df.copy()
                if season_toinclude != "all":
                    d = d[d['season'] == season_toinclude]
                d = filters.split_percentiles(d, player)
                fig = px.line_polar(d, r='percentile', theta='split', line_close=True, height=300)
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
                fig.update_traces(mode='lines+markers', line=dict(color="#00c15a", width=2),marker=dict(color='#00c15a', size=6))
                st.plotly_chart(fig)

    # third section with times -------------------------------------------------------------------------------------------
    with st.container(
        border=True,
        width='stretch',
        height='stretch',
    ):
        st.markdown("""#### times""")
        times = filters.select_splits(filters.filter_players(df, [player]))

        # filter by split (default is finish time)
        selected_split = st.pills("split: ", times['split'].unique(), default = "finish", selection_mode = "single")
        if not selected_split: st.warning("choose a split")
        else:
            times = times[times['split'] == selected_split]
        
            # boxplot for times not sorted by season
            overall_boxplot = px.box(times, y = "time", height = 350, points='all', hover_data=['player', 'time', 'season', 'match'])
            overall_boxplot.update_xaxes(showgrid=True).update_traces(fillcolor=None, selector=dict(type='box'), marker=dict(color='white', opacity=0.2), pointpos=0, jitter=0.5)
        
            # boxplot for times by season
            seasons_boxplot = px.box(times, y = "time", x = 'season', color = 'season', height = 350, points='all', hover_data=['player', 'time', 'season', 'match'])
            seasons_boxplot.update_xaxes(showgrid=True).update_traces(fillcolor=None, selector=dict(type='box'), pointpos=0, jitter=0.5, marker=dict(opacity=0.4))
        
            # for the spider plot comparing to all players
        
            # put all the plots on the page
            col1, col2 = st.columns([0.2, 0.8])
            with col1:
                st.markdown("""###### all times""")
                st.plotly_chart(overall_boxplot)
            with col2:
                st.markdown("""###### times by season""")
                st.plotly_chart(seasons_boxplot) 
            with st.container():
                st.markdown("""###### times""")
                t = (times[times['time'].isna() == False].sort_values('time', ascending=True)[['season', 'match', 'split', 'time']])
                t['time'] = [("-" if time < 0 else "") + str(datetime.timedelta(seconds = abs(time)))[2:] for time in t['time']]
                t = filters.add_round(t)
                t["seed"] = [s[-1:] for s in t['match']]
                t = t[['season', 'round', 'seed', 'time']]
                t.columns = ['season', 'round', 'seed', selected_split]
                st.dataframe(t, height = 150)

    with st.container(
        border=True,
        width='stretch',
        height='stretch',
    ):
        st.markdown("""#### win rate""")

        # allows you to pick whether to look at win rate by series or by seed (default is by seed)
        wr_by = st.pills("by", ['seed', 'series'], selection_mode ='single', default = 'seed')
        if not wr_by: st.warning("choose an option")
        else:

            winrate_df = filters.winrate(df, by = wr_by)
            winrate_df = winrate_df[winrate_df['player'] == player]
            winrate_df = winrate_df[['won', 'lost']].T.reset_index()
            winrate_df.columns = ['result', 'count']
        
            winrate_df2 = filters.winrate(df, by = wr_by, byseason=True)
            winrate_df2 = winrate_df2[winrate_df2['player'] == player]
            winrate_df2 = winrate_df2[['season', 'won', 'lost']]
            winrate_df2 = winrate_df2.melt('season')
            winrate_df2.columns = ['season', 'result', 'count']
        
            # winrate pie chart
            winrate_pie = px.pie(
                winrate_df,
                names='result',
                values='count',
                height=300,
                color='result',
                color_discrete_map={
                    'won': '#05DF72',
                    'lost': '#FF6467'
                },
            )
            winrate_pie.update_traces(textinfo='percent+label')
        
            # winrate by seasons bar chart 
            winrate_bar = px.bar(
                winrate_df2,
                x='season',
                y='count',
                color='result',
                height=300,
                range_y = [0, 5] if wr_by == 'series' else None,
                color_discrete_map={
                    'won': '#05DF72',
                    'lost': '#FF6467'
                },
            )
            
            # put the winrate section on the page
            col5, col6 = st.columns([0.4, 0.6])
            with col5:
                st.markdown("""###### overall""")
                st.plotly_chart(winrate_pie)
            with col6:
                st.markdown("""###### by season""")
                st.plotly_chart(winrate_bar)

    styled_df = filters.get_series(df, player)[['season', 'round', 'player', 'winner']]
    styled_df['player'] = styled_df['player'].apply(
        lambda players: next((p for p in players if p != player), None)
    )

    with st.container(
        border=True,
        width='stretch',
        height='stretch'
        ):
        st.markdown("""#### seed types""")
        pie, box = st.columns([0.45, 0.55])
        times = filters.select_splits(filters.filter_players(df, [player]))
        splits = times['split'].unique()

        df = df[df['player'] == player]
        c, t = st.columns(2)

        with c:
            st.markdown("""##### seed type frequency""")
            counts = df.groupby('seed_type').count().reset_index()[['seed_type', 'match']].rename(columns={'match':'count', 'seed_type':'seed type'})
            seed_types_pie = px.pie(counts, values='count', names='seed type', height=350)
            seed_types_pie.update_layout(
                legend=dict(orientation="h", yanchor="bottom", y=-0.8, xanchor="center", x=0.5)
            )
            st.plotly_chart(seed_types_pie)
        
        with t:
            st.markdown("""##### seed type fequency per season""")
            seedtype_counts_byseason = df.groupby(['seed_type', 'season']).count().reset_index()[['seed_type', 'season', 'match']].rename(columns={'match':'count', 'seed_type':'seed type'})
            percents = st.checkbox('show as percent of all seeds played', False)
            
            if percents:
                seedtype_counts_byseason['percent'] = (
                    seedtype_counts_byseason['count'] /
                    seedtype_counts_byseason.groupby('season')['count'].transform('sum')
                ) * 100
                y_col = 'percent'
            else:  y_col = 'count'

            seedtype_bar = px.bar(
                seedtype_counts_byseason,
                x='season',
                y=y_col,
                color='seed type',
                height=300,
            )
            seedtype_bar.update_layout(
                legend=dict(orientation="h", yanchor="bottom", y=-0.8, xanchor="center", x=0.5)
            )
            st.plotly_chart(seedtype_bar)
        
        st.markdown(
            """<style> 
                .player-link { 
                    text-decoration: none !important; 
                    color: #30e685 !important; 
                    transition: color 0.2s ease, 
                    transform 0.1s ease !important; 
                } 
                .player-link:hover { 
                    color: #D8F999 !important; 
                    transform: scale(1.05) !important; 
                    font-weight: bold !important 
                } """, 
            unsafe_allow_html=True)
        st.markdown("""##### times by seed type""")
        seed_types_by = st.pills('show', list(splits), default = "finish")
        if not seed_types_by: st.warning("choose an option")
        else:
            box, t = st.columns([0.6, 0.4])
            with box:
                box_df = df[['player', 'season', 'match', 'seed_type', seed_types_by]].sort_values('seed_type')
                seed_type_box = px.box(box_df, y = seed_types_by, x = 'seed_type', color = 'seed_type', points='all', hover_data=['player', seed_types_by, 'season', 'match'])
                seed_type_box.update_xaxes(showgrid=True)
                seed_type_box.update_traces(fillcolor=None, selector=dict(type='box'))
                seed_type_box.update_traces(pointpos=0, jitter=0.5, marker=dict(opacity=0.4))
                seed_type_box.update_layout(showlegend=False)
                st.plotly_chart(seed_type_box)
        
            with t:
        
                for seedtype in df['seed_type'].unique():
                    average_time_st = df[df['seed_type'] == seedtype][seed_types_by].mean()
                    fastest_time_st = df[df['seed_type'] == seedtype][seed_types_by].min()
                    slowest_time_st = df[df['seed_type'] == seedtype][seed_types_by].max()
                    if not math.isnan(fastest_time_st):
                        if fastest_time_st < 0:
                            fastest_time_st = "-" + str(datetime.timedelta(seconds = abs(fastest_time_st)))[2:]
                        else: fastest_time_st = str(datetime.timedelta(seconds = abs(fastest_time_st)))[2:]
                    else: fastest_time_st = "N/A"
                    
                    if not math.isnan(slowest_time_st): slowest_time_st = str(datetime.timedelta(seconds = abs(slowest_time_st)))[2:]
                    else: slowest_time_st = "N/A"
                    
                    if not math.isnan(average_time_st): average_time_st = str(datetime.timedelta(seconds = np.round(average_time_st)))[2:]
                    else: average_time_st = "N/A"
        
                    st.markdown(f'<span style="color:#00c15a;font-weight:bold">{seedtype}</span> \n - average <span style="font-weight:bold">{seed_types_by}</span>: <span style="color:#00c15a;font-weight:bold">{average_time_st}</span>\n - fastest <span style="font-weight:bold">{seed_types_by}</span>: <span style="color:#00c15a;font-weight:bold">{fastest_time_st}</span> \n - slowest <span style="font-weight:bold">{seed_types_by}</span>: <span style="color:#00c15a;font-weight:bold">{slowest_time_st}</span>', unsafe_allow_html=True)

        # st.markdown("""##### seed types by season""")
        # seedtype2 = st.pills("seed type", df['seed_type'].unique(), key = 6, default = "ruined portal")
        # seed_types_by2 = st.pills('show', list(splits), key = 7, default = 'finish')
        # seedtypes_byseason = df[['player', 'season', 'match', 'seed_type', seed_types_by2]].sort_values('seed_type')
        # seedtypes_byseason = seedtypes_byseason[seedtypes_byseason['seed_type'] == seedtype2].sort_values('season')
        # seed_type_box = px.box(seedtypes_byseason, y = seed_types_by2, x = 'season', title = seedtype2 + " " + seed_types_by2 + " times per season", color = 'season', height = 400, points='all', hover_data=['player', seed_types_by2, 'season', 'match'])
        # seed_type_box.update_xaxes(showgrid=True)
        # seed_type_box.update_traces(fillcolor=None, selector=dict(type='box'))
        # seed_type_box.update_traces(pointpos=0, jitter=0.5, marker=dict(opacity=0.4))
        # seed_type_box.update_layout(showlegend=False)
        # st.plotly_chart(seed_type_box)

    with st.container(
        border=True,
        width='stretch',
        height='stretch'
        ):
        st.markdown("#### all matches")

        seasons = df[df['player'] == player]['season'].sort_values().unique()

        for season in seasons:
            filtered_df = styled_df[styled_df['season'] == season]

            with st.expander(f"season {season}", expanded=False):
                for round, opponent in zip(filtered_df['round'], filtered_df['player']):
                    players = sorted([player, opponent])
                    st.markdown(f'<div style="margin:3px 0;">' f'- <a href="/match?season={season}&round={round}&game={players[0] + " vs " + players[1]}" class="player-link" target="_self">{round}</a> vs ' f'<a href="/player?player={opponent}" class="player-link" target="_self">{opponent}</a>' f'</div>', unsafe_allow_html=True)
                st.write(" ")
