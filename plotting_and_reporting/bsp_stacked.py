import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib import cm
import itertools as it
import logging 
import os
import sys

# make hatches less annoyingly thick
mpl.rcParams['hatch.linewidth'] = 0.15

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

CACHEFILE=".expframe.cached.h5"

# This generates a clustered, stacked bar for two sets of scaling
# experiments.
# Command-line arguments:
#  (1) the path to the .dat files
#  (2) the name of the output file
# 
# The first run of this script will take a while, as it's not particularly efficient.
# However, subsequent runs will use a cached hdf5 dataframe, making things faster (at least
# if you're not rerunning the experiment often)
#
# KCH NOTE: This code assumes the following:
# * There are two and only two comparison points (here C and Julia mislabeled 'mpi')
# * .dat files are of the form OP_LANG_PROCCOUNT.dat


class ExperimentFrame:

    langs       = []
    ops         = []
    proc_counts = []
    types       = []
    elms        = 1

    # Find which languages, operations, and proc counts
    def discover_params(self):

        for fname in os.listdir(self.dat_dir):
            basename, ext = os.path.splitext(fname)

            # only count the .dat files
            if not ext == ".dat":
                continue

            op, lang, proc_count, tp = basename.split('_')

            if op not in self.ops:
                self.ops.append(op)
            if lang not in self.langs:
                self.langs.append(lang)
            if proc_count not in self.proc_counts:
                self.proc_counts.append(proc_count)
            if tp not in self.types:
                self.types.append(tp)

            self.proc_counts = sorted(self.proc_counts, key=int)
            self.langs       = sorted(self.langs)
            self.ops         = sorted(self.ops)


    # Is this even a valid experiment combination?
    def check_cfg(self, lang, proc_count, tp):
        if lang not in self.langs or proc_count not in self.proc_counts or tp not in self.types:
            logging.error(f"No such experimental configuration {lang}:{proc_count}:{tp}")
            return False
        return True

    def check_cfg_with_op(self, lang, proc_count, op, tp):
        if lang not in self.langs or proc_count not in self.proc_counts or op not in self.ops or tp not in self.types:
            logging.error(f"No such experimental configuration {lang}:{proc_count}:{tp}")
            return False
        return True


    # Return the mean of all measurements of a particular operation for a
    # particular language/proc_count experiment. This will correspond to the
    # mean of recorded values in one .dat file
    def op_mean(self, lang, proc_count, op, tp):
        self.check_cfg_with_op(lang, proc_count, op, tp)
        rows = self.df.loc[(self.df['op'] == op) & (self.df['lang'] == lang) & (self.df['proc_count'] == proc_count) & (self.df['type'] == tp)]
        if op == 'comms':
            return np.mean(rows['measurement'].values)
        else:
            return np.mean(rows['measurement'].values)*self.elms


    # Return the number of trials for a given experimental configuration
    def op_trials(self, lang, proc_count, op, tp):
        self.check_cfg_with_op(lang, proc_count, op, tp)
        rows = self.df.loc[(self.df['lang'] == lang) & (self.df['proc_count'] == proc_count) & (self.df['op'] == op) & (self.df['type'] == tp)]
        return rows.shape[0]


    # The total of an experiment is calculated as the sum of the means of all ops
    # for that experimental configuration
    def exp_total(self, lang, proc_count, tp):
        total = 0
        for op in self.ops:
            total += self.op_mean(lang, proc_count, op, tp)
        return total


    def __init__(self, path=os.getcwd()):

        self.dat_dir = path

        self.discover_params()

        logging.debug("Languages: {}".format(self.langs))
        logging.debug("Operations: {}".format(self.ops))
        logging.debug("Process Counts: {}".format(self.proc_counts))
        logging.debug("Types: {}".format(self.types))

        # Processing this into a DataFrame takes some time, so we cache the
        # generated frame in a CSV file
        if not os.path.exists(f"{self.dat_dir}/{CACHEFILE}"):

            logging.debug("No cached DataFrame found, processing .dat files")

            self.df = pd.DataFrame(data = {'op': [], 'lang': [], 'proc_count': [], 'type': [], 'measurement-num': [], 'measurement': []})

            i = 0

            for cnt in sorted(self.proc_counts):
                for lang in sorted(self.langs):
                    for op in sorted(self.ops):
                        for tp in sorted(self.types):
                            # Note this assumes a specific file naming convention...
                            logging.debug(f"Processing {lang}:{op}:{cnt}:{tp}")

                            # Skip C + Opt combination, no such thing
                            if tp == 'opt' and lang == "c":
                                continue

                            with open(f"{self.dat_dir}/{op}_{lang}_{cnt}_{tp}.dat", "r") as f:
                                j = 0
                                for line in f.readlines():

                                    # this is dumb. it assumes there will only be *one* unique element coutn
                                    # for all .dat files in the directory you pointed me to
                                    if line[0] == '#':
                                        a,b,c     = line.split(',', maxsplit=2)
                                        elms,val  = b.split('=')
                                        self.elms = int(val)
                                        continue

                                    row = pd.Series(data=[op, lang, cnt, tp, j, int(line)], index=self.df.columns, name=i)
                                    self.df = self.df.append(row)
                                    i += 1
                                    j += 1


            self.df.to_hdf(f"{self.dat_dir}/{CACHEFILE}", key='df', mode='w')

        else:
            logging.debug(f"Discovered cached DataFrame {self.dat_dir}/{CACHEFILE} (delete it to generate new results)")
            self.df = pd.read_hdf(f"{self.dat_dir}/{CACHEFILE}", key='df')


    # Sources
    # * https://stackoverflow.com/a/43567145
    # * https://python-graph-gallery.com/11-grouped-barplot/
    # * https://gist.github.com/ctokheim/6435202a1a880cfecd71
    def plot_stacked(self, barwidth=0.25, of=None):

        f, ax = plt.subplots(1, figsize=(8,8))

        # Set up the color map 
        colors = cm.plasma(np.linspace(0.1, 0.9, len(self.ops)))

        # set up hatches
        hatches = ['/', '.', 'o', '-', 'o', '#', '-', 'O']

        # we have one cluster of bars for each proc count
        bars  = self.proc_counts
        bar_l = range(len(bars))

        # these should not be hard-coded, ideally passed in via command-line as list
        seriesa = {'comms': [], 'flops': [], 'reads': [], 'writes': []}
        seriesb = {'comms': [], 'flops': [], 'reads': [], 'writes': []}
        seriesc = {'comms': [], 'flops': [], 'reads': [], 'writes': []}

        # bar X coords on the graph. The second set is just offset from the first bars by the bar width
        pos1 = np.arange(len(bars))
        pos2 = [x + barwidth for x in pos1]
        pos3 = [x + barwidth for x in pos2]

        # These are the y coords for the bottoms of each component of a bar stack.
        # We'll update them as we go
        bottoma = np.zeros_like(bar_l).astype('float')
        bottomb = np.zeros_like(bar_l).astype('float')
        bottomc = np.zeros_like(bar_l).astype('float')

        for c in self.proc_counts:
            for op in self.ops:
                meana  = self.op_mean('c', c, op, "unopt")
                totala = self.exp_total('c', c, "unopt")
                seriesa[op].append(meana/totala)
                meanb  = self.op_mean('julia', c, op, "unopt")
                totalb = self.exp_total('julia', c, "unopt")
                seriesb[op].append(meanb/totalb)
                meanc  = self.op_mean('julia', c, op, "opt")
                totalc = self.exp_total('julia', c, "opt")
                seriesc[op].append(meanc/totalc)


        print(seriesa)
        for i, op in enumerate(self.ops):
            ax.bar(pos1, seriesa[op], bottom=bottoma, label=op, width=barwidth, edgecolor='black', color=colors[i], alpha=0.8, hatch=hatches[i]*3, linewidth=0.25)
            ax.bar(pos2, seriesb[op], bottom=bottomb, width=barwidth, edgecolor='black', color=colors[i], alpha=0.8, hatch=hatches[i]*3, linewidth=0.25)
            ax.bar(pos3, seriesc[op], bottom=bottomc, width=barwidth, edgecolor='black', color=colors[i], alpha=0.8, hatch=hatches[i]*3, linewidth=0.25)
            bottoma += seriesa[op]
            bottomb += seriesb[op]
            bottomc += seriesc[op]


        FONTSIZE=18

        # replaces X axis labels
        loc=-0.015
        rot=-90
        [ax.text(p-barwidth/2, loc, 'C', fontsize=FONTSIZE, rotation=rot, va='top') for p in pos1]
        [ax.text(p-barwidth/2, loc, 'Julia', fontsize=FONTSIZE, rotation=rot, va='top') for p in pos2]
        [ax.text(p-barwidth/2, loc, 'Julia (opt)', fontsize=FONTSIZE, rotation=rot, va='top') for p in pos3]

        ax.set_xticks([r + barwidth for r in range(len(bars))])
        ax.set_xticklabels(self.proc_counts, size=FONTSIZE)
        ax.set_xlabel("Total MPI Ranks", fontsize=FONTSIZE)
        ax.set_ylabel("Execution Time Breakdown", fontsize=FONTSIZE)
        ax.tick_params(axis='y', labelsize=FONTSIZE-1)

        # move down proc labels so we can describe the language
        ax.tick_params(axis='x', pad=100)

        ax.legend(bbox_to_anchor=(1.0, 1.15), fontsize=FONTSIZE-2, ncol=len(self.ops))

        plt.tight_layout()

        if of is None:
            plt.show()
        else:
            f.savefig(of)


dat_path    = sys.argv[1]
output_file = sys.argv[2]

ef = ExperimentFrame(path=dat_path)
ef.plot_stacked(of=output_file)
