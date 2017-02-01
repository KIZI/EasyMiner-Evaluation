# EasyMiner-Evaluation

This repository contains prepared evaluation datasets and evaluation scripts for [EasyMiner project](http://easyminer.eu).
    
## Run using docker
Example code in case you want to run evaluation on the same docker server as data mining services of [EasyMiner](http://github.com/kizi/easyminer).

```bash
docker build -t easyminer-evaluation https://github.com/kizi/easyminer-evaluation.git#master
docker run --name easyminer-evaluation -it --network easyminer easyminer-evaluation /bin/bash
```

For EasyMiner state test, and then run the container using command (with replacement of the URL part): 
```bash
# HEADS UP: docker-server is IP address returned by ifconfig, DO NOT USE localhost ! 
HTTP_SERVER_ADDR=<docker-server>
docker run -it --network easyminer easyminer-evaluation python ./easyminercenter/auto/short_test.py --api_url=http://$HTTP_SERVER_ADDR/easyminercenter/api
```     

If you have used the default docker image names defined in the repository [kizi/EasyMiner](https://github.com/KIZI/EasyMiner), the run command is:
```bash
docker run -it --network easyminer easyminer-evaluation python ./easyminercenter/auto/short_test.py --api_url=http://easyminer-frontend/easyminercenter/api
```     
    
In docker image interactive mode, you can find all requested scripts and results in the folder ```/easyminer-evaluation```.
Do not forget to input your API KEY generated in the EasyMiner frontend! 