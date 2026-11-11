# Builds the C++ backend as a shared library the Python UI loads via ctypes.
CXX      ?= c++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -fPIC

ifeq ($(shell uname -s),Darwin)
  LIB := build/libdemoapi.dylib
  LDFLAGS += -dynamiclib
else
  LIB := build/libdemoapi.so
  LDFLAGS += -shared
endif

.PHONY: all run clean
all: $(LIB)

$(LIB): cpp/demo_api.cpp cpp/demo_api.h
	@mkdir -p build
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -o $@ cpp/demo_api.cpp

run: $(LIB)
	python3 app.py

clean:
	rm -rf build
