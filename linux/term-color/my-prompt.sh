#!/usr/bin/env bash
GREEN="\[$(tput setaf 2)\]"
RESET="\[$(tput sgr0)\]"

exec PS1="${GREEN}my prompt${RESET}> "
