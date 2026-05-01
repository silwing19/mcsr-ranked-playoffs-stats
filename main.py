import streamlit as st
from utils import filters
from utils import adjustments
import plotly.express as px
import datetime
from utils import sidebar
import pandas as pd

st.set_page_config(layout="wide", page_title="mcsr ranked playoffs stats")

df, placements = filters.load_data()

st.title("mcsr ranked playoffs stats")
sidebar.make_sidebar()

# add at the top quick stats - number of seeds played total, overall average time, overall fastest time, number of seasons, number of players total

# seasons played ---------------------------------------------------------------------------------------------

col1, col2 = st.columns([0.5, 0.5])

seasons_placements = filters.playoffsplacements(placements).groupby('playoffs_played').count().rename(columns = {"playoffs_played": "playoffs played", "average_placement":"number of players"}).reset_index()
seasons_pie = px.pie(seasons_placements, values='number of players', names='playoffs_played', height=300)

playoffs_played_df = filters.playoffsplacements(placements).reset_index()[['player', 'playoffs_played']].sort_values('playoffs_played', ascending=False).reset_index(drop=True)
most_seasons_player = playoffs_played_df[playoffs_played_df['playoffs_played'] == max(playoffs_played_df['playoffs_played'])]['player'].iloc[0]
most_seasons_played = playoffs_played_df[playoffs_played_df['playoffs_played'] == max(playoffs_played_df['playoffs_played'])]['playoffs_played'].iloc[0]

players_in_multiple_seasons = len(playoffs_played_df[playoffs_played_df['playoffs_played'] > 1])
players_in_one_season = len(playoffs_played_df[playoffs_played_df['playoffs_played'] == 1])
total_players = len(playoffs_played_df)

with col1:
    with st.container(
        border=True,
            width='stretch',
            height='stretch'
    ):
        st.markdown("""#### seasons played per player""", help="number of seasons played by each player. on the pie chart, each color is a number of seasons and the size is the number of players who've played in that many seasons")
        st.markdown(f"""
            * number of unique playoffs participants: <span style="color:#00c15a;"><b>{total_players}</b></span>  
            * number of players who played one season: <span style="color:#00c15a;"><b>{players_in_one_season}</b></span>  
            * number of players who played multiple seasons: <span style="color:#00c15a;"><b>{players_in_multiple_seasons}</b></span>  
            * most seasons played: <span style="color:#00c15a;"><b>{most_seasons_player}</b></span> (<span style="color:#00c15a;">{most_seasons_played}</span> seasons)
            """, unsafe_allow_html=True)
        st.plotly_chart(seasons_pie)
        st.dataframe(playoffs_played_df.rename(columns={'playoffs_played':'number of seasons played'}), height=150)

# seeding -----------------------------------------------------------------------------------------

with col2:
    with st.container(
        border=True,
        width='stretch',
        height='stretch'
    ):
        st.markdown("""#### average seed per player""", help="each player's average seed going into all seasons they've played in. seeds are on a 1-16 scale")
        adjust_for_seasons = st.checkbox('adjust for number of seasons played', help="adjusts for the number of seasons played to keep players with very few seasons from having skewed results. makes the rankings in the table more robust, but the actual number loses interpretability", key = 21)
        
        seasons_placements = filters.playoffsplacements(placements, adjust=True if adjust_for_seasons else False)
        avg_seed_player = seasons_placements[seasons_placements['average_seed'] == min(seasons_placements['average_seed'])]['player'].iloc[0]
        avg_seed_avg = round(seasons_placements[seasons_placements['average_seed'] == min(seasons_placements['average_seed'])]['average_seed'].iloc[0], 2)
        
        st.markdown(f"""  
            * top average seed: <span style="color:#00c15a;"><b>{avg_seed_player}</b></span> (<span style="color:#00c15a;">{avg_seed_avg}</span> {'adjusted' if adjust_for_seasons else ''} average seed)
            """, unsafe_allow_html=True)
        fig = px.box(
            seasons_placements.rename(columns={'average_seed':'average seed'}).reset_index(drop=True),
            x="average seed",
            height=220, points="all", hover_data=['player', 'average seed']
        )
        fig.update_xaxes(showgrid=True)
        fig.update_traces(fillcolor=None, selector=dict(type='box'),marker=dict(opacity=0.4, color='white'))
        fig.update_traces(pointpos=0, jitter=1)
        st.plotly_chart(fig)
        st.dataframe(seasons_placements.reset_index(drop=True)[['player', 'average_seed']].rename(columns={'average_seed': 'average seed'}).sort_values('average seed', ascending=True).reset_index(drop=True), height = 260)

