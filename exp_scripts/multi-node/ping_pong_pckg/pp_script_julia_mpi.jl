import MPI
@everywhere include("pp_julia_mpi.jl")


    iters = 100
    doit_mpi(iters)    
