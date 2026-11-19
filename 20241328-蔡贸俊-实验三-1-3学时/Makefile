CC = gcc
CXX = g++
CFLAGS = -std=c11 -Wall -Wextra -O2
CXXFLAGS = -std=c++11 -Wall -Wextra -O2
SKF_LIB = vendor/libgm3000.1.0.so
SKF_LINK = -Lvendor -l:libgm3000.1.0.so -Wl,-rpath,'$$ORIGIN/../vendor'
SDF_SRC = sdf/src/testsdf.c sdf/src/sdf.c

.PHONY: all
all: build/skf-original build/sdf-original

build:
	mkdir -p $@

build/skf-original: skf/enumdevinfo/main.cpp skf/include/skfapi.h $(SKF_LIB) | build
	$(CXX) -m64 -o $@ $< $(SKF_LINK)

build/sdf-original: $(SDF_SRC) sdf/include/sdf.h | build
	$(CC) $(CFLAGS) -ftrivial-auto-var-init=zero -Isdf/include -o $@ $(SDF_SRC)