# average placements -------------------------------------------------------------------------------------------

place, comparison = st.columns([0.5, 0.5])

with place:
    with st.container(
        border=True,
        width='stretch',
        height='stretch'
    ):
        st.markdown("""#### average placement per player""", help="each player's average placement across all seasons they've played in. placements are on a 1-6 scale for most seasons and a 1-7 scale for seasons 5 and 6 (this is different from the ranked website to make it so lower placements don't skew averages as much)")
        
        adjust_placements = st.checkbox('put all seasons on a 1-6 scale', help="seasons 5 and 6 are on a 1-7 scale because of differences in the bracket structure; this adjustment keeps all the seasons on the 1-6 scale so players who came last in season 5 or 6 aren't lower that ones who came last in the other seasons", key = 24)
        adjust_for_seasons = st.checkbox('adjust for number of seasons played', help="adjusts for the number of seasons played to keep players with very few seasons from having skewed results. makes the rankings in the table more robust, but the actual number loses interpretability", key = 22)
        
        seasons_placements = filters.playoffsplacements(placements, rescale=True if adjust_placements else False, adjust=True if adjust_for_seasons else False)
        avg_placement_player = seasons_placements[seasons_placements['average_placement'] == min(seasons_placements['average_placement'])]['player'].iloc[0]
        avg_placement_avg = round(seasons_placements[seasons_placements['average_placement'] == min(seasons_placements['average_placement'])]['average_placement'].iloc[0], 2)
        
        st.markdown(f"""  
            * top average placement: <span style="color:#00c15a;"><b>{avg_placement_player}</b></span> (<span style="color:#00c15a;">{avg_placement_avg}</span> {'adjusted' if adjust_for_seasons else ''} average placement)
            """, unsafe_allow_html=True)
        fig = px.box(
            seasons_placements.rename(columns={'average_placement':'average placement'}).reset_index(drop=True),
            x="average placement",
            height=250, points="all", hover_data=['player', 'average placement']
        )
        fig.update_xaxes(showgrid=True)
        fig.update_traces(fillcolor=None, selector=dict(type='box'),marker=dict(opacity=0.4, color='white'))
        fig.update_traces(pointpos=0, jitter=1)
        st.plotly_chart(fig)
        st.dataframe(seasons_placements.reset_index()[['player', 'average_placement']].rename(columns={'average_placement': 'average placement'}).sort_values('average placement', ascending=True).reset_index(drop=True), height = 150)

with comparison:
    with st.container(
        border=True,
        width='stretch',
        height='stretch'
    ):
        st.markdown("""#### placement by seed""", help="compares placement by seed for each player/season to see whether higher seeds correlate with better placements")
        adjust_placements2 = st.checkbox("put all seasons' placements on a 1-6 scale", help="seasons 5 and 6 are on a 1-7 scale because of differences in the bracket structure; this adjustment keeps all the seasons on the 1-6 scale so players who came last in season 5 or 6 aren't lower that ones who came last in the other seasons", key=23)
        placements2 = adjustments.rescale_placements(placements) if adjust_placements2 else placements
        placements2 = placements2[['season', 'player', 'seed', 'placement']]
        placements2["season"] = placements2["season"].astype("category")
        place_by_seed = px.strip(placements2, x="placement", y="seed", color='season', hover_data=['season', 'player', 'placement', 'seed'])
        place_by_seed.update_traces(jitter=0.75)
        st.write("plot has jitter added to be able to see all points, hover points to see exact values")
        st.plotly_chart(place_by_seed)
        #st.write(placements2)

# seeds played per player and season ----------------------------------------------------------------

col3, col4 = st.columns([0.4, 0.6])

