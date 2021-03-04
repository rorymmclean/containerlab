# ContainerLab
Uses Python to deliver a web interface for managing Docker-based virtual labs of Open Source software. 

This product is provided by and maintained by Poc2Ops. It is still under active development at this time. 

## Usage
web.py presents a CherryPy-based web application.
cleanup.py removes any expired labs every two minutes. 

To add a new lab...
1 The SQLite table app must be updated with the lab #, a template to present to user, and other information. 
2 A docker compose file named LABxx is placed in the compose folder. This includes strings replaced during the launch. See LAB01 as an example.
3 A corresponding wiki page (referenced in the template) is required. 
4 The image will probably need some demo configurations and data. In the Mongo situation, public traffic accident data was loaded. This also required that we built a new version of MongoDB which did not use volumes. The demo configurations and data must remain in the container. This container is then committed, tagged, and push as a new repository so it is launched preconfigured. Some container images will load demo configurations when they first load, but this process usually takes longer than we wish for the labs, so preloaded images are used. 

