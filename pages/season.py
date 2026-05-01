import streamlit as st
from utils import filters
import plotly.express as px
import pandas as pd
import datetime
from utils import sidebar
import math
import numpy as np

st.set_page_config(layout="wide")

df, placements = filters.load_data()
sidebar.make_sidebar()

# selecting a season
params = st.query_params
season = params.get("season")
if season: season = int(season)
seasons = df.sort_values('season')['season'].unique().tolist()
default_season = season if season else st.session_state.get("selected_season", max(seasons)) 
season = st.pills("choose a season", seasons, selection_mode='single', default = default_season if season else max(seasons))
if not season: 
    st.warning("choose a season")
    #st.set_page_config(layout="wide", page_title="mcsr ranked playoffs stats - " + "season")
else:
    #st.set_page_config(layout="wide", page_title="mcsr ranked playoffs stats - season " + str(season))
    st.title("season " + str(season))
    seeds, col1, col2 = st.columns([0.25, 0.25, 0.5])
    placements = placements[placements['season'] == season]

    st.html("""
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
            """)
    
    # placements ------------------------------------------------------------------------------------------
    with col1:
        with st.container(
            border=True,
            width='stretch',
            height='stretch',
            horizontal=False,
            vertical_alignment='top'
        ):
            st.markdown("""#### final standings""")
            sorted_df = placements.sort_values(['season', 'placement'])

            def medal(p):
                if p == 1: return " 🥇 ", "1em"
                elif p == 2: return " 🥈 ", "1em"
                elif p == 3: return " 🥉 ", "1em"
                else: return f"{p}th", "1em"
            places_list = '\n'.join(
                f'- <div><span style="font-size:{size};display:inline;color:#00c15a;font-weight:bold">{icon}</span>: <span style="font-size:1em;"><a href="/player?player={pl}" target="_self" class="player-link">{pl}</a></span></div>'
                for p, pl in zip(sorted_df['placement'], sorted_df['player'])
                for icon, size in [medal(p)]
            )

            st.markdown(places_list, unsafe_allow_html=True)
            #st.write(" ")

    # seeding ------------------------------------------------------------------------------------
    with seeds:
        with st.container(
            border=True,
            width='stretch',
            height='stretch',
            horizontal=False,
            vertical_alignment='top'
        ):
            st.markdown("""#### seeding""")
            sorted_df = placements.sort_values(['season', 'seed'])

            seeds_list = '\n'.join(
                f'- <div><span style="font-size:1em;display:inline;color:#00c15a;font-weight:bold">{p}</span>: <span style="font-size:1em;"><a href="/player?player={pl}" target="_self" class="player-link">{pl}</a></span></div>'
                for p, pl in zip(sorted_df['seed'], sorted_df['player'])
            )

            st.markdown(seeds_list, unsafe_allow_html=True)
            #st.write(" ")

    # finish times ---------------------------------------------------------------------------------------

    with col2:
        with st.container(
            border=True,
            width='stretch',
            height='stretch',
            horizontal=False,
            vertical_alignment='top'
        ):
            st.markdown("""#### finish times""")
            
            season_stats = df[df['season'] == season]
            average_finish = season_stats['finish'].mean()
            fastest_finish = season_stats['finish'].min()
            fastest_finish_player = season_stats[season_stats['finish'] == fastest_finish]['player'].iloc[0]
            slowest_finish = season_stats['finish'].max()
            slowest_finish_player = season_stats[season_stats['finish'] == slowest_finish]['player'].iloc[0]
            
            st.markdown(f"""  
                * season average finish: <span style="color:#00c15a;"><b>{str(datetime.timedelta(seconds = abs(round(average_finish))))[2:]}</b></span>
                * season fastest finish: <span style="color:#00c15a;"><b>{str(datetime.timedelta(seconds = abs(round(fastest_finish))))[2:]}</b></span> (<span><a href="/player?player={fastest_finish_player}" class="player-link" target="_self">{fastest_finish_player}</a></span>)
                * season slowest finish: <span style="color:#00c15a;"><b>{str(datetime.timedelta(seconds = abs(round(slowest_finish))))[2:]}</b></span> (<span><a href="/player?player={slowest_finish_player}" class="player-link" target="_self">{slowest_finish_player}</a></span>)
            """, unsafe_allow_html=True)
            
            all_times = filters.select_splits(df)
            season_times = filters.select_splits(df, seasons=[season])

            compareto = ['all times'] + ["season " + str(i) for i in seasons if i != season]
            compare_to = st.pills("compare to", compareto, selection_mode='single', default='all times')
            
            if not compare_to: st.warning("choose an option")
            else:
                if compare_to != 'all times': all_times = all_times[all_times['season'] == int(compare_to[-1])]
                if compare_to == 'all times': all_times['season'] = 'all'
                splits_to_plot = pd.concat([season_times, all_times])
                finishes_to_plot = splits_to_plot[splits_to_plot['split'] == 'finish']
    
                finishes_box = px.box(finishes_to_plot, orientation='h', y = 'split', x = "time", color = "season", height = 250, points='all', hover_data=['player', 'time'], color_discrete_sequence=['#00c15a', 'gray'])
                finishes_box.update_xaxes(showgrid=True).update_traces(fillcolor=None, selector=dict(type='box'), pointpos=0, jitter=0.5, marker=dict(opacity=0.3)).update_layout(yaxis_title=None,)
    
                st.plotly_chart(finishes_box)

    # times by split -----------------------------------------------------------------------------------------

    with st.container(
        border=True,
        width='stretch',
        height='stretch',
        horizontal=False,
        vertical_alignment='top'
    ):
        st.markdown("""#### splits""")
        all_times = filters.select_splits(df)
        season_times = filters.select_splits(df, seasons=[season])

        show = st.pills("show", ['average', 'fastest', 'slowest'], selection_mode='single', default='average')
        if not show: st.warning("choose an option")
        else:
            if show == 'average': s = 'mean'
            elif show == 'fastest': s = 'min'
            elif show == 'slowest': s = 'max'
    
            times = df[df['season'] == season]
            cols_to_convert = times.columns.difference(['season', 'player', 'match'])
            times[cols_to_convert] = times[cols_to_convert].apply(pd.to_numeric, errors='coerce')
            times2 = times.select_dtypes(include='number').agg(['mean', 'min', 'max'])
            times2 = times2[['overworld', 'terrain to bastion', 'bastion split', 'fort to blind', 'blind to stronghold','stronghold nav', 'end fight']].T.reset_index()       
            times_list = '\n'.join(
                    f'- season {show} {split} - <span style="display:inline;color:#00c15a;font-weight:bold">{"-" if time < 0 else ""}{str(datetime.timedelta(seconds = abs(round(time))))[2:]}</span> {f'(<a href="/player?player={times[times[split] == time]['player'].iloc[0]}" class="player-link" target="_self">' + times[times[split] == time]['player'].iloc[0] + '</a>)' if show != 'average' else ""}'
                    for split, time in zip(times2['index'], times2[s])
                )
            
            st.markdown(times_list, unsafe_allow_html=True)
        
        compareto2 = ['all times'] + ["season " + str(i) for i in seasons if i != season]
        compare_to2 = st.pills("compare to", compareto2, selection_mode='single', default='all times', key=2)
        if not compare_to2: st.warning("choose an option")
        else:
            if compare_to2 != 'all times': all_times = all_times[all_times['season'] == int(compare_to2[-1])]
            if compare_to2 == 'all times': all_times['season'] = 'all'
            splits_to_plot = pd.concat([season_times, all_times])
            splits_to_plot = splits_to_plot[splits_to_plot['split'] != 'finish']
            times_box = px.box(splits_to_plot, x = 'split', y = "time", color = "season", height = 500, points='all', hover_data=['player', 'time'], color_discrete_sequence=['#00c15a', 'gray'])
            times_box.update_xaxes(showgrid=True).update_traces(fillcolor=None, selector=dict(type='box'), pointpos=0, jitter=0.5, marker=dict(opacity=0.3)).update_layout(xaxis_title=None)  
            st.plotly_chart(times_box)     

    # all matches ---------------------------------------------------------------------------------------------
    col3, col4 = st.columns([0.3, 0.7])

    with col3:
        with st.container(
            border=True,
            width='stretch',
            height='stretch',
            horizontal=False,
            vertical_alignment='top'
        ):
            st.markdown("""#### all matches""")
            
            season_df = df[df['season'] == season]
            season_df['match'] = [m[:-2] for m in season_df['match']]
            season_df = filters.add_round(season_df)

            for round in season_df['round'].sort_values().unique():
                st.markdown(f"""###### <span style="color:#00c15a">{round}</span>""", unsafe_allow_html=True)
                matches = season_df[season_df['round'] == round]
                matches = matches['match'].unique()
                games = []
                for match in matches:
                    players = sorted(season_df.loc[season_df['match'] == match, 'player'].unique())
                    players = players[0] + " vs " + players[1]
                    games.append(players)
                matches_list = '\n'.join(f'- <a href="/match?season={season}&round={round}&game={game}" target="_self" class="player-link">{game}</a>' for game in games)
                st.markdown(matches_list, unsafe_allow_html=True)

    # seed types ------------------------------------------------------------------------------------------

    with col4:
        with st.container(
            border=True,
            width='stretch',
            height='stretch',
            horizontal=False,
            vertical_alignment='top'
        ):
            times = filters.select_splits(df[df['season'] == season])
            splits = times['split'].unique()

            seeds_df = df[df['season'] == season]
        
            st.markdown("""##### seed type frequency""")
            counts = seeds_df.groupby('seed_type').count().reset_index()[['seed_type', 'match']].rename(columns={'match':'count', 'seed_type':'seed type'})
            seed_types_pie = px.pie(counts, values='count', names='seed type', height=300)
            st.plotly_chart(seed_types_pie)

            st.markdown("""##### times by seed type""")
    
            seed_types_by = st.pills('show', list(splits), default = "finish")
            
            if not seed_types_by: st.warning("choose a season")
            else:
                box, t = st.columns([0.6, 0.4])
                
                with box:
                    box_df = df[['player', 'season', 'match', 'seed_type', seed_types_by]].sort_values('seed_type')
                    box_df = box_df[box_df['season'] == season]
                    seed_type_box = px.box(box_df, y = seed_types_by, x = 'seed_type', color = 'seed_type', points='all', hover_data=['player', seed_types_by, 'season', 'match'])
                    seed_type_box.update_xaxes(showgrid=True)
                    seed_type_box.update_traces(fillcolor=None, selector=dict(type='box'))
                    seed_type_box.update_traces(pointpos=0, jitter=0.5, marker=dict(opacity=0.4))
                    seed_type_box.update_layout(showlegend=False)
                    st.plotly_chart(seed_type_box)
    
                with t:
    
                    for seedtype in seeds_df['seed_type'].unique():
                        average_time_st = seeds_df[seeds_df['seed_type'] == seedtype][seed_types_by].mean()
                        fastest_time_st = seeds_df[seeds_df['seed_type'] == seedtype][seed_types_by].min()
                        slowest_time_st = seeds_df[seeds_df['seed_type'] == seedtype][seed_types_by].max()
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
