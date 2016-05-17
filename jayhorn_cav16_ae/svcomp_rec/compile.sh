#!/bin/bash

for file in */ ; do 
  if [[ -d "$file" && ! -L "$file" ]]; then
    echo "Compiling $file"; 
    cd $file
    javac -g *.java 
    cd ..
  fi; 
done