CXX=g++
CXXFLAGS= -ggdb3 -O0  -std=c++17 -Wall -pedantic
prog=RESTServer
SRCDIR=src
OBJDIR=build

INCLUDES=include/third-party
SOURCES=$(wildcard $(SRCDIR)/*.cpp)
OBJECTS=$(subst $(SRCDIR)/,$(OBJDIR)/,$(SOURCES:%.cpp=%.o))

$(info OBJECTS: ${OBJECTS})

all: $(OBJECTS)
	$(CXX) $(CXXFLAGS) -o $(OBJDIR)/$(prog) $^ $(LIBS)

$(OBJDIR)/%.o: $(SRCDIR)/%.cpp
	mkdir -p $(OBJDIR)
	$(CXX) $(CXXFLAGS) -o $@ -I $(INCLUDES) -c $<

clean:
	rm -rf build
