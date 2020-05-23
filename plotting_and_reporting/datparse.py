#!/usr/bin/python3

""" Dat Parse

Usage:
    datparse.py [options] -p <dirs>...

Options:
    -h --help            Show this screen
    -V --version         Show version
    -o --output=<file>   Output file (defaults to stdout)
    -p --path=<path>...  Paths to search for .exp files (experiment outputs)

"""

import pandas as pd
import re
from io import StringIO
from docopt import docopt
from os.path import isfile, join
from os import scandir

# takes in a .exp file and creates a pandas DataFrame from it
def slurp_file(f, df):
    entry = {}
    entry['name'] = f.name
    with open(f) as file:
        for line in file:
            match = re.match("^Benchmark Time.+Total=(\d+.*\d*)", line)
            if match:
                entry['total-time'] = match.group(1)
            match = re.search("Distributed Processes=(\d+)", line)
            if match:
                entry['total-procs'] = match.group(1)
            match = re.search("LANG=(\w+)", line)
            if match:
                entry['lang'] = match.group(1)
            match = re.search("Global nx=(\d+)", line)
            if match:
                entry['gnx'] = match.group(1)
            match = re.search("Global ny=(\d+)", line)
            if match:
                entry['gny'] = match.group(1)
            match = re.search("Global nz=(\d+)", line)
            if match:
                entry['gnz'] = match.group(1)
            match = re.search("npx=(\d+)", line)
            if match:
                entry['npx'] = match.group(1)
            match = re.search("npy=(\d+)", line)
            if match:
                entry['npy'] = match.group(1)
            match = re.search("npz=(\d+)", line)
            if match:
                entry['npz'] = match.group(1)
            match = re.search("reference iterations=(\d+)", line)
            if match:
                entry['reference-iters'] = match.group(1)
            match = re.search("Optimization phase=(\d+.*\d+)", line)
            if match:
                entry['time-optimization'] = match.group(1)
            match = re.search("DDOT=(\d+.*\d+)", line)
            if match:
                entry['time-ddot'] = match.group(1)
            match = re.search("WAXPBY=(\d+.*\d+)", line)
            if match:
                entry['time-waxpby'] = match.group(1)
            match = re.search("SpMV=(\d+.*\d+)", line)
            if match:
                entry['time-spmv'] = match.group(1)
            match = re.search("MG=(\d+.*\d+)", line)
            if match:
                entry['time-mg'] = match.group(1)
            match = re.search("Raw Total B/W=(\d+.*\d+)", line)
            if match:
                entry['raw-mem-bw'] = match.group(1)
            match = re.search("Raw Total=(\d+.*\d+)", line)
            if match:
                entry['raw-gflops'] = match.group(1)
            match = re.search("LANG=(\w+)", line)

    df.append(entry)

if __name__ ==  '__main__':

    args = docopt(__doc__, version='Dat Parse 0.1 (c) Kyle C. Hale')

    df = []

    for i in args['--path']:

        for f in scandir(i):
            if isfile(f) and f.name.endswith(".exp"):
                slurp_file(f, df)

    frame = pd.DataFrame(df)

    # if we don't get an output file specified, just print
    # the CSV out to stdout
    if args['--output']:
        frame.to_csv(args['--output'], index=False)
    else:
        print(frame.to_csv(index=False))
