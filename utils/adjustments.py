# puts placements on the same scale
def rescale_placements(data):
    df = data.copy()
    df["placement"] = (
                df.groupby("season")["placement"]
                .transform(lambda x: 1 + (x - x.min()) * 5 / (x.max() - x.min()))
            )
    return df

def adjust(df, to_adjust, by, k = None):
    global_avg = df[to_adjust].mean() * 1.5
    if k: k = k 
    else: k = df[to_adjust].mean()
    df[to_adjust] = (df[to_adjust] * df[by] + global_avg * k) / (df[by] + k)
    return df.reset_index()
