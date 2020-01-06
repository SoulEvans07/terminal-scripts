#/usr/bin/env bash
osascript -e 'tell application "Terminal" to do script "cd ~/workspace/cleansheet/api; shortr; npm run build-watch"'
sleep 10s
osascript -e 'tell application "Terminal" to do script "cd ~/workspace/cleansheet/api; shortr; ./start_server.sh perf inspectb"'
sleep 5s
osascript -e 'tell application "Terminal" to do script "cd ~/workspace/cleansheet/client; shortr; npm start"'
