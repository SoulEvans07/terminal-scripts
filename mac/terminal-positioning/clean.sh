#/usr/bin/env bash
cs_workdir="~/workspace/cleansheet"

position_window() {
    osascript -e "tell application \"Terminal\"
        set position of window id $1 to {$2, $3}
        set size of window id $output to {$4, $5}
    end tell"
}

get_last_word() {
    echo $6
}

output=$(osascript -e "tell application \"Terminal\" to do script \"cd $cs_workdir/api; shortr; npm run build-watch\"")
output=$(get_last_word $output)
position_window $output 862 600 815 520

sleep 10s

output=$(osascript -e "tell application \"Terminal\" to do script \"cd $cs_workdir/api; shortr; ./start_server.sh perf inspectb\"")
output=$(get_last_word $output)
position_window $output 862 0 815 520

sleep 5s

output=$(osascript -e "tell application \"Terminal\" to do script \"cd $cs_workdir/client; shortr; npm start\"")
output=$(get_last_word $output)
position_window $output 47 600 815 520
