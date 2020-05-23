CC:=gcc
MPICC:=mpicc
CFLAGS:=-O3 -Wall

all: bsp_mpi

bsp_mpi: bsp_mpi.c
	$(MPICC) $(CFLAGS) -o $@ $< 

run: bsp_mpi
	@./sync_bsp_c_binary.sh
	@./git_pull_everywhere.sh
	@./test_bsp.sh 224

clean:
	@rm -f bsp_mpi

.PHONY: clean run
