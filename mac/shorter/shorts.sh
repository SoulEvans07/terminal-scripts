#!/usr/bin/env bash
pwd=`pwd`
# echo "pwd: $pwd"
if [[ $pwd =~ ^$HOME.* ]]
then
	from_home=true
	pwd="~${pwd#$HOME}" 
fi
# echo "pwd: $pwd"
slash="${pwd//[^\/]}"
count=${#slash}
# echo "slashes: $slash"
# echo "count: $count"

if (( $count >= 3 ))
then
	pwd="${pwd//[a-zA-Z0-9]*\//.../}"
fi

echo $pwd