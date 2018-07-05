#!/bin/bash
for((i=0; i<256; i++)); do
    printf "\e[38;5;${i}m%03d" $i;
    printf '\e[0m';
    [ ! $((($i+1) % 16)) -eq 0 ] && printf ' ' || printf '\n'
done
