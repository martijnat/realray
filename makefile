all:
	cython --embed main.py
	gcc -O3 `pkg-config --libs --cflags python3` main.c -o main.o
	./main.o
