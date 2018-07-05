#!/usr/bin/env bash
B="\[$(tput bold)\]"
U="\[$(tput setaf 10)\]"
P="\[$(tput setaf 12)\]"
R="\[$(tput sgr0)\]"

MACHINE="$(cat /etc/hostname)"

export PS1="${B}${U}$USER@$MACHINE${R}:${B}${P}\W${R}$ "
