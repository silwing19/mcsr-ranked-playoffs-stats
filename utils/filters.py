import pandas as pd
import streamlit as st
import numpy as np
from utils import adjustments

SPLITS = ['overworld', 'terrain to bastion', 'bastion split', 'fort to blind', 'blind to stronghold',
          'stronghold nav', 'end fight', "finish"]

# loads split and placement data and converts all times to seconds
@st.cache_data
def load_data():
    placements = pd.read_csv("placements.csv")
    df = pd.read_csv("all_splits.csv")
    df.iloc[:, 4:18] = df.iloc[:, 4:18].apply(
        lambda col: pd.to_timedelta(col).dt.total_seconds()
    )
    df = df.sort_values('season')
    df['season'] = df['season'].astype('category')
    return [df, placements]

# returns a data frame with player, average placement, number of seasons, and percentile for average placement. 
# has an option to return it with the placements rescaled and/or adjusted for number of seasons
def playoffsplacements(df, rescale = False, adjust = False):
    if rescale: df = adjustments.rescale_placements(df)
    df =  df.groupby('player').agg({'season':'count', 'placement':'mean', 'seed':'mean'}).rename(columns={'season': 'playoffs_played', 'placement': 'average_placement', 'seed': 'average_seed'})
    if adjust: df = adjustments.adjust(df, 'average_placement', 'playoffs_played', 3)
    if adjust: df = adjustments.adjust(df, 'average_seed', 'playoffs_played', 3)
    df["average_placement_percentile"] = df["average_placement"].rank(pct=True)
    df["average_seed_percentile"] = df["average_seed"].rank(pct=True)
    return df.reset_index()

# returns a data frame with each player's games played, games won and lost, winrate, and percentiles for all of these. 
# has an option to go by seeds or by series, and also adjust winrate by seeds/series played
def winrate(df, adjust = False, by = 'seed', byseason = False):
    if by == 'seed':
        df['win'] = np.where(df['finish'].isna(), 0, 1)
        if byseason: 
            df = df.groupby(['player', 'season']).agg({'match':'count', 'win':'sum'}).rename(columns={'match': 'played', 'win': 'won'})
        else:
            df = df.groupby('player').agg({'season':'count', 'win':'sum'}).rename(columns={'season': 'played', 'win': 'won'})
    else:
        df = convert_to_series(df, byseason = byseason)
    df = df[df['played'] > 0]
    df['lost'] = df['played'] - df['won']
    df['winrate'] = df['won'] / df['played']
    if adjust: df = adjustments.adjust(df, 'winrate', 'played', k = 5)
    df["played_percentile"] = df["played"].rank(pct=True)
    df["won_percentile"] = df["won"].rank(pct=True)
    df["winrate_percentile"] = df["winrate"].rank(pct=True)
    return df.reset_index()

# returns a table with the number of seeds played per season, the number of possible seeds for each season,
# and the percent of all possible seeds that were played for each season
def seeds_by_season(df):
    df = df.sort_values(['season', 'match']).drop_duplicates(subset=['season', 'match'])
    df = df.groupby('season').count().reset_index()[['season', 'match']].rename(columns={'match':'number of seeds'})
    df['possible seeds'] = np.where(df['season'].isin([1, 2, 3, 4]), ((3 * 8) + (5 * 7) + (7 * 1)), ((15 * 5) + (7 * 1)))
    df['percent of possible'] = (df['number of seeds'] / df['possible seeds']) * 100
    return df

# converts a table of seeds into a table of series
def convert_to_series(df, byseason = False):
    df['win'] = np.where(df['finish'].isna(), 0, 1)
    df = df.groupby(['season', 'match', 'player'], observed = True)['win'].sum().reset_index()
    df['match'] = df['match'].str[:-2]
    df = df.groupby(['season', 'match', 'player'], observed = True)['win'].sum().reset_index()
    df["group"] = df.index // 2
    df["winner"] = df.groupby("group")["win"].rank(method="first").eq(2).astype(int)
    if byseason:
        df = df.groupby(['player', 'season']).agg({'match':'count', 'winner':'sum'}).rename(columns={'match': 'played', 'winner': 'won'})
    else: df = df.groupby('player').agg({'match':'count', 'winner':'sum'}).rename(columns={'match': 'played', 'winner': 'won'})
    df['lost'] = df['played'] - df['won']
    return df

# returns the data frame, but filtered for the players you specify
def filter_players(df, players = None):
    df = df[df['player'].isin(players)]
    return df

# returns the data frame, but filtered for the season you specify
def filter_seasons(df, seasons = None):
    df = df[df['season'].isin(seasons)]
    return df

