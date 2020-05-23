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
from docopt import docopt
import sys


# KCH: Use this one as a template. Add a dispatch line in main as well
def plot_total_time(proc_count,output, df):

    print("Producing figure for wall clock time...")

    # have to convert julia timings to sec (why is it in nsec in the first place???)
    df['total-procs'] /= 14
    df['total-procs'] = df['total-procs'].apply(np.int64)
    print(df['total-procs'])
    for i, row in df.iterrows():
        if row['lang'] == 'julia':
            df.loc[i,'total-time'] = df.loc[i,'total-time']

    # take a slice with only the Index column (procs), the series column (language), 
    # and the values (total-time)
    b = df[['lang', 'total-time', 'total-procs']]

    # we have to pivot it so that total-procs is the index before plotting it
    ax = b.pivot(index='total-procs', columns='lang', values='total-time').plot.bar(rot=0)
    bars = ax.patches
    hatches = ['xxx','xxx','xxx','xxx','xxx','---','---','---','---','---']

    for bar, hatch in zip(bars, hatches):
        bar.set_hatch(hatch)
    ax.legend(loc='upper left',ncol=1)
    #ax.set_title("Parameter size "+proc_count)
    ax.set_ylabel("Execution time (s)")
    ax.set_xlabel("Total number of MPI Ranks")
    plt.axis('tight')
    plt.tight_layout()
    print(f"OK: output graph saved in: {output}")
    plt.savefig(output)


def plot_gflops(output, df):

    print("Producing figure for GFLOP/s...")

    # KCH TODO: why are the Julia GFLOPS values so tiny? 

    b = df[['lang', 'raw-gflops', 'total-procs']]

    ax = b.pivot(index='total-procs', columns='lang', values='raw-gflops').plot.bar(rot=0)

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
