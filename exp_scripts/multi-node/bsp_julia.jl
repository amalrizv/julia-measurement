using Distributed
using MPI
using DocOpt
import MPI: Status


include("cli.jl")

mutable struct bsptype
    size     :: Int64
    rank     :: Int64
    iters    :: Int64
    elements :: Int64
    flops    :: Int64
    reads    :: Int64
    writes   :: Int64
    comms    :: Int64
    is_opt   :: Bool
    comm_world
end

const MYCOMMWORLD = Cint(1140850688)
function MySend(buf::Array{Int64}, cnt::Cint, dst::Cint, tag::Cint, comm::Cint)
	ccall((:MPI_Send, "libmpich"), Cint, 
				   (Ptr{Cchar}, Cint, Cint, Cint, Cint, Cint),
				   Base.cconvert(Ptr{Cchar}, buf), 
				   cnt,
				   Cint(1275068673),
				   dst,
				   tag,
				   comm)
	return nothing
end

function MyRecv!(buf::Array{Int64}, cnt::Cint, src::Cint, tag::Cint, comm::Cint)
	stat_ref = Ref{Status}(MPI.STATUS_EMPTY)
	ccall((:MPI_Recv, "libmpich"), Cint, 
				   (Ptr{Cchar}, Cint, Cint, Cint, Cint, Cint, Ptr{Status}),
				   Base.cconvert(Ptr{Cchar}, buf), 
				   cnt,
				   Cint(1275068673),
				   src,
				   tag,
				   comm,
				   stat_ref)
	return stat_ref[]
end

function dump_exp_prefix(fhandle, a)
	write(fhandle, "# iters=$(a.iters),elements=$(a.elements),flops=$(a.flops),comms=$(a.comms),reads=$(a.reads),writes=$(a.writes),is_opt=$(a.is_opt)\n")
end


function gen_fname(op_type::String, procs, is_opt)

	str = op_type*"_julia_"*string(procs)

	if is_opt
	    str *= "_opt"
	else
	    str *= "_unopt"
	end

	return str * ".dat"
end

function do_flops(a)

    i          = Int64
    x::Float64 = 1995.1937
    sum        = x
    val        = Float64
    mpy        = Float64

    if a.rank == 0
	fname     = gen_fname("flops", a.size, a.is_opt)
        fs        = open(fname, "a")
	dump_exp_prefix(fs, a)
        start     = time_ns()
    end

    # do the actual floating point math
    for i=1 :a.flops
    	val = x
	    mpy = x
    	sum = sum + mpy*val
    end

    if a.rank == 0
        stop  = time_ns()
        write(fs,"$(stop- start)\n")
        close(fs)
    end
    sum
end


function do_reads(a)

    mymem     = Array{Int64,1}(undef, a.reads)
    sum       = Float64
    x         = Float64
    i         = Int64

    if a.rank == 0
        fname     = gen_fname("reads", a.size, a.is_opt)
        fs        = open(fname, "a")
	dump_exp_prefix(fs, a)
        start     = time_ns()
    end

    # do the actual reads
    for i=1:a.reads
	    sum = mymem[i]
    end

    if a.rank == 0
        stop      = time_ns()
        write(fs,"$(stop- start)\n")
        close(fs)
    end
    sum

end


function do_writes(a)

    x::Float64   = 93.0
    sum::Float64 = x

    mymem = Array{Int64,1}(undef,a.writes)


    if a.rank == 0
        fname     = gen_fname("writes", a.size, a.is_opt)
        fs        = open(fname, "a")
	dump_exp_prefix(fs, a)
        start = time_ns()
    end

    # do the actual writes
    for i=1:a.writes
    	mymem[i] = sum
    end

    if a.rank == 0
        stop       = time_ns()
        write(fs,"$(stop- start)\n")
        close(fs)
    end
end


function do_computes(a)

    i  = Int64
    for i=1:a.elements

    	do_flops(a)
        do_reads(a)
    	do_writes(a)

    end

end


function do_comms(a)

    b         = Array{Int64,1}(undef, a.comms)

    if a.rank == a.size-1
        fwd = 0
    else
        fwd = a.rank+1
    end

    if a.rank == 0
        bck = a.size-1
    else
        bck = a.rank-1
    end

    if a.rank == 0
	fname     = gen_fname("comms", a.size, a.is_opt)
        fs        = open(fname, "a")
	dump_exp_prefix(fs, a)
        start     = time_ns()
    end

    # do the actual communication phase
    for i=1:a.comms
	if a.is_opt
	    MySend(b, Base.cconvert(Cint, length(b)), Base.cconvert(Cint, fwd), Cint(10+i), MYCOMMWORLD)
	else
	    MPI.Send(b, fwd, 10+i, a.comm_world)
	end
        a1 = Array{Int64,1}(undef, a.comms)
	if a.is_opt
	    MyRecv!(a1, Base.cconvert(Cint, length(a1)), Base.cconvert(Cint, bck), Cint(10+i), MYCOMMWORLD)
	else 
	    MPI.Recv!(a1, bck, 10+i, a.comm_world)
	end

        # wait for everyone to finish
	MPI.Barrier(a.comm_world)
    end

    if  a.rank == 0
        stop      = time_ns()
        write(fs,"$(stop- start)\n")
        close(fs)
    end


end

function doit_mpi(iters, elements, flops, reads, writes, comms, is_opt)
    MPI.Init()

    bspcomm = MPI.COMM_WORLD


    rank = MPI.Comm_rank(bspcomm)
    size = MPI.Comm_size(bspcomm)

    a = bsptype(size, rank, iters, elements, flops, writes, reads, comms, is_opt, bspcomm)
    
    for i=1:iters
    	do_computes(a)
        do_comms(a)
    end

    MPI.Finalize()
end

args = docopt(doc, version=v"0.0.2")

iters  = parse(Int, args["--iterations"])
elms   = parse(Int, args["--elements"])
flops  = parse(Int, args["--flops"])
reads  = parse(Int, args["--reads"])
writes = parse(Int, args["--writes"])
comms  = parse(Int, args["--comms"])
is_opt = args["--is-opt"]

# actual invocation
doit_mpi(iters, elms, flops, reads, writes, comms, is_opt)
