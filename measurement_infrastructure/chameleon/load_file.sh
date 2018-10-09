#!/usr/bin/env bash

cd /home/cc/julia-measurement/exp_scripts/multi-node
filename=myhosts

while read -r mchnames
do
	name="$mchnames"
	echo $name
	ssh -qn cc@$name "cd /home/cc/julia-measurement/exp_scripts/multi-node; git pull; mpicc -O3 bsp_mpi.c;cd ping_pong_pckg; mpicc -O3 pp_mpi.c;"
done < "$filename"
