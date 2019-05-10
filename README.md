ECE 422: Reliable and Secure Systems Design 
=============
This repository provides the starter kit for the Reliability project. The `docker-images` folder
contains the Dockerfile, a simple application in `Python` and a requirement file including dependencies for
the application. This directory is for your information and reference as the image (simpleweb) has already been build 
and pushed to [Docker Hub](https://hub.docker.com/r/ddsystemsl/simpleweb) repository.

Following steps show how you can prepare the deployment environment on Cybera Cloud; briefly you need to a) provision 
Virtual Machines (VMs) on Cybera b) install Docker on VMs c) create a Swarm cluster of at least two of 
VMs and d) deploy a web application on the Swarm cluster as microservices.

Also this repository contains a base implementation of an HTTP client program that may be customized or extended 
according to your needs. 

Initial steps for accomplishing your project:   

1. Follow the instructions [here](https://github.com/DDSystemLab/cybera-docker-swarm) to create a docker swarm. Try and go over the tutorial to get a feeling on how to work with docker swarm.

2. You need to open the following TCP ports in the `default security group` in Cybera:
        - 22 (ssh), 2376 and 2377 (Swarm), 5000 (Visualization), 8000 (webapp), 6379 (Redis), 8089 (locust load generator)
        - You can do this on Cybera by going to `Network` menu and `Security Groups`. ([See Here](./figures/sg.png))
    
3. On your Swarm manager, clone the repository, and change into it:
    ```bash
    $ git clone https://github.com/nimamahmoudi/ECE422-Proj2-StartKit
    $ cd ECE422-Proj2-StartKit
    ```
4. Run the following to deploy your application:
    ```bash
    $ docker stack deploy --compose-file docker-compose.yml app_name
    ```
5.  Your deployed application should include three microservices:
    1. A visualization microservice that is used to visualize the Swarm cluster nodes and the running microservices. 
        - Open `http://swarm_manager_ip:5000` in your browser. Note that you should have the Cybera VPN client 
        running in order to see the page. ([Sample](./figures/vis.png))
    2. A web application which is linked to a Redis datastore. This simple application shows the number that it has 
        been visited and the period that took it to solve a hard problem. 
        - Open `http://swarm_manager_ip:8000` to see the web application. Try to refresh the page. You should see the 
        hitting number increases one by one and also the computation time to change each time. ([Sample](./figures/app.png))
    3. A Redis microservice which in fact doesn't do anything fancy but to return the number of hitting.

6.  Now, login into your `Client_VM` and clone the http client repository. Run the following command to install the requirements for the load generator:
    ```bash
    $ git clone https://github.com/DDSystemLab/ddsl_load_tester
    $ sudo apt -y install python-pip
    $ pip install ddsl_load_tester/requirements.txt
    ```

7.  Then follow the instructions in the  with one user who sends a request, wait for response, when received the 
    response would think for one second, and then send another request. This cycle goes on as long as the client 
    program is running.
    ```bash
    $ git clone https://github.com/DDSystemLab/ddsl_load_tester
    $ cd ddsl_load_tester/examples
    $ locust --host=http://MASTER_NODE_IP:8000 -f locustfile.py
    ```
    1. You can open up a browser and go to `http://CLIENT_VM_IP:8089` to see the `locust` web interface. Set both the number of users and hatch rate to 1 and
       press the `Start Swarming` button.
       Look at the charts for response time as they are being updated. You should see a response time of about 500ms depending on your computation power.
    3. Generally, this client program creates a number of users that send requests to the server and after receiving 
        the response thinks for the amount of `think_time` and then send a new request.
        The `think_time` can be adjusted in the `locustfile.py`.
    4. If you increase the number of users or decrease the think time, i.e. increasing the workload, the response 
        time should increase.
    5. **Important Note**: for development and testing purposes you may run the client program on your laptop 
    which is a reasonable strategy. However, running the client program for a long time on your laptop might appear as 
    a DoS attack to Cybera firewall which may result in unexpected outcome for your VMs. Therefore, try to run the 
    http client program on the `Client_VM`.
    

8. For more information on how to work with the load generator, go to the [load generator repository](https://github.com/DDSystemLab/ddsl_load_tester).

9. Set the `hatch_rate` to 1 and use the user_sequence in `sequence.py` to generate two sine waves. Run the `sequence.py` to see the example output of running the sequence.
    ```bash
    $ python sequence.py
    ```
    
 Good Luck!
