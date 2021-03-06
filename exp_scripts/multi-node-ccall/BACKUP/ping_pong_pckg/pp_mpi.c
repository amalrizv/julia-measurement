#include <stdio.h>
#include <time.h>
#include <stdlib.h>
#include <mpi.h>
struct bsp_type {
    int size;
    int rank;
    int iters;
    MPI_Comm comm_w;
};

static void do_pp(int iters, int throwout);
static void do_ping_pong(struct bsp_type *a);


#define MIN_PING_PONG_SIZE 8 // in bytes
#define MAX_PING_PONG_SIZE (1024*1024) // up to 1MB

#define FNAME_MAX 128

static void do_ping_pong(struct bsp_type *a)
{
    printf("in ping pong %d\n", a->rank);
    int i;
    FILE *fs = NULL;
    struct timespec start;
    struct timespec end;
    int tag = 10;

    /* bi-directional test, only two ranks supported */
    int ping = 0;
    int pong = 1;
    int j = 1;

    for (i = MIN_PING_PONG_SIZE; i <= MAX_PING_PONG_SIZE; i *= 2) {

        unsigned char *arr = malloc(i);

        if (!arr) {
            fprintf(stderr, "Could not allocate array in %s\n", __func__);
            return;
        }

        /* start timer */
        if (a->rank == ping) {
            char filename[FNAME_MAX] = {0};
            snprintf(filename, FNAME_MAX, "comm_size_c_%d.dat", i);
            fs = fopen(filename,"a");
	    if (!fs) {
		    fprintf(stderr, "Could not open dat file\n");
		    return;
	    }
	    clock_gettime(CLOCK_REALTIME, &start);
          }

        /* PING */
        if (a->rank == ping) {
            if (MPI_Send(arr, i, MPI_BYTE, pong, tag+j, a->comm_w) != MPI_SUCCESS) {
                fprintf(stderr, "MPI_Send (ping stage) unsuccessful\n");
            }
        } else if (a->rank == pong) {
            if (MPI_Recv(arr, i, MPI_BYTE, ping, tag+j, a->comm_w, MPI_STATUS_IGNORE) != MPI_SUCCESS) {
                fprintf(stderr, "MPI_Recv (ping stage) unsuccessful\n");
            }
           
        }
        /* PONG */
        if (a->rank == pong) {
            if (MPI_Send(arr, i, MPI_BYTE, ping, tag*j, a->comm_w) != MPI_SUCCESS) {
                printf("MPI_Send (pong stage) unsuccessful\n");
            }
        } else if (a->rank == ping) {
            if (MPI_Recv(arr, i, MPI_BYTE, pong, tag*j, a->comm_w, MPI_STATUS_IGNORE) != MPI_SUCCESS) {
                printf("MPI_Recv (pong stage) unsuccessful\n");
            }
        }

        if (a->rank == ping) {
              clock_gettime(CLOCK_REALTIME, &end);
              long s_ns = start.tv_sec*1000000000 + start.tv_nsec;
              long e_ns = end.tv_sec*1000000000 + end.tv_nsec;
              fprintf(fs,"%lu\n", e_ns - s_ns);
              fclose(fs);
          }

        /* synch up before trial for next buffer size */
        //MPI_Barrier(a->comm_w);
	MPI_Barrier(MPI_COMM_WORLD);
	j++;
    }
    //MPI_Barrier(a->comm_w);
    printf("out of ping pong\n");

}

static void do_pp(int iters, int throwout)
{
    
    int max_len;
    int rank;
    int size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    int j;
    char processorname[MPI_MAX_PROCESSOR_NAME];
    MPI_Get_processor_name(processorname,&max_len);

    printf("Hello world!  I am process number: %d on processor %s\n", rank, processorname);
    struct bsp_type a = { size, rank, iters, MPI_COMM_WORLD};
    for (j =0; j<iters+throwout;j++) {
            do_ping_pong(&a);
    }
}


int 
main (int argc, char ** argv)
{

    MPI_Init(&argc, &argv);
//    doit(iters, reads, writes, comms);
    do_pp(100, 10);

    MPI_Finalize();
    //printf("done with finalize\n");
    
    return 0;
}

