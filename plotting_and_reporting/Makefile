
all: plots

plots: prep context-switches task-creations spawn-fetch ping-pong condvars channels bsp-stacked-10 bsp-stacked-100

prep: .prepped.txt

.prepped.txt:
	@./prep.sh

context-switches: data/context-switches/julia_ctx_switch.dat data/context-switches/c_ctx_switch.dat context_switch_plot.py
	python3 ./context_switch_plot.py

task-creations: data/task-creations/c_task_create_tput.dat data/task-creations/julia_task_create_tput.dat task_creation_tput_plot.py
	python3 ./task_creation_tput_plot.py

ping-pong: data/pingpong/c_and_julia/* data/pingpong/c_and_julia_opt/* pingpong_lineplot.py
	python3 ./pingpong_lineplot.py

spawn-fetch: data/spawn-fetch/spawn_fetch.csv spawn_fetch_grouped_bar.py
	python3 ./spawn_fetch_grouped_bar.py

condvars: data/condvar/*.dat cond_plot.py
	python3 ./cond_plot.py

channels: data/channels/*.dat channel_plot.py
	python3 ./channel_plot.py

bsp_10_deps: data/bsp/comms_10/*.dat
	rm -f data/bsp/comms_10/*.expframe.*

bsp_100_deps: data/bsp/comms_100/*.dat
	rm -f data/bsp/comms_100/*.expframe.*

bsp-stacked-10: bsp_stacked.py bsp_10_deps
	python3 ./bsp_stacked.py data/bsp/comms_10 bsp-stacked-comms-10.pdf

bsp-stacked-100: bsp_stacked.py bsp_100_deps
	python3 ./bsp_stacked.py data/bsp/comms_100 bsp-stacked-comms-100.pdf

clean:
	@rm -f *.pdf

.PHONY: all clean plots prep