with col3:
    with st.container(
        border=True,
        width='stretch',
        height='stretch'
    ):
        seeds_by_season = filters.seeds_by_season(df)
        most_seeds_season = seeds_by_season[seeds_by_season['number of seeds'] == max(seeds_by_season['number of seeds'])]['season'].iloc[0]
        most_seeds_season_count = seeds_by_season[seeds_by_season['number of seeds'] == max(seeds_by_season['number of seeds'])]['number of seeds'].iloc[0]
        least_seeds_season = seeds_by_season[seeds_by_season['number of seeds'] == min(seeds_by_season['number of seeds'])]['season'].iloc[0]
        least_seeds_season_count = seeds_by_season[seeds_by_season['number of seeds'] == min(seeds_by_season['number of seeds'])]['number of seeds'].iloc[0]
        
        most_percent_season = seeds_by_season[seeds_by_season['percent of possible'] == max(seeds_by_season['percent of possible'])]['season'].iloc[0]
        most_percent_percent = seeds_by_season[seeds_by_season['percent of possible'] == max(seeds_by_season['percent of possible'])]['percent of possible'].iloc[0]
        least_percent_season = seeds_by_season[seeds_by_season['percent of possible'] == min(seeds_by_season['percent of possible'])]['season'].iloc[0]
        least_percent_percent = seeds_by_season[seeds_by_season['percent of possible'] == min(seeds_by_season['percent of possible'])]['percent of possible'].iloc[0]
        
        st.markdown("""#### seeds played per season""")
        show_as = st.pills('show as', ['number of seeds', '% of possible seeds'], default = 'number of seeds')
        if not show_as: st.warning("choose an option")
        else:
            if show_as == 'number of seeds':
                st.markdown(f"""  
                    * season with most seeds played: <span style="color:#00c15a;"><b>{most_seeds_season}</b></span> (<span style="color:#00c15a;">{most_seeds_season_count}</span> seeds played)
                    * season with least seeds played: <span style="color:#00c15a;"><b>{least_seeds_season}</b></span> (<span style="color:#00c15a;">{least_seeds_season_count}</span> seeds played)
                """, unsafe_allow_html=True)
                seeds_season_bar = px.bar(seeds_by_season, x = 'season', y = 'number of seeds', color = 'season', height = 225)
            else:
                st.markdown(f"""  
                    * season with highest percent of possible seeds played: <span style="color:#00c15a;"><b>{most_percent_season}</b></span> (<span style="color:#00c15a;">{round(most_percent_percent, 2)}%</span> of possible seeds played)
                    * season with lowest percent of possible seeds played: <span style="color:#00c15a;"><b>{least_percent_season}</b></span> (<span style="color:#00c15a;">{round(least_percent_percent, 2)}%</span> of possible seeds played)
                """, unsafe_allow_html=True)
                seeds_season_bar = px.bar(seeds_by_season, x = 'season', y = 'percent of possible', color = 'season', height = 225)
            seeds_season_bar.update_layout(showlegend=False)
            st.plotly_chart(seeds_season_bar)
            st.dataframe(seeds_by_season, height=150)

with col4:
    with st.container(
        border=True,
        width='stretch',
        height='stretch'
    ):
        st.markdown("""#### games played per player""", help='number of games played by each player, can be shown by individual seed or by overall series')
        by = st.pills('by', ['seed', 'series'], default = 'seed', key = 1)
        if not by: st.warning("choose an option")
        else:
            seeds_by_player = filters.winrate(df, by = by)
            most_seeds_player = seeds_by_player[seeds_by_player['played'] == max(seeds_by_player['played'])].reset_index()['player'].iloc[0]
            most_seeds_player_count = seeds_by_player[seeds_by_player['played'] == max(seeds_by_player['played'])]['played'].iloc[0]

            seeds_player_boxplot = px.box(
                seeds_by_player.rename(columns={'played':by + ' played'}).reset_index(),
                x=by + " played",
                height=225, points="all", hover_data=['player', by + ' played']
            )
            seeds_player_boxplot.update_xaxes(showgrid=True)
            seeds_player_boxplot.update_traces(fillcolor=None, selector=dict(type='box'),marker=dict(opacity=0.4, color='white'))
            seeds_player_boxplot.update_traces(pointpos=0, jitter=1)

            st.markdown(f"""  
                * most {by}{'s' if by == 'seed' else ''} played: <span style="color:#00c15a;"><b>{most_seeds_player}</b></span> (<span style="color:#00c15a;">{most_seeds_player_count}</span> {by}{'s' if by == 'seed' else ''} played)
            """, unsafe_allow_html=True)
            st.plotly_chart(seeds_player_boxplot)
            st.dataframe(seeds_by_player.reset_index()[['player', 'played']].sort_values('played', ascending=False).reset_index(drop=True).rename(columns={'played': by + 's played' if by == 'seed' else by + ' played'}), height=250)

