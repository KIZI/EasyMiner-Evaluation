# EasyMiner-Evaluation

This repository contains prepared evaluation datasets and evaluation scripts for [EasyMiner project](http://easyminer.eu).
    
## Run using docker
Example code in case you want to run evaluation on the same docker server as data mining services of [EasyMiner](http://github.com/kizi/easyminer).

```bash
docker build -t easyminer-evaluation https://github.com/kizi/easyminer-evaluation.git#master -f docker/Dockerfile
docker run --name easyminer-evaluation -it --network easyminer easyminer-evaluation /bin/bash
```
    
In docker image interactive mode, you can find all requested scripts and results in the folder ```/easyminer-evaluation```.
Do not forget to input your API KEY generated in the EasyMiner frontend! 