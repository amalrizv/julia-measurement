#!/usr/bin/python3

""" CG Plot: Plot results from HPCG experiments

Usage:
    cgplot.py [options] 

Options:
    -h --help            Show this screen
    -V --version         Show version
    -i --input=<file>    Input file (defaults to stdin)
    -o --output=<file>   Output file [default: plot.pdf]
    -p --param=<value>   Parameter
    -t --type=<type>     Measurement to plot [default: total-time]

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import cm
from docopt import docopt
import sys

# make hatches less annoyingly thick
mpl.rcParams['hatch.linewidth'] = 0.3
barwidth = 0.3

BIGGER_SIZE = 18
plt.rc('font', size=BIGGER_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=BIGGER_SIZE)     # fontsize of the x and y labels
plt.rc('xtick', labelsize=BIGGER_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=BIGGER_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=BIGGER_SIZE)


# KCH: Use this one as a template. Add a dispatch line in main as well
def plot_total_time(proc_count,output, df):

    print("Producing figure for wall clock time...")

    # have to convert julia timings to sec (why is it in nsec in the first place???)
    df['total-procs'] /= 14
    df['total-procs'] = df['total-procs'].apply(np.int64)
    for i, row in df.iterrows():
        if row['lang'] == 'julia':
            df.loc[i,'total-time'] = df.loc[i,'total-time']

    # take a slice with only the Index column (procs), the series column (language), 
    # and the values (total-time)
    b = df[['lang', 'total-time', 'total-procs']]

    procs = sorted(df['total-procs'].unique())
    bar_pos_c = np.arange(0, len(procs))
    bar_pos_j = [x + barwidth for x in bar_pos_c]

    vals_c = []
    vals_j = []
    for p in procs:
        vals_c.append(b[(b['lang'] == 'CPP') & (b['total-procs'] == p)]['total-time'].values[0])
        vals_j.append(b[(b['lang'] == 'julia') & (b['total-procs'] == p)]['total-time'].values[0])

    color = cm.viridis(np.linspace(0.3, 0.7, 2))

    fig, ax = plt.subplots(1, figsize=(6,5))
    
    hatches = ['x','.','-', '/']

    ax.bar(bar_pos_c, vals_c, label="C++", hatch=hatches[0]*2, width=barwidth, color=color[0], edgecolor='black', linewidth=0.25)
    ax.bar(bar_pos_j, vals_j, label="Julia", hatch=hatches[1]*2, width=barwidth, color=color[1], edgecolor='black', linewidth=0.25)

    ax.legend(loc='best')
    ax.set_xticks([r + (barwidth/2) for r in range(len(procs))])
    ax.set_xticklabels(procs)
    ax.set_ylabel("Execution time (s)")
    ax.set_xlabel("MPI Ranks per Node")
    plt.axis('tight')
    plt.tight_layout()
    print(f"OK: output graph saved in: {output}")
    plt.savefig(output)


def plot_gflops(output, df):

    print("Producing figure for GFLOP/s...")

    # KCH TODO: why are the Julia GFLOPS values so tiny? 

    b = df[['lang', 'raw-gflops', 'total-procs']]

    ax = b.pivot(index='total-procs', columns='lang', values='raw-gflops').plot.bar(rot=0, barwidth=barwidth, hatch=True)

    ax.set_title("HPCG Experiment [Raw GFLOP/s] (14 nodes)")
    ax.set_ylabel("GFLOP/s")
    ax.set_xlabel("Total number of MPI Ranks")
    plt.axis('tight')
    plt.tight_layout()
    print(f, "OK: output graph saved in: {output}")
    plt.savefig(output)



if __name__ ==  '__main__':

    args = docopt(__doc__, version='CGPlot 0.1 (c) Kyle C. Hale')

    output  = args['--output']
    exptype = args['--type']
    param = args['--param']
    infile  = sys.stdin

    if args['--input']:
        infile = args['--input']

    frame = pd.read_csv(infile)

    frame.set_index('total-procs')

    dispatch = {
            'total-time': plot_total_time,
            'gflops': plot_gflops}

    func = dispatch.get(exptype, lambda: "Invalid experiment type")

    func(param,output, frame)