# wins --------------------------------------------------------------------

col5, col6 = st.columns([0.5, 0.5]) 

with col5:
    with st.container(
        border=True,
        width='stretch',
        height='stretch'
    ):
        st.markdown("""#### number of wins per player""")
        by2 = st.pills('by', ['seed', 'series'], default = 'seed', key = 2)
        if not by2: st.warning("choose an option")
        else: 
            seeds_by_player = filters.winrate(df, by = by2)
            most_wins_player = seeds_by_player[seeds_by_player['won'] == max(seeds_by_player['won'])].reset_index()['player'].iloc[0]
            most_wins_player_count = seeds_by_player[seeds_by_player['won'] == max(seeds_by_player['won'])]['won'].iloc[0]

            st.markdown(f"""  
                * most {by2}{'s' if by2 == 'seed' else ''} won: <span style="color:#00c15a;"><b>{most_wins_player}</b></span> (<span style="color:#00c15a;">{most_wins_player_count}</span> {by2}{'s' if by2 == 'seed' else ''} won)
            """, unsafe_allow_html=True)

            seeds_won_boxplot = px.box(
            seeds_by_player.rename(columns={'won':by2 + ('s' if by2 == 'seed' else '') + ' won'}).reset_index(),
                x=by2 + ('s' if by2 == 'seed' else '') + ' won',
                height=225, points="all", hover_data=['player', by2 + ('s' if by2 == 'seed' else '') + ' won']
            )
            seeds_won_boxplot.update_xaxes(showgrid=True)
            seeds_won_boxplot.update_traces(fillcolor=None, selector=dict(type='box'),marker=dict(opacity=0.4, color='white'))
            seeds_won_boxplot.update_traces(pointpos=0, jitter=1)
            st.plotly_chart(seeds_won_boxplot)
            st.dataframe(seeds_by_player.reset_index()[['player', 'won']].rename(columns={'won':by2 + ('s' if by2 == 'seed' else '') + ' won'}).sort_values(by2 + ('s' if by2 == 'seed' else '') + ' won', ascending=False).reset_index(drop=True), height=150)

# win rate -------------------------------------------------------------------------------------
 
with col6:
    with st.container(
        border=True,
        width='stretch',
        height='stretch'
    ):
        st.markdown("""#### win rate per player""")
        winrate_by = st.pills('winrate by', ['seed', 'series'], default = 'seed')
        if not winrate_by: st.warning("choose an option")
        else:
            if winrate_by == 'seed':
                adjust_winrate = st.checkbox('adjust for number of seeds played', help="adjusts for the number of seeds played to keep players with very few seeds from having skewed results. makes the rankings in the table more robust, but the values lose interpretability")
            else:
                adjust_winrate = st.checkbox('adjust for number of series played', help="adjusts for the number of series played to keep players with very few matches from having skewed results. makes the rankings in the table more robust, but the values lose interpretability")
            
            seeds_by_player = filters.winrate(df, by = winrate_by, adjust = adjust_winrate)
            most_winrate_player = seeds_by_player[seeds_by_player['winrate'] == max(seeds_by_player['winrate'])].reset_index()['player'].iloc[0]
            most_winrate_player_wr = seeds_by_player[seeds_by_player['winrate'] == max(seeds_by_player['winrate'])]['winrate'].iloc[0]

            st.markdown(f"""  
                * highest win rate: <span style="color:#00c15a;"><b>{most_winrate_player}</b></span> (<span style="color:#00c15a;">{round(most_winrate_player_wr * 100, 2)}%</span> {'adjusted' if adjust_winrate else ''} win rate)
            """, unsafe_allow_html=True)
            winrate_boxplot = px.box(
            seeds_by_player.rename(columns={'winrate':'win rate'}).reset_index(),
                x="win rate",
                height=225, points="all", hover_data=['player', 'win rate']
            )
            winrate_boxplot.update_xaxes(showgrid=True)
            winrate_boxplot.update_traces(fillcolor=None, selector=dict(type='box'),marker=dict(opacity=0.4, color='white'))
            winrate_boxplot.update_traces(pointpos=0, jitter=1)
            st.plotly_chart(winrate_boxplot)
            st.dataframe(seeds_by_player.reset_index()[['player', 'winrate']].rename(columns={'winrate':'win rate'}).sort_values('win rate', ascending=False).reset_index(drop=True), 
                        height=150,
                        column_config={
                            "win rate": st.column_config.ProgressColumn(
                                min_value=0,
                                max_value=1,
                                color="auto",
                                format="compact",
                                )
                        })

