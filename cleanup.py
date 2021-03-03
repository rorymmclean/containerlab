import time
import sqlite3
import subprocess

DB_STRING = "dockermgr.db"

while True:
    with sqlite3.connect(DB_STRING) as c:
         r_cursor = c.execute('''SELECT id, appname, starttime, default_dur from SUBSCRIPTION 
            where DATETIME('now') > DATETIME(starttime,"+"||default_dur||" minute");''') 
    for row in r_cursor:
        print(row[0])
        ### Kill Lab
        lablaunch = subprocess.run(["bash", "killlab.sh", row[0]], stdout=subprocess.PIPE)
		### Update Table
        with sqlite3.connect(DB_STRING) as c:
             c.execute('DELETE FROM SUBSCRIPTION WHERE ID = :var1',[row[0]])
    time.sleep(120)

