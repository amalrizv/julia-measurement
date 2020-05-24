import matplotlib.pyplot as plt
import numpy as np
import sys
import matplotlib as mpl
from scipy import stats

mpl.rcParams["errorbar.capsize"] = 2

BIGGER_SIZE = 18
plt.rc('font', size=BIGGER_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=BIGGER_SIZE)     # fontsize of the x and y labels
plt.rc('xtick', labelsize=BIGGER_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=BIGGER_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=BIGGER_SIZE)

def barplot_files(fnames, xlabels,  yaxis):

    xdef = np.arange(0, len(xlabels))
    orig = [np.loadtxt(f) for f in fnames]
    data = []

    # outlier removal (Tukey)
    for d in orig:
        # outlier removal (Tukey, 1.5 param)
        d_25 = np.quantile(d, 0.25)
        iqr = stats.iqr(d)
        d_75 = np.quantile(d, 0.75)
        lower = d_25 - 1.5*iqr
        upper = d_75 + 1.5*iqr
        cdata = np.array([x for x in d if x > lower and x < upper])
        data.append(cdata)

    bars    = [np.mean(x) for x in data]
    stddevs = [np.std(x) for x in data]

    fig, ax = plt.subplots(1, figsize=(7,7))

    ax.bar(xdef, bars, yerr=stddevs, width=0.3, color='rebeccapurple', edgecolor='black', linewidth=0.5, alpha=0.7)

    ax.set(xticklabels=xlabels)
    plt.xticks(xdef, rotation=30)
    plt.ylabel(yaxis)
    plt.tight_layout()
    plt.yscale('log')
    
    plt.savefig("parallel-constructs.pdf")



exps        = ["c_pt_parfor", "c_omp_parfor", "julia_parallel_for", "julia_pmap"]
filenames   = ["data/thread-decomposition/" + x + ".dat" for x in exps]
yaxis_title = "Latency (ns)"

barplot_files(filenames, ["pthreads manual", "OMP parallel for", "Julia parallel for", "Julia pmap()"],  yaxis_title)