# times ----------------------------------------------------------------------------------------

times = filters.select_splits(df)

with st.container(
    border=True,
    width='stretch',
    height='stretch'
    ):
    st.markdown("""#### all playoffs times""")
    selected_split = st.pills("split: ", times['split'].unique(), default = "finish", selection_mode = "single")
    if not selected_split: st.warning("choose a split")
    else:
        alltimes = times[times['split'] == selected_split]

        fastest_time = alltimes['time'].min()
        fastest_time_player = alltimes[alltimes['time'] == fastest_time]['player'].iloc[0]
        fastest_time_match = alltimes[alltimes['time'] == fastest_time]['match'].iloc[0]
        fastest_time_season = alltimes[alltimes['time'] == fastest_time]['season'].iloc[0]
        if fastest_time < 0:
            fastest_time = "-" + str(datetime.timedelta(seconds = abs(fastest_time)))[2:]
        else: fastest_time = str(datetime.timedelta(seconds = abs(fastest_time)))[2:]

        slowest_time = alltimes[alltimes['time'] == max(alltimes['time'])]['time'].iloc[0]
        slowest_time_player = alltimes[alltimes['time'] == max(alltimes['time'])]['player'].iloc[0]
        slowest_time_match = alltimes[alltimes['time'] == max(alltimes['time'])]['match'].iloc[0]
        slowest_time_season = alltimes[alltimes['time'] == max(alltimes['time'])]['season'].iloc[0]
        slowest_time = str(datetime.timedelta(seconds = slowest_time))[2:]

        mapping = [
            ("RO16", "round of 16"),
            ("QF", "quarterfinals"),
            ("SF", "semifinals"),
            ("TPM", "third place match"),
            ("GF", "grand finals"),
            ("R1", "round 1"),
            ("R2", "round 2"),
        ]

        for key, value in mapping:
            if key in fastest_time_match:
                fastest_time_match = value
                break
        for key, value in mapping:
            if key in slowest_time_match:
                slowest_time_match = value
                break

        st.markdown(f"""  
            * fastest {selected_split}: <span style="color:#00c15a;"><b>{fastest_time}</b></span> by <span style="color:#00c15a;"><b>{fastest_time_player}</b></span> (<span style="color:#00c15a;">season {fastest_time_season} {fastest_time_match}</span>)
            * slowest {selected_split}: <span style="color:#00c15a;"><b>{slowest_time}</b></span> by <span style="color:#00c15a;"><b>{slowest_time_player}</b></span> (<span style="color:#00c15a;">season {slowest_time_season} {slowest_time_match}</span>)
            """, unsafe_allow_html=True, help = 'negative values come from entering the fort first' if selected_split == 'bastion split' else None)

        overall_boxplot = px.box(alltimes, y = "time", height = 500, points='all', hover_data=['player', 'time', 'season', 'match'])
        overall_boxplot.update_xaxes(showgrid=True)
        overall_boxplot.update_traces(fillcolor=None, selector=dict(type='box'),marker=dict(color='white'))
        overall_boxplot.update_traces(pointpos=0, jitter=0.5, marker=dict(opacity=0.2))

        seasons_boxplot = px.box(alltimes, y = "time", x = 'season', color = 'season', height = 500, points='all', hover_data=['player', 'time', 'season', 'match'])
        seasons_boxplot.update_xaxes(showgrid=True)
        seasons_boxplot.update_traces(fillcolor=None, selector=dict(type='box'))
        seasons_boxplot.update_traces(pointpos=0, jitter=0.5, marker=dict(opacity=0.4))

        otime = filters.over_time(df, splits = [selected_split])
        chart = px.line(
            otime,
            x="game_order",
            y="time",
            color="season",
            hover_data=["player", "season", "match", "time"],
            markers=True,
            labels=dict(time="time (seconds)", game_order="seeds in order"),
            height = 350
        )
        chart.update_xaxes(showticklabels=False)
        chart.update_traces(
            hovertemplate=
            "<b>%{customdata[0]}</b><br>" +
            "season: %{customdata[1]}<br>" +
            "match: %{customdata[2]}<br>" +
            "time: %{y}<extra></extra>"
        )

        col7, col8 = st.columns([0.2, 0.8])
        with col7:
            st.markdown("""###### overall""")
            st.plotly_chart(overall_boxplot)
        with col8:
            st.markdown("""###### by season""")
            st.plotly_chart(seasons_boxplot)
        st.markdown("""###### over time""")
        st.plotly_chart(chart)
        st.markdown("""###### all times""")
        alltimes = alltimes[alltimes['time'].isna() == False].sort_values('time').reset_index(drop=True)
        alltimes['time_new'] = [str(datetime.timedelta(seconds = abs(time)))[2:] for time in alltimes['time']]
        alltimes.loc[alltimes['time'] < 0, 'time_new'] = (
            '-' + alltimes.loc[alltimes['time'] < 0, 'time_new']
        )
        alltimes['time'] = alltimes['time_new']
        alltimes = filters.add_round(alltimes)
        alltimes["seed"] = [s[-1:] for s in alltimes['match']]
        st.dataframe(alltimes[['player', 'season', 'round', 'seed', 'time']].rename(columns={'time':selected_split}), 
                    height=200)
    
