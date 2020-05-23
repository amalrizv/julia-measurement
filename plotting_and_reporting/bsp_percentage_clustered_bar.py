import ipdb
import matplotlib
import numpy as np
import pandas as pd
from matplotlib import cm
from matplotlib.ticker import PercentFormatter

# matplotlib.use("TkAgg")  # Do this before importing pyplot!
import matplotlib.pyplot as plt

def bsp_percentage_clustered_bar(input, ouput):
    # Font Size

    SMALL_SIZE  = 11
    MEDIUM_SIZE = 12
    BIGGER_SIZE = 14
    plt.rc('font', size=MEDIUM_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=MEDIUM_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)     # fontsize of the x and y labels
    plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=MEDIUM_SIZE)

    # Colors for bars Palette warm

    color = cm.coolwarm(np.linspace(0.1,0.9,4))


    # Read csv

    df1 = pd.read_csv(input)

    # Split DataFrame for each language  and then delete those columns

    df_julia = df1.loc[df1['lang']== 'julia']
    df_cpp   = df1.loc[df1['lang'] == 'CPP']

    del df_cpp['lang']
    del df_julia['lang']

    # Calculate percentages

    d_j = df_julia.groupby(['proc', 'op']).agg({'median':'sum'})
    d_c = df_cpp.groupby(['proc', 'op']).agg({'median':'sum'})

    d_j_1 = d_j.groupby(level=0).apply(lambda x: 100*x/float(x.sum()))
    d_c_1 = d_c.groupby(level=0).apply(lambda x: 100*x/float(x.sum()))


    print(d_c_1)
    print(d_j_1)

    # Print table to Latex [optional]
    print(d_j_1.to_latex())
    print(d_c_1.to_latex())

    # Take a slice [Doesnt work]

    def ungroup_datafram(x):
        df = pd.DataFrame(columns=['op', 'median', 'proc'])
        for i, row in x.iterrows():
            df = df.append({'op':i[1], 'proc': i[0], 'median': row[0]}, ignore_index=True)
        return df

    # ipdb.set_trace()

    j = ungroup_datafram(d_j_1)[['op', 'median', 'proc']]  # d_j_1[['op', 'median', 'proc']]
    c = ungroup_datafram(d_c_1)[['op', 'median', 'proc']]  #d_c_1[['op', 'median', 'proc']]

    # Pivot for clustered bar plot

    ax = j.pivot(index='proc', columns='op', values='median').plot.bar(rot=0, width=0.2, color=color, stacked=True, position=1)
    c.pivot(index='proc', columns='op', values='median').plot.bar(ax=ax, rot=0, width=0.2, color=color,stacked=True, position=0)

    # Labels

    plt.xlabel("Ranks per node")
    plt.ylabel("Breakdown")


    # Floating Labels

    rects = ax.patches
    print((rects))
    labels = []                 # Make some labels.
    #labels.extend(('Julia','','CPP','Julia','CPP','Julia','CPP','Julia','CPP','Julia','CPP'))
    #labels = np.arange(40)
    # RZV:This is a hack for now for floating labels
    labels = ['     Julia CPP', '     Julia CPP', '     Julia CPP', '      Julia CPP', '     Julia CPP']
    for rect, label in zip(rects, labels):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2, height + 0.5, label, ha='center', va='bottom')
    # Hatches

    #bars = ax.patches
    #hatches=['/////', 'xxxxx', '-----', '.....'
    #hatches = ['/////','/////','/////','/////','/////','.....','.....','.....','.....','.....', '++++', '++++', '++++','++++','++++','-----','-----','-----','-----','-----',\
    #       '/////','/////','/////','/////','/////','.....','.....','.....','.....','.....', '++++', '++++', '++++','++++','++++','-----','-----','-----','-----','-----']
    #for bar, hatch in zip(bars, hatches):
    #    bar.set_hatch(hatch)

    # Percent Y Axis
    #y_value=['{:,.2f}'.format(x) + '%' for x in ax.get_yticks()]
    #ax.set_yticklabels(y_value)
    #ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: '{:.0%}'.format(y)))

    #vals = ax.get_yticks()
    #ax.set_yticklabels(['{:,.2%}'.format(x) for x in vals])
    plt.gca().yaxis.set_major_formatter(PercentFormatter(100))
    #ax.yaxis.get_major_formatter().set_scientific(False)
    #ax.yaxis.get_major_formatter().set_useOffset(False)

    # Legend
    plt.legend(["comms", "flops","reads", "writes"],loc='upper center',bbox_to_anchor=(0.5,1.15), ncol=4,title="", frameon=False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)


    # Save Figure
    #plt.show()
    fig = plt.gcf()
    fig.set_size_inches((14.40, 8.64), forward=False)
    plt.savefig(output)


bsp_percentage_clustered_bar("bsp_comm_10.csv", "bsp_prcnt_10.pdf")
bsp_percentage_clustered_bar("bsp_comm_10_opt.csv", "bsp_prcnt_10_opt.pdf")
bsp_percentage_clustered_bar("bsp_comm_100.csv", "bsp_prcnt_100.pdf")
bsp_percentage_clustered_bar("bsp_comm_100_opt.csv", "bsp_prcnt_100_opt.pdf")
