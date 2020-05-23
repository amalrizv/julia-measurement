#!/bin/sh
for i in 01 02 03 04 05 06 08 12 13 14 15 16 17 18
do
	echo "torusnode$i"
	scp bsp_mpi torusnode$i:/home/arizvi/julia-measurement/exp_scripts/multi-node
done
