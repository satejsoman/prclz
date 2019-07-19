#!/bin/bash
input=$1.txt
mkdir $1
while IFS= read -r line
do 
  wget "$line" -P $1
done < "$input"
