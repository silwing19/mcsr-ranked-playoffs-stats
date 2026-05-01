# puts placements on the same scale
def rescale_placements(df):
    df["placement"] = (
                df.groupby("season")["placement"]
                .transform(lambda x: 1 + (x - x.min()) * 5 / (x.max() - x.min()))
            )
    return df

def adjust(df, to_adjust, by, k = None):
    global_avg = df[to_adjust].mean()
    if k: k = k 
    else: k = 3
    df[to_adjust] = (df[to_adjust] * df[by] + global_avg * k) / (df[by] + k)
    return df.reset_index()
