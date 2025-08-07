
# DevHost

[![Language](https://img.shields.io/badge/language-python-blue.svg?style=flat)](https://www.python.org)





## About

DevHost is a user application that shows devices with one click to monitor their status, along with health and what os is device using in real time. The python script uses ping method to checking devices' ttl amount to learn the os status along with the flask/ninja html communication. 



## How To Use

- for starting the program, you need to install [docker desktop](https://docs.docker.com/get-started/introduction/get-docker-desktop) and [python](https://www.python.org/downloads).
 
- after installing the dependent apps, you can use your terminal to start with command below.

```bash
cd devhost
pip install -r app/requirements.txt
docker compose up -d
flask run
```