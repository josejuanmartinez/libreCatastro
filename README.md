# libreCATASTRO
An opensource, MIT-licensed application that scraps the official Spanish 
Cadaster registry and stores information in Elastic Searcher.

![libreCatastro example](https://drive.google.com/uc?export=view&id=1kisisDNmrQ5ZBWNzqnSzF0AsHu6-zS-P "libreCadsatro example")

**Features**

_Scrapping_
* From XML webservices. Check http://www.catastro.meh.es/ws/Webservices_Libres.pdf
* From HTML webpages.
* Scraps all properties, including houses, flats, garages, storehouses, even buildings in ruins!
* Scraps all usages and purposes: living, commercial, religious, military...
* Scraps rural (parcelas) and urban properties.
* Retrieves **the building plan** of every property
* Skips already scrapped information
* Can be queried to scrap a list of provinces
* Can be queried to scrap by a polygon of coordinates
* Can be queried to start from a specific city in a province

_Storing_
* Stores in ElasticSearch
* Supports automatic map visualization in Kibana

_Visualization_

Includes a configured Kibana that shows.
1) A heatmap in the map of Spain (World) where the properties are
2) All data in tables
3) The picture of the property

**DoS Warning**

Spanish Cadaster has set restrictions, banning temporarily IPs that more than 10 
queries in 5 seconds. A sleep command has been set to 5sec where needed, and can be configured
at your own risk.

At night DoS happens more often it seems, and 5sec can throw a `Connection Reset by Peer` message.
To try to avoid this, add this two cron commands after having launched libreCatastro
to send to sleep at 23:00 and restart processing at 09:00 everyday
```
0 23 * * * ps aux | grep "[l]ibreCadastro" | awk '{print $2}' | xargs kill -TSTP
0 09 * * * ps aux | grep "[l]ibreCadastro" | awk '{print $2}' | xargs kill -CONT
```


**Installation**

Having Docker and Docker-compose installed, run first:
```
docker-compose up -d
pip install -r requirements.txt
```

Then configure ElasticSearch index:
```
python3 initialize_elasticsearch.py
```

An finally, execute libreCatastro as follows in the next step.

**Execution**
```
$ python libreCatastro.py --help

usage: libreCatastro.py [-h] [--coords]
                        [--filenames FILENAMES [FILENAMES ...]]
                        [--provinces PROVINCES [PROVINCES ...]]
                        [--sleep SLEEP] [--html] [--scale SCALE] [--pictures]
                        [--startcity STARTCITY] [--listprovinces]
                        [--listcities LISTCITIES] [--health]

Runs libreCatastro

optional arguments:
  -h, --help            show this help message and exit
  --coords (scrapping by coordinates. By default, if not set, it's by provinces)
  --filenames FILENAMES [FILENAMES ...] (for files with polygon coordinates)
  --provinces PROVINCES [PROVINCES ...] (for a list of provinces to scrap)
  --sleep SLEEP (time to sleep to avoid Cadaster DoS)
  --html (if you prefer to scrap HTML or if XML servers are down)
  --scale SCALE (for scrapping by coordinates, how big is the step)
  --pictures (scrap also the plan of the house)
  --startcity STARTCITY (start from a specific city in a province, in alphabetic order)
  --listprovinces (just list all provinces in alphabetic order)
  --listcities PROVINCE (just list all cities of a province in alphabetic order)
  --health (check if Cadaster servers are up)
 ```
 
**Health**
I highly recommend to execute first of all:
`python3 libreCatastro.py --health` to check if XML and HTML servers are up.

**Time to get the complete DB**
Taking into account that there are restrictions that prevents a crapping faster than 5sec per page,
scrapping can take very long time. so:
1) Go directly to the provinces / cities you need the most. Leave the rest for later.
2) Use different IP addresses and query parallely.
3) Write me an email to jjmcarrascosa@gmail.com to get the full DB.

**Using additional machines (parallel extraction)**
You won't need to repeat the previous steps, because we will use one Elastic Search for all the machines.
For additional machines, do the following:
1) Make sure you have successfully run all the previous steps and ElasticSearch is running in one machine;
2) Copy the pubic IP address of that machine
3) In a new machine, clone this repository and do the following:
```
pip install -r requirements.txt
export ES_HOST="{IP OR HOST OF THE MACHINE RUNNING ELASTICSEARCH"
export ES_PORT="{PORT OF THE MACHINE RUNNING ELASTICSEARCH. USUALLY 9200}"
```
And finally, run libreCatastro:
```
python libreCatastro.py [....]
```