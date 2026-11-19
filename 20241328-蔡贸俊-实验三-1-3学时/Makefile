CC = gcc
CXX = g++
CFLAGS = -std=c11 -Wall -Wextra -O2
CXXFLAGS = -std=c++11 -Wall -Wextra -O2
SKF_LIB = vendor/libgm3000.1.0.so
SKF_LINK = -Lvendor -l:libgm3000.1.0.so -Wl,-rpath,'$$ORIGIN/../vendor'
SDF_SRC = sdf/src/testsdf.c sdf/src/sdf.c

.PHONY: all
all: build/skf-original build/sdf-original build/skf-state build/sdf-info

build:
	mkdir -p $@

build/skf-original: skf/enumdevinfo/main.cpp skf/include/skfapi.h $(SKF_LIB) | build
	$(CXX) -m64 -o $@ $< $(SKF_LINK)

build/sdf-original: $(SDF_SRC) sdf/include/sdf.h | build
	$(CC) $(CFLAGS) -ftrivial-auto-var-init=zero -Isdf/include -o $@ $(SDF_SRC)

build/skf-state: skf/device_state.cpp skf/include/skfapi.h $(SKF_LIB) | build
	$(CXX) $(CXXFLAGS) -m64 -o $@ $< $(SKF_LINK)

build/skf-state-mock: skf/device_state.cpp tests/skf_mock.cpp skf/include/skfapi.h | build
	$(CXX) $(CXXFLAGS) -DLAB_SKF_MOCK -o $@ skf/device_state.cpp tests/skf_mock.cpp

build/sdf-info: sdf/src/device_info.c sdf/include/sdf_device.h sdf/include/sdf.h | build
	$(CC) $(CFLAGS) -Werror -Isdf/include -o $@ $<

build/test-sdf: tests/sdf_test.c sdf/src/device_info.c sdf/include/sdf_device.h sdf/include/sdf.h | build
	$(CC) $(CFLAGS) -Werror -DLAB_SDF_NO_MAIN -Isdf/include -o $@ $(filter %.c,$^)
