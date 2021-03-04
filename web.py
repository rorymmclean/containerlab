import os, os.path
import random
import string
import cherrypy
import psutil
import shutil
import docker
import sqlite3
import subprocess
import onetimepad 

client = docker.from_env()
DB_STRING = "dockermgr.db"

def check_port(a):
    checkflag = 'Y'
    cont_curr = client.containers.list()
    for row in cont_curr:
        container = client.containers.get(str(row)[12:-1])
        ports = container.attrs['NetworkSettings']['Ports']
        portstr = ports[list(ports.keys())[0]][0]["HostPort"]
        if portstr == str(a):
            checkflag='N'  
    return checkflag

def random_string_generator(str_size, allowed_chars):
    return ''.join(random.choice(allowed_chars) for x in range(str_size))

padchars = string.ascii_letters 

html_top = """<html>
          <head>
            <link href="/static/css/bootstrap/bootstrap.css" rel="stylesheet">
            <link href="/static/css/main.css" rel="stylesheet">
            <link href="/static/css/elements/top-navigation-1.css" rel="stylesheet">
            <link href="/static/css/elements/navbar-2.css" rel="stylesheet">
            <link href="/static/css/ui-elements/buttons.css" rel="stylesheet">
            <style>  
                 .top-navigation-1 {
                    height: 50px;
                 }
                 
                 .footer {
                 	position: fixed;
					bottom: -10px;
					height: 100px;
					min-height: 100px;
					width: 100%;
                 }
                 
                 .corebody {
                    top: 130px;
                    padding: 20px;
                 }
            </style>  
          </head>
          <body>
          <div id="root">
            <div class="row">
             <div data-layout="top-navigation-1" data-background="light" data-navbar="primary" 
               data-top-navigation="primary" data-logo="light" data-left-sidebar="light" 
               data-collapsed="false">
               <div class="navbar navbar-2 d-flex justify-content-around align-items-center flex-nowrap display-4">
                 <div style="width:75px;position:absolute;padding:0px;left:0px;"><a class="flex-nowrap" href="/"><img src="/static/icons/p2c_logo.png" width="60px" height="60px"></a></div>
                 <div>Poc2Ops Open Source Labs</div>
               </div>
               <div class="top-navigation top-navigation-1 d-flex flex-row justify-content-start align-items-center flex-nowrap h6">
                  <ul class="list-unstyled">
                     <li class="list-item"><a class="list-link" href="/">Home</a></li>
                  </ul>
                  <ul class="list-unstyled">
                     <li class="list-item"><a class="list-link" href="/labs">Labs</a></li>
                  </ul>
                  <ul class="list-unstyled">
                     <li class="list-item"><a class="list-link" href="/subscriptions">Subscriptions</a></li>
                  </ul>
               </div>
             </div>
           </div>  """

html_footer = """ 
             <div data-navbar="primary">
             <div class="navbar navbar-2 justify-content-around align-items-center h6 footer" style="min-height:90px;">
                 <div style="width: 33%; height: 90%; float:left;">
                    <b><a href="http://www.poc2ops.com" target="_blank">Poc2Ops.com</a></b><br/>
                    1911 Freedom Drive, Suite 650<br/>
                    Reston, VA  20190
                 </div>
                 <div style="width: 33%; height: 90%; float:center;">
                    Email: <a href="mailto:info@poc2ops.com">info@Poc2Ops.com</a><br/>
                    Phone: 443-280-0781<br/>
                    Fax: 703-935-4603
                 </div>
                 <div style="width: 33%; height: 90%; float:right;">
                    Poc2Ops can help you implement a <I>Open Source First</I> strategy and gain the benefits available from the world of community developed and supported software.
                 </div>
             </div>
             </div>  
          </div>  
          </body>
        </html>"""               

