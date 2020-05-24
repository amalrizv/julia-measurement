import numpy as np
import pandas as pd
def latx_print(input):
    # Read csv

    df1 = pd.read_csv(input)
    df1.set_index('op')
    df =     df1.pivot(index='op', columns='lang', values='mean')
    #df  = df1.groupby('lang').sum().unstack()

    print(df.to_latex())

latx_print("lock.csv")
