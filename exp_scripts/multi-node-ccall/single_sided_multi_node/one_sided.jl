using MPI
import Distributed
import Compat

mutable struct wintype
	rank::Int64
	N::Int64
	iters::Int64
	gets::Int64
	puts::Int64
	comm
end


function win_put(a)
	rank = a.rank
	N = a.N
	comm = a.comm
	win = MPI.Win()
	gets = a.gets
	buf = fill(Int(rank),N)
	received = fill(-1,N)
	println(N ,"\n", buf, "\n", received,"\n")
	MPI.Win_create(buf, MPI.INFO_NULL, comm, win)
	MPI.Win_fence(0, win)
	if rank == 1 
		start = time_ns()
	end
	for i = 1:gets
		if rank==N-1
			MPI.Put(received, 0, win)
			MPI.Win_fence(0, win)
		else 
			MPI.Put(received, (rank+1), win)
			MPI.Win_fence(0, win)
		end	
	end
	MPI.Barrier(comm)
	if rank == 1
		stop = time_ns()
		file =  "test_put_x10.txt"
		fs = open(file, "a")
		int = stop - start
	        Distributed.fetch(Distributed.@spawnat(1, write(fs,"$(stop- start)\n")))
		close(fs)
		println(rank, " ----> ",received)
	end
end
function win_get(a)
	rank = a.rank
	N = a.N
	comm = a.comm
	win = MPI.Win()
	gets = a.gets
	buf = fill(Int(rank),N)
	received = fill(-1,N)
	println(N ,"\n", buf, "\n", received,"\n")
	MPI.Win_create(buf, MPI.INFO_NULL, comm, win)
	MPI.Win_fence(0, win)
	if rank == 1 
		start = time_ns()
	end
	for i = 1:gets
		if rank==N-1
			MPI.Get(received, 0, win)
			MPI.Win_fence(0, win)
		else 
			MPI.Get(received, (rank+1), win)
			MPI.Win_fence(0, win)
		end	
	end
	MPI.Barrier(comm)
	if rank == 1
		stop = time_ns()
		file =  "test_x10.txt"
		fs = open(file, "a")
		int = stop - start
	        Distributed.fetch(Distributed.@spawnat(1, write(fs,"$(stop- start)\n")))
		close(fs)
		println(rank, " ----> ",received)
	end
end
function put_size(a)
    	min = 8
    	max = 1024*1024
	rank = a.rank
	N = a.N
	comm = a.comm
	win = MPI.Win()
	gets = a.gets
	received = fill(-1,N)
    	i = min
    	while i <= max
        	buf=Array{Int8,1}(undef,i)
		MPI.Win_create(buf, MPI.INFO_NULL, comm, win)
		MPI.Win_fence(0, win)
        	if a.rank == 1
            		file_suffix = "_"*string(i)*".dat"
            		fs = open("put_size"*file_suffix, "a")
        	      	start = time_ns()
	        end

		for j = 1:gets
			if rank==N-1
				MPI.Put(received, 0, win)
				MPI.Win_fence(0, win)
			else 
				MPI.Put(received, (rank+1), win)
				MPI.Win_fence(0, win)
			end	
		end
		MPI.Barrier(comm)

        	if a.rank == 1

            	# end timer print out result
            		stop  = time_ns()
	        	Distributed.fetch(Distributed.@spawnat(1, write(fs,"$(stop- start)\n")))
            		close(fs)
            		println("time written")
       	 	end
    		i = i *2
    
   	 end
end

function get_size(a)
    	min = 8
    	max = 1024*1024
	rank = a.rank
	N = a.N
	comm = a.comm
	win = MPI.Win()
	gets = a.gets
	received = fill(-1,N)
    	i = min
    	while i <= max
        	buf=Array{Int8,1}(undef,i)
		MPI.Win_create(buf, MPI.INFO_NULL, comm, win)
		MPI.Win_fence(0, win)
        	if a.rank == 1
            		file_suffix = "_"*string(i)*".dat"
            		fs = open("win_size"*file_suffix, "a")
        	      	start = time_ns()
	        end

		for j = 1:gets
			if rank==N-1
				MPI.Get(received, 0, win)
				MPI.Win_fence(0, win)
			else 
				MPI.Get(received, (rank+1), win)
				MPI.Win_fence(0, win)
			end	
		end
		MPI.Barrier(comm)

        	if a.rank == 1

            	# end timer print out result
            		stop  = time_ns()
	        	Distributed.fetch(Distributed.@spawnat(1, write(fs,"$(stop- start)\n")))
            		close(fs)
            		println("time written")
       	 	end
    		i = i *2
    
   	 end
end

function driver(iters, gets, puts)
	MPI.Init()
	rank = MPI.Comm_rank(MPI.COMM_WORLD)
	N  = MPI.Comm_size(MPI.COMM_WORLD)
	comm = MPI.COMM_WORLD
	a = wintype(rank, N, iters, gets, puts, comm)
	for i = 1:iters
		win_put(a)
		win_get(a)
	end
	MPI.Finalize()
end

driver(100, 50000, 50000)
