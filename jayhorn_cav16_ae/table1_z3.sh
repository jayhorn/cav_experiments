#!/bin/bash

export LD_LIBRARY_PATH=$(pwd)/native_lib
export DYLD_LIBRARY_PATH=$(pwd)/native_lib

cd benchmarks/cbmc

echo "Running the CBMC benchmarks with Z3"
for file in */ ; do
  if [[ -d "$file" && ! -L "$file" ]]; then
    echo "Running CBMC benchmark $file";
    time java -jar ../../jayhorn.jar -j $file -solver z3 -t 60
  fi;
done


cd ../svcomp_rec
echo "Running the SVCOMP benchmarks with Z3"
for file in */ ; do
    if [[ -d "$file" && ! -L "$file" ]]; then
        echo "Running SVCOMP benchmark $file";
        time java -jar ../../jayhorn.jar -j $file -solver z3 -t 60
    fi;
done

cd ../MinePump/spec1-5/
echo "Running the MinePump benchmarks with Z3"
for file in */ ; do
    if [[ -d "$file" && ! -L "$file" ]]; then
        echo "Running MinePump benchmark $file";
        time java -jar ../../../jayhorn.jar -j $file -solver z3 -t 60
    fi;
done
