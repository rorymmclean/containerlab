import time
import sqlite3
import subprocess
from datetime import datetime
import sys

DB_STRING = "dockermgr.db"

while True:
    sleep_timer = 120
    with sqlite3.connect(DB_STRING) as c:
         r_cursor = c.execute('''SELECT id, appname, starttime, default_dur from SUBSCRIPTION 
            where DATETIME('now') > DATETIME(starttime,"+"||default_dur||" minute") limit 1;''') 
    for row in r_cursor:
        sys.stdout.write(row[0]+' \n')
		### Update Table
        with sqlite3.connect(DB_STRING, 10) as c:
             c.execute('DELETE FROM SUBSCRIPTION WHERE ID = :var1',[row[0]])
             c.commit()
        c.close()     
        ### Kill Lab
        sys.stdout.write('Removed at: '+str(datetime.now())+' \n')
        lablaunch = subprocess.run(["bash", "killlab.sh", row[0]],capture_output=True)
        sleep_timer = 10
    time.sleep(sleep_timer)