# returns a table with average time and number of instances. if you specify season, it does it by season, and if you specify player, it does it by player
def average_time(df, players=None, seasons=None, adjust = False, adjust_for_seasons = False):
    if players: 
        df = filter_players(df, players)
    elif seasons: 
        df = filter_seasons(df, seasons)
    players2 = df.reset_index()['player'].drop_duplicates()
    df = df[df['time'].isna() == False]
    if adjust_for_seasons: 
        df["time"] = df["time"] - df.groupby("season")["time"].transform("mean")
    if seasons: 
        result = df.groupby('season').agg({'match':'count', 'time':'mean'}).rename(columns={'match': 'number_of_instances', 'time': 'average_time'})
        result = result.reindex(seasons)
    else: 
        result = df.groupby('player').agg({'match':'count', 'time':'mean'}).rename(columns={'match': 'number_of_instances', 'time': 'average_time'})
        result = result.reindex(players)
    if adjust: result = adjustments.adjust(result, 'average_time', 'number_of_instances', 15)
    if 'player' in result.reset_index().columns:
        result = pd.merge(result, players2, how='outer', on='player')
        result["average_time_percentile"] = result["average_time"].rank(pct=True, na_option='bottom')
    return result

# returns a table with the the fastest times, you can filter by player and season
def fastest_time(df, players=None, seasons=None):
    if players: 
        df = filter_players(df, players)
    if seasons: 
        df = filter_seasons(df, seasons)
    if seasons: 
        result = df.groupby('season')['time'].min().to_frame(name='fastest_time')
        result = result.reindex(seasons)
    else:
        result = df.groupby('player')['time'].min().to_frame(name='fastest_time')
        result = result.reindex(players)
    result["fastest_time_percentile"] = result["fastest_time"].rank(pct=True, na_option='bottom')
    return result

# returns a table with split times
def select_splits(df, splits = None, players = None, seasons = None):
    if players: df = filter_players(df, players)
    if seasons: df = filter_seasons(df, seasons)
    if not splits: splits = SPLITS
    splits = df[['season', 'match', 'player', *splits]]
    return pd.melt(splits, id_vars=["season", 'match', 'player'], var_name="split", value_name="time")

# returns a table with times and the order they happened in
def over_time(df, splits = None):
    splits = select_splits(df, splits = splits if splits else None)
    otime = splits.assign(
    round_order=splits['match'].case_when(
        [(splits['match'].str.contains("RO16"), 1),
         (splits['match'].str.contains("QF"), 2),
         (splits['match'].str.contains("SF"), 3),
         (splits['match'].str.contains("TPM"), 4),
         (splits['match'].str.contains("GF"), 5),
         (splits['match'].str.contains("R1"), 1),
         (splits['match'].str.contains("R2"), 1.5)]
    )
    )
    otime = otime.assign(
        seed_order=otime['match'].str.split(".").str[1]
    )
    otime = otime.assign(
        match_order=(otime['match'].str.split("_").str[1]).str.split(".").str[0]
    )
    otime = otime.sort_values(by=['season', 'round_order', "match_order", "seed_order"])
    otime['game_order'] = (otime['match'] != otime['match'].shift()).cumsum()
    otime = otime.sort_values(['game_order']).reset_index(drop=True)
    return otime[otime['time'].isna() == False]

def ordinal(n):
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix

def get_matches(df, player):
    # adds a column for round
    df["round"] = df['match'].case_when(
        [(df['match'].str.contains("RO16"), "round of 16"),
        (df['match'].str.contains("QF"), "quarterfinals"),
        (df['match'].str.contains("SF"), "semifinals"),
        (df['match'].str.contains("TPM"), "third place match"),
        (df['match'].str.contains("GF"), "grand finals"),
        (df['match'].str.contains("R1"), "round 1"),
        (df['match'].str.contains("R2"), "round 2")]    
    )
    df = df.sort_values(['season', 'round', 'match', 'player'])
    df['player_num'] = df.groupby(['season', 'round', 'match']).cumcount() + 1
    winner = df.loc[df['finish'].isna() == False].set_index(['season', 'round', 'match'])['player']
    df = df.pivot(
        index=['season', 'round', 'match'],
        columns='player_num',
        values='player'
    ).rename(columns={1: 'player1', 2: 'player2'})
    result = df.copy()
    result['winner'] = winner
    result = result.reset_index()
    if player: result = result[(result['player1'] == player) | (result['player2'] == player)]
    return result