# average times --------------------------------------------------------------------------------------------------------------------------------------------

with st.container(
    border=True,
    width='stretch',
    height='stretch'
    ):
    st.markdown("""#### average times (per season and player)""")
    selected_split2 = st.pills("split: ", times['split'].unique(), default = "finish", selection_mode = "single", key = 3)
    if not selected_split2: st.warning("choose a split")
    else:
        alltimes2 = times[times['split'] == selected_split2]
        overall_average = str(datetime.timedelta(seconds = round(alltimes2['time'].mean())))[2:]
        st.markdown(f"""  
                * overall average {selected_split2}: <span style="color:#00c15a;"><b>{overall_average}</b></span>
                """, unsafe_allow_html=True)
        avg_by_season = filters.average_time(alltimes2, seasons = list(alltimes2['season'].unique())).reset_index()
        col9, col10 = st.columns([0.5, 0.5])
        with col9:
            st.markdown("""###### average times by season""")
            fastest_season = avg_by_season[avg_by_season['average_time'] == min(avg_by_season['average_time'])]['season'].iloc[0]
            fastest_season_avg = str(datetime.timedelta(seconds = round(avg_by_season[avg_by_season['average_time'] == min(avg_by_season['average_time'])]['average_time'].iloc[0])))[2:]
            slowest_season = avg_by_season[avg_by_season['average_time'] == max(avg_by_season['average_time'])]['season'].iloc[0]
            slowest_season_avg = str(datetime.timedelta(seconds = round(avg_by_season[avg_by_season['average_time'] == max(avg_by_season['average_time'])]['average_time'].iloc[0])))[2:]
            st.markdown(f"""  
                * fastest season: <span style="color:#00c15a;"><b>season {fastest_season}</b></span> (<span style="color:#00c15a;">{fastest_season_avg}</span> average {selected_split2})
                * slowest season: <span style="color:#00c15a;"><b>season {slowest_season}</b></span> (<span style="color:#00c15a;">{slowest_season_avg}</span> average {selected_split2})
                """, unsafe_allow_html=True)
            season_averages = px.line(avg_by_season.rename(columns={'average_time':'average ' + selected_split2}).sort_values('season').reset_index(),
                x="season",
                y="average " + selected_split2,
                hover_data=["season", "average " + selected_split2],
                markers=True,
                height = 250
            )
            season_averages.update_traces(line=dict(color="#00c15a", width=2))
            st.plotly_chart(season_averages)
            avg_by_season['average_time'] = [str(datetime.timedelta(seconds = round(time)))[2:] for time in avg_by_season['average_time']]
            st.dataframe(avg_by_season.sort_values('season').rename(columns={'average_time':'average ' + selected_split2})[['season', 'average ' + selected_split2]], height = 150)
        
        with col10:
            st.markdown("""###### average times by player""")
            adjust_for_season_times = st.checkbox('adjust for season', help="mean centers the times within each season; this accounts for the overall reduction in times as the seasons go by. this makes the ranking table below more about how a player performs against the people they played against at the time, and can be interpreted more as 'how much faster/slower does this player play on average compared to the average time in that season'")
            adjust_for_times = st.checkbox('adjust for number of times for this split', help="adjusts for the number of times the player finished this split to keep players with very few instances from having skewed results. keep in mind that this makes the rankings in the table more robust, but the actual numbers lose interpretability")
            avg_by_player = filters.average_time(alltimes2, adjust = adjust_for_times, adjust_for_seasons=adjust_for_season_times).reset_index()
            
            fastest_avg_player = avg_by_player[avg_by_player['average_time'] == min(avg_by_player['average_time'])]['player'].iloc[0]
            fastest_avg_player_time = round(avg_by_player[avg_by_player['average_time'] == min(avg_by_player['average_time'])]['average_time'].iloc[0])

            sign = "-" if fastest_avg_player_time < 0 else ""
            fastest_avg_player_time = abs(fastest_avg_player_time)

            minutes, fastest_avg_player_time = divmod(fastest_avg_player_time, 60)
            fastest_avg_player_time = f"{sign}{minutes:02}:{fastest_avg_player_time:02}"

            if adjust_for_season_times:
                st.markdown(f"""  
                    * fastest average time: <span style="color:#00c15a;"><b>{fastest_avg_player}</b></span> (on average <span style="color:#00c15a;">{fastest_avg_player_time}</span> {'(adjusted)' if adjust_for_times else ''} from the average {selected_split2} of players in the same season)
                    """, unsafe_allow_html=True)
            else:
                st.markdown(f"""  
                    * fastest average time: <span style="color:#00c15a;"><b>{fastest_avg_player}</b></span> (<span style="color:#00c15a;">{fastest_avg_player_time}</span> {'adjusted' if adjust_for_times else ''} average {selected_split2})
                    """, unsafe_allow_html=True)
            
            player_avgs_boxplot = px.box(avg_by_player.rename(columns={'average_time':'average ' + selected_split2}).reset_index(), x = 'average ' + selected_split2, height = 210, points='all', hover_data=['player', 'average ' + selected_split2])
            player_avgs_boxplot.update_xaxes(showgrid=True)
            player_avgs_boxplot.update_traces(fillcolor=None, selector=dict(type='box'))
            player_avgs_boxplot.update_traces(pointpos=0, jitter=0.5, marker=dict(opacity=0.4, color='white'))
            st.plotly_chart(player_avgs_boxplot)
            avg_by_player = avg_by_player[avg_by_player['average_time'].isna() == False].sort_values('average_time').reset_index(drop=True)
            avg_by_player['time_new'] = [str(datetime.timedelta(seconds = abs(round(time))))[2:] for time in avg_by_player['average_time']]
            avg_by_player.loc[avg_by_player['average_time'] < 0, 'time_new'] = (
                '-' + avg_by_player.loc[avg_by_player['average_time'] < 0, 'time_new']
            )
            avg_by_player['average_time'] = avg_by_player['time_new']
            avg_by_player = avg_by_player.rename(columns={'average_time':'average ' + selected_split2})
            st.dataframe(avg_by_player[['player', 'average ' + selected_split2]], height = 150)

