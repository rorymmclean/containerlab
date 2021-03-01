import os, os.path
import random
import string
import cherrypy
import psutil
import shutil
import docker
import sqlite3
client = docker.from_env()
DB_STRING = "dockermgr.db"

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
                    position: absolute;
                    top: 130px;
                    padding: 20px;
                 }
            </style>  
          </head>
          <body>
          <div id="root">
             <div data-layout="top-navigation-1" data-background="light" data-navbar="primary" 
               data-top-navigation="primary" data-logo="light" data-left-sidebar="light" 
               data-collapsed="false">
               <div class="navbar navbar-2 d-flex justify-content-around align-items-center flex-nowrap display-4">
                 Poc2Ops Open Source Labs
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
                  <ul class="list-unstyled">
                     <li class="list-item"><a class="list-link" href="/stats">Stats</a></li>
                  </ul>
               </div>
             </div>"""

html_footer = """ 
             <div data-navbar="primary">
             <div class="navbar navbar-2 justify-content-around align-items-center h6 footer" style="min-height:90px;">
                 <div style="width: 33%; height: 90%; float:left;">
                    <h5 style="margin-bottom: 0;"><a href="http://www.poc2ops.com" target="_blank">Poc2Ops.com</a></h5>
                    Street<br/>
                    City, State 12345
                 </div>
                 <div style="width: 33%; height: 90%; float:center;">
                    Email: <a href="mailto:info@poc2ops.com">info@Poc2Ops.com</a><br/>
                    Phone: TBD<br/>
                    Fax: 703-935-4603
                 </div>
                 <div style="width: 33%; height: 90%; float:right;">
                    Poc2Ops can help you implement a <I>Open Source First</I> strategy.<br/>

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
               <div class="col main corebody">
               <H3>Welcome to Poc2Ops Open Source Software Lab</H3>
               <H5>You are welcome to initiate any of our labs. You will then have the designated subscription time to work with the lab before the instance is terminated.<br>Relaunching the lab will reset the lab to its original state.</H5>
               <H5>When you initiate a lab you will receive a link to the application and a reference to a wiki page that corresponds to that application.</H5>
               <H5>If you have any questions, feel free to contact us at <a href = "mailto:info@poc2ops.com">info@poc2ops.com</a> </H5>
               </div>"""
             
        html_return = html_top + html_body + html_footer
        return html_return
        
    @cherrypy.expose
    def labs(self):
        loadrate = float(list(psutil.getloadavg())[1])/float(psutil.cpu_count())
        if loadrate > 1:
            button_flag = 'disabled'
        else:
            button_flag = ''
        html_body = """<div class="col-6 corebody"><h2 class="text-center">Available Labs</h2><table class="table table-unbordered table-striped thead-inverse"><thead><tr><th>Lab Name</th><th style="text-align:center">Duration</th><th style="text-align:center">Launch</th></tr></thead>"""
        with sqlite3.connect(DB_STRING) as c:
            r_cursor = c.execute('SELECT id, appname, default_dur from APPS;') 
        for row in r_cursor:
            html_body = html_body + '<tr><td>'+str(row[1])+'</td><td style="text-align:center">'+str(row[2])+'</td><td style="text-align:center"><button class="btn btn-primary btn-rounded" '+button_flag+' app="'+str(row[0])+'">Launch</button></td></tr>'                          
        html_body = html_body + """</table></div>"""            
        html_return = html_top + html_body + html_footer
        return html_return


    @cherrypy.expose
    def subscriptions(self):
        html_body = """<div class="col-8 corebody"><h2 class="text-center">Active Subscriptions</h2><div class="table-widget-4"><table class="table table-unbordered table-striped thead-inverse"><thead><tr><th>ID</th><th>Application</th><th style="text-align:center">Start Time</th><th style="text-align:center">Duration</th><th style="text-align:center">End Time</th></tr></thead>"""
        with sqlite3.connect(DB_STRING) as c:
            r_cursor = c.execute('''SELECT id, appname, starttime, default_dur, 
               DATETIME(starttime,"+"||default_dur||" minute") as endtime, DATETIME('now') as nowtime from SUBSCRIPTION;''') 
        for row in r_cursor:
            html_body = html_body + '<tr><td>'+row[0]+'</td><td>'+str(row[1])+'</td><td style="text-align:center">'+str(row[2])+'</td><td style="text-align:center">'+str(row[3])+'</td><td style="text-align:center">'+str(row[4])+'</td></tr>'                          
        html_body = html_body + "</table></div></div>"             
        html_return = html_top + html_body + html_footer
        return html_return

    @cherrypy.expose
    def stats(self):
        loadrate = round(float(list(psutil.getloadavg())[1])/float(psutil.cpu_count())*100,2)
        freespace = str(round(list(shutil.disk_usage("/"))[2]/(1024*1024*1024),1))+' gb'
        curr_cont = str(len(client.containers.list()))
        curr_images = str(len(client.images.list()))
        
        html_body = """<div class="col-4 corebody">
            <table class="table table-unbordered table-striped thead-inverse">
            <thead><tr><th>Statistic</th><th>Metric</th></tr></thead>
            <tr><td>Load Rate (%)</td><td>"""+str(loadrate)+"""</td></tr>
            <tr><td>Free Space</td><td>"""+freespace+"""</td></tr>
            <tr><td># Containers</td><td>"""+curr_cont+"""</td></tr>
            <tr><td># Images</td><td>"""+curr_images+"""</td></tr>
            </table></div>"""
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