#!/bin/bash
N=$1
for (( i=14 ; i<=$1 ;i=i*2 ))
do
       echo "Processes per node: $i"
       mpirun -map-by node --hostfile myhosts -np $i ./bsp_mpi          -i 100 -e 10 -f 1000000 -r 500000 -w 500000 -c 100
       mpirun -map-by node --hostfile myhosts -np $i julia bsp_julia.jl -i 100 -e 10 -f 1000000 -r 500000 -w 500000 -c 100
       mpirun -map-by node --hostfile myhosts -np $i julia bsp_julia.jl -i 100 -e 10 -f 1000000 -r 500000 -w 500000 -c 100 -o
done