# seed types -----------------------------------------------------------------------------------------------------

with st.container(
    border=True,
    width='stretch',
    height='stretch'
):
    st.markdown("""#### seed types""")
    pie, box = st.columns([0.45, 0.55])
    splits = times['split'].unique()

    c, t = st.columns(2)

    with c:
        st.markdown("""##### overall seed type frequency""")
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
    box, t = st.columns(2)
    with box:
        box_df = df[['player', 'season', 'match', 'seed_type', seed_types_by]].sort_values('seed_type')
        seed_type_box = px.box(box_df, y = seed_types_by, x = 'seed_type', color = 'seed_type', height = 600, points='all', hover_data=['player', seed_types_by, 'season', 'match'])
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
            fastest_time_st_pl = df[df[seed_types_by] == fastest_time_st]['player'].iloc[0]
            slowest_time_st_pl = df[df[seed_types_by] == slowest_time_st]['player'].iloc[0]

            if fastest_time_st < 0:
                fastest_time_st = "-" + str(datetime.timedelta(seconds = abs(fastest_time_st)))[2:]
            else: fastest_time_st = str(datetime.timedelta(seconds = abs(fastest_time_st)))[2:]
            average_time_st = str(datetime.timedelta(seconds = round(average_time_st)))[2:]
            slowest_time_st = str(datetime.timedelta(seconds = abs(slowest_time_st)))[2:]

            st.markdown(f'<span style="color:#00c15a;font-weight:bold">{seedtype}</span> \n - average <span style="font-weight:bold">{seed_types_by}</span>: <span style="color:#00c15a;font-weight:bold">{average_time_st}</span>\n - fastest <span style="font-weight:bold">{seed_types_by}</span>: <span style="color:#00c15a;font-weight:bold">{fastest_time_st}</span> (by <a href="/player?player={fastest_time_st_pl}" class="player-link" target="_self">{fastest_time_st_pl}</a>)\n - slowest <span style="font-weight:bold">{seed_types_by}</span>: <span style="color:#00c15a;font-weight:bold">{slowest_time_st}</span> (by <a href="/player?player={slowest_time_st_pl}" class="player-link" target="_self">{slowest_time_st_pl}</a>)', unsafe_allow_html=True)

    st.markdown("""##### seed types by season""")
    seedtype2 = st.pills("seed type", df['seed_type'].unique(), key = 6, default = "ruined portal")
    seed_types_by2 = st.pills('show', list(splits), key = 7, default = 'finish')
    seedtypes_byseason = df[['player', 'season', 'match', 'seed_type', seed_types_by2]].sort_values('seed_type')
    seedtypes_byseason = seedtypes_byseason[seedtypes_byseason['seed_type'] == seedtype2].sort_values('season')
    seed_type_box = px.box(seedtypes_byseason, y = seed_types_by2, x = 'season', title = seedtype2 + " " + seed_types_by2 + " times per season", color = 'season', height = 400, points='all', hover_data=['player', seed_types_by2, 'season', 'match'])
    seed_type_box.update_xaxes(showgrid=True)
    seed_type_box.update_traces(fillcolor=None, selector=dict(type='box'))
    seed_type_box.update_traces(pointpos=0, jitter=0.5, marker=dict(opacity=0.4))
    seed_type_box.update_layout(showlegend=False)
    st.plotly_chart(seed_type_box)

    st.markdown("""##### seed type averages by player""")
    adjust_st = st.checkbox('adjust for number of instances')
    seed_types_by3 = st.pills('show', list(splits), key = 8, default = 'finish')
    st_players_toplot = filters.seedtype_avgs(df, seed_types_by3, adjust = adjust_st)

    boxplt, table = st.columns(2)
    with boxplt:
        st_playeravg_box = px.box(st_players_toplot, y = 'average', x = 'seed_type', color = 'seed_type', height = 400, points='all', hover_data=['player', 'average'])
        st_playeravg_box.update_xaxes(showgrid=True)
        st_playeravg_box.update_traces(fillcolor=None, selector=dict(type='box'))
        st_playeravg_box.update_traces(pointpos=0, jitter=0.5, marker=dict(opacity=0.4))
        st_playeravg_box.update_layout(showlegend=False)
        st.plotly_chart(st_playeravg_box)  
        
    with table:
        view = st.pills('view', ['average times', 'counts'], default = 'average times')
        st.markdown(f"""###### {"average" if view == 'average times' else ""} {seed_types_by3} {"" if view == 'average times' else "counts"} per seed type by player""")
        if view == 'average times':
            st_players = (st_players_toplot.pivot(index='player', columns='seed_type', values='average').reset_index())
            cols = st_players.columns[1:]
            st_players[cols] = st_players[cols].apply(
                lambda col: col.map(
                    lambda x: (
                        (("-" if x < 0 else "") +
                         str(pd.to_timedelta(abs(round(x)), unit="s")))[10:]
                        if pd.notnull(x) else ""
                    )
                )
            )
        else:
            st_players = (st_players_toplot.pivot(index='player', columns='seed_type', values='match_count').reset_index())
        st.dataframe(st_players)
    
