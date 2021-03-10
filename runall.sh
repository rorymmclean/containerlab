nohup python3 -u web.py > web.log 2>&1 & echo $! > web.pid
nohup python3 -u cleanup.py > cleanup.log 2>&1 & echo $! > cleanup.pid
