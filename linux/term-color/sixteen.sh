#!/usr/bin/env bash
for C in {0..16}; do
    tput setaf $C
    tput bold
    echo "soul $C"
done
tput sgr0
echo