class StringGenerator(object):
    @cherrypy.expose
    def index(self):
        html_body = """
               <div class="row">
               <div class="col-2">&nbsp;
               </div>
               <div class="col-8  corebody">
               <H3>Welcome to Poc2Ops Open Source Software Lab</H3>
               <H5>You are welcome to initiate any of our labs. You will then have the designated subscription time to work with the lab before the instance is terminated. If you require additional time, there is a button on the Subscription page that lets you extend your instances by and additional hour.</H5>
               <H5>Data is not persisted in the labs but demo data is typically provided with every lab. If your lab expires and you relaunch the lab, it will be reset back to its original state.</H5>
               <H5>Whenever you initiate a lab your browser will display a link to the lab and a link to a wiki page that corresponds with that application. If there are specific exercises we recommend you try, they will be described in the wiki page. If you need to obtain these links, there is an icon on the Subscription page you can click to redisplay this information.</H5>
               <H5>If you have any questions, feel free to contact us at <a href = "mailto:info@poc2ops.com">info@poc2ops.com</a> </H5>
               </div>
               </div>"""
             
        html_return = html_top + html_body + html_footer
        return html_return
        
    @cherrypy.expose
    def labs(self):
        target_page = 'http://localhost:8080/launch'
        cherrypy.session['mypad'] = random_string_generator(6, padchars)
        loadrate = float(list(psutil.getloadavg())[1])/float(psutil.cpu_count())
        if loadrate > 1:
            button_flag = 'disabled'
        else:
            button_flag = ''
        html_body = """
            <div class="row">
            <div class="col-3">&nbsp;</div>
            <div class="col-6 corebody">
            <h2 class="text-center">Available Labs</h2>
            <table class="table table-unbordered table-striped thead-inverse">
            <thead><tr><th style="text-align:center;vertical-align:middle;">ID</th><th style="text-align:center;vertical-align:middle;">Lab Name</th><th style="text-align:center">Launch</th></tr></thead>"""
        with sqlite3.connect(DB_STRING) as c:
            r_cursor = c.execute('SELECT id, appname, default_dur from APPS;') 
        for row in r_cursor:
            padapp = onetimepad.encrypt(row[0], cherrypy.session['mypad'])
            html_body = html_body + '<tr><td style="text-align:center;vertical-align:middle;">'+str(row[0])+'</td><td style="text-align:center;vertical-align:middle;">'+str(row[1])+'</td><td style="text-align:center;vertical-align:middle;"><button class="btn btn-primary btn-rounded" '+button_flag+' onclick=''window.location.href="'+target_page+'?app='+padapp+'";''>Launch</button></td></tr>'                          
        html_body = html_body + '</table></div></div>' 
        html_return = html_top + html_body + html_footer
        return html_return


    @cherrypy.expose
    def launch(self, app=10):
        try: cherrypy.session['mypad'] 
        except KeyError: cherrypy.session['mypad'] = 'x'
        myapp = onetimepad.decrypt(app, cherrypy.session['mypad'])
        cherrypy.session['mypad'] = ''
        if myapp[0:3] != 'LAB':
           raise cherrypy.HTTPRedirect("/labs")
        myHostName = "localhost"
        ### Determine Parameters
        with sqlite3.connect(DB_STRING) as c:
            r_cursor = c.execute('SELECT id, appname, default_dur, nbr_ports, message from APPS where id = "'+myapp+'" LIMIT 1;') 
        for row in r_cursor:
            html_core_body = str(row[4]).replace('[APP]', row[1])                          
        ### Determine New Ports and New Name
        port_list = ['']*5
        for z in range(0,row[3]):
            myflag = 'N'
            while myflag == 'N':
                tp=random.randint(55000,59999)
                myflag = check_port(tp)
            port_list[z] = str(tp)
            html_core_body = html_core_body.replace('[PORT'+str(z)+']', str(tp))
        run_name = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k = 6))  
        html_core_body = html_core_body.replace('[NAME]',run_name)
        html_core_body = html_core_body.replace('localhost',myHostName)
        ### Launch Lab
        lablaunch = subprocess.run(["bash", "runlab.sh", row[0], run_name, port_list[0], port_list[1], port_list[2], port_list[3], port_list[4]], stdout=subprocess.PIPE)
		### Save Data
        with sqlite3.connect(DB_STRING) as c:
             c.execute('INSERT INTO SUBSCRIPTION(ID, APPNAME, STARTTIME, DEFAULT_DUR, MESSAGE) VALUES (:var1, :var2, datetime("now"), :var4, :var5)',
                       [row[0]+'-'+run_name, row[1], str(row[2]), html_core_body])
        ### Update Sessions
        try: cherrypy.session['mylabs'] 
        except KeyError: cherrypy.session['mylabs'] = ''
        cherrypy.session['mylabs'] = cherrypy.session['mylabs'] + row[0]+'-'+run_name+','
        ### Output Results
        html_body = """
            <div class="row">
            <div class="col-2">&nbsp;</div>
            <div class="col-8 corebody">"""
        html_body = html_body + html_core_body 
        html_body = html_body + "</div></div>"

        html_return = html_top + html_body + html_footer
        return html_return


    @cherrypy.expose
    def subscriptions(self):
        time_page = 'http://localhost:8080/addtime'
        info_page = 'http://localhost:8080/inforeplay'
        cherrypy.session['mypad'] = random_string_generator(10, padchars)
        try: cherrypy.session['mylabs'] 
        except KeyError: cherrypy.session['mylabs'] = ''
        html_body = """
            <div class="row">
            <div class="col-2">&nbsp;</div>
            <div class="col-8 corebody">
            <h2 class="text-center">Active Subscriptions</h2>
            <table class="table table-unbordered table-striped thead-inverse">
            <thead><tr><th>ID</th><th style="vertical-align:middle;">Application</th><th style="text-align:center;vertical-align:middle;">Start Time</th>
            <th style="text-align:center;vertical-align:middle;">Duration</th><th style="text-align:center;vertical-align:middle;">End Time</th>
            <th style="test-aling:center;vertical-align:middle;">Actions</th></tr>
            </thead>"""
        with sqlite3.connect(DB_STRING) as c:
            r_cursor = c.execute('''SELECT id, appname, starttime, default_dur, 
               DATETIME(starttime,"+"||default_dur||" minute") as endtime, DATETIME('now') as nowtime from SUBSCRIPTION;''') 
        for row in r_cursor:
            if cherrypy.session['mylabs'].find(row[0])>=0:
               padapp = onetimepad.encrypt(row[0], cherrypy.session['mypad'])
               action_str ='<button class="btn btn-primary btn-rounded" onclick=''window.location.href="'+time_page+'?lab='+padapp+'";''>+Time</button>'
               action_str = action_str + '<button class="btn btn-primary btn-rounded" onclick=''window.location.href="'+info_page+'?lab='+padapp+'";''>Info</button>'
            else:
               action_str = ""   
            html_body = html_body + '<tr><td style="vertical-align:middle;">'+row[0]+'</td><td style="text-align:center;vertical-align:middle;">'+ \
                 str(row[1])+'</td><td style="text-align:center;vertical-align:middle;">'+str(row[2])+ \
                 '</td><td style="text-align:center;vertical-align:middle;">'+str(row[3])+ \
                 '</td><td style="text-align:center;vertical-align:middle;">'+str(row[4])+'</td>'+ \
                 '<td style="text-align:center;vertical-align:middle;">'+action_str+'</td></tr>'                          
        html_body = html_body + '</table></div></div>'             
        html_return = html_top + html_body + html_footer
        return html_return


    @cherrypy.expose
    def addtime(self, lab=20):        
        try: cherrypy.session['mypad'] 
        except KeyError: cherrypy.session['mypad'] = 'x'
        mylab = onetimepad.decrypt(lab, cherrypy.session['mypad'])
        cherrypy.session['mypad'] = ''
        if mylab[0:3] != 'LAB':
           raise cherrypy.HTTPRedirect("/subscriptions")
        with sqlite3.connect(DB_STRING) as c:
            r_cursor = c.execute('''
            UPDATE SUBSCRIPTION SET default_dur = round((strftime('%s', DATETIME('now',"+60 minute")) - strftime('%s', STARTTIME))/60,0) where id = :var1''',[mylab])
        raise cherrypy.HTTPRedirect("/subscriptions")
        
        
    @cherrypy.expose
    def inforeplay(self, lab=20):        
        try: cherrypy.session['mypad'] 
        except KeyError: cherrypy.session['mypad'] = 'x'
        mylab = onetimepad.decrypt(lab, cherrypy.session['mypad'])
        cherrypy.session['mypad'] = ''
        if mylab[0:3] != 'LAB':
           raise cherrypy.HTTPRedirect("/subscriptions")
        with sqlite3.connect(DB_STRING) as c:
            r_cursor = c.execute('''SELECT id, appname, starttime, DATETIME(starttime,"+"||default_dur||" minute"), message from SUBSCRIPTION where id = :var1''',[mylab])
        for row in r_cursor:
            html_core_body = """
                <h5>Lab: """+row[0]+"""</h5>
                <h5>Applicaiton Name: """+row[1]+"""</h5>
                <h5>Start Time: """+row[2]+"""</h5>
                <h5>Expiration Time: """+row[3]+"""</h5><h5>Previous Message:</h5><hr>
                """+str(row[4])
        ### Output Results
        html_body = """
            <div class="row">
            <div class="col-2">&nbsp;</div>
            <div class="col-8 corebody">"""
        html_body = html_body + html_core_body 
        html_body = html_body + "</div></div>"
        html_return = html_top + html_body + html_footer
        return html_return
        

    @cherrypy.expose
    def killsessions(self, klab=20):
        ### Kill Lab
        lablaunch = subprocess.run(["bash", "killlab.sh", klab], stdout=subprocess.PIPE)
		### Update Table
        with sqlite3.connect(DB_STRING) as c:
             c.execute('DELETE FROM SUBSCRIPTION WHERE ID = :var1',[klab])
             c.commit()
        raise cherrypy.HTTPRedirect("/subscriptions")
        
        
    @cherrypy.expose
    def stats(self):
        loadrate = round(float(list(psutil.getloadavg())[1])/float(psutil.cpu_count())*100,2)
        freespace = str(round(list(shutil.disk_usage("/"))[2]/(1024*1024*1024),1))+' gb'
        curr_cont = str(len(client.containers.list()))
        curr_images = str(len(client.images.list()))
        
        html_body = """
            <div class="row">
            <div class="col-4">&nbsp;</div>
            <div class="col-4 corebody">
            <table class="table table-unbordered table-striped thead-inverse">
            <thead><tr><th>Statistic</th><th>Metric</th></tr></thead>
            <tr><td>Load Rate (%)</td><td>"""+str(loadrate)+"""</td></tr>
            <tr><td>Free Space</td><td>"""+freespace+"""</td></tr>
            <tr><td># Containers</td><td>"""+curr_cont+"""</td></tr>
            <tr><td># Images</td><td>"""+curr_images+"""</td></tr>
            </table></div></div>
            """
        html_return = html_top + html_body + html_footer
        return html_return

    @cherrypy.expose
    def session(self): 
        try: cherrypy.session['mylabs'] 
        except KeyError: cherrypy.session['mylabs'] = ''       
        try: cherrypy.session['mypad'] 
        except KeyError: cherrypy.session['mypad'] = ''       
        html_body = """
            <div class="row">
            <div class="col-4">&nbsp;</div>
            <div class="col-4 corebody">
            <h5>Labs launched by this session: 
            """+cherrypy.session['mylabs']+"""</h5>
            <h5>Last mypad session value: 
            """+cherrypy.session['mypad']+"""</h5>
            </div></div>
            """
        html_return = html_top + html_body + html_footer
        return html_return



if __name__ == '__main__':
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './src'
        }
    }
    cherrypy.quickstart(StringGenerator(), '/', conf)