# gets the series played by each player and who won 
def get_series(df, player):
    result = get_matches(df, player)
    final = (
        pd.concat([
            result[['season','round','player1']].rename(columns={'player1':'player'}),
            result[['season','round','player2']].rename(columns={'player2':'player'})
        ])
        .drop_duplicates()
        .groupby(['season','round'])['player']
        .apply(list)
    )
    winners = result.groupby(['season', 'round'])['winner'].agg(lambda x: x.mode().iloc[0]).to_frame()
    winners = winners[winners['winner'].isna() == False]
    # combine
    final = pd.merge(final, winners, on=['season', 'round'])
    final[['player1','player2']] = pd.DataFrame(final['player'].tolist(), index=final.index)
    order = ['round 1', 'round 2', 'round of 16', 'quarterfinals', 'semifinals', 'third place match', 'grand finals']
    round_order = pd.CategoricalDtype(categories=order, ordered=True)
    final = final.reset_index()
    final['round'] = final['round'].astype(round_order)
    final = final.sort_values(['season', 'round'])
    final.loc[(final["season"] == 5) & (final["round"] == "semifinals") & (final["winner"] == "ancoboy"), "winner"] = 'hackingnoises' 
    return final

# gives you a specific player's percentile for each split compared to all players
def split_percentiles(df, player):
    players = df['player'].unique()
    alltimes = select_splits(df).groupby(['player', 'split']).agg({'time':'mean'}).reset_index()
    d = []
    for pl in players:
        player_vals = {'player':pl}
        for split in alltimes['split'].unique():
            t = alltimes[alltimes['split'] == split]
            player_vals[split] = (t[t['player'] == pl]['time'].iloc[0])
        d = d + [player_vals]

    d = pd.DataFrame(d)
    percentiles = []
    for split in alltimes['split'].unique():
        d1 = d[['player', split]]
        player_time = d1[d1['player'] == player][split].iloc[0]
        if pd.isna(player_time): 
            perc = 0
        else: 
            perc = (100 - (len(d1[d1[split] <= player_time]) / len(players)) * 100) if pd.isna(player_time) == False else 100
        percentiles.append({'split': split, 'percentile': perc})

    return pd.DataFrame(percentiles).reindex([5, 7, 0, 4, 1, 6, 2, 3])

# gives you a specific seed's percentile for each split compared to all times in the data frame you give it (returns for both players)
def seed_percentiles(data, seed_df, season = None, byplayer = False):
    if season: data = data[data['season'] == season]
    df = data.copy()
    alltimes = select_splits(df)
    percentiles1 = []
    player1, player2 = seed_df['player'].sort_values().unique()
    for split in alltimes['split'].unique():
        player_time = seed_df[(seed_df['player'] == player1) & (seed_df['split'] == split)]['time'].iloc[0]
        if byplayer: df = df[df['player'] == player1]
        perc = 100 - (len(df[df[split] <= player_time]) / len(df[df[split].isna() == False]) * 100) if pd.isna(player_time) == False else 0
        percentiles1.append({'split': split, 'percentile': perc})
    df = data.copy()
    percentiles2 = []
    for split in alltimes['split'].unique():
        player_time = seed_df[(seed_df['player'] == player2) & (seed_df['split'] == split)]['time'].iloc[0]
        if byplayer: df = df[df['player'] == player2]
        perc = 100 - (len(df[df[split] <= player_time]) / len(df[df[split].isna() == False]) * 100) if pd.isna(player_time) == False else 0
        percentiles2.append({'split': split, 'percentile': perc})
    percentiles1 = pd.DataFrame(percentiles1)
    percentiles2 = pd.DataFrame(percentiles2)
    return [percentiles1, percentiles2]

# adds a column with the round name
def add_round(df):
    df["round"] = df['match'].case_when(
        [(df['match'].str.contains("RO16"), "round of 16"),
        (df['match'].str.contains("QF"), "quarterfinals"),
        (df['match'].str.contains("SF"), "semifinals"),
        (df['match'].str.contains("TPM"), "third place match"),
        (df['match'].str.contains("GF"), "grand finals"),
        (df['match'].str.contains("R1"), "round 1"),
        (df['match'].str.contains("R2"), "round 2")]    
    )
    round_order = [
        "round 1",
        "round 2",
        "round of 16",
        "quarterfinals",
        "semifinals",
        "third place match",
        "grand finals"
    ]

    df['round'] = pd.Categorical(
        df['round'],
        categories=round_order,
        ordered=True
    )
    return df

# returns a data frame with the average time for each player by seed type (you can choose the split)
def seedtype_avgs(df, split, adjust = False):
    df = df.groupby(['player', 'seed_type']).agg(average=(split, 'mean'), match_count=(split, 'count')).reset_index()
    if adjust: df = adjustments.adjust(df, 'average', 'match_count')
    return df