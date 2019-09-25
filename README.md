#libreCATASTRO
An opensource, MIT-licensed application that scraps the official Spanish 
Cadaster registry and stores information in Elastic Searcher.

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

UPDATE: At night DoS happens more often it seems, and 5sec can throw a `Connection Reset by Peer` message.


**Installation**

Having Docker and Docker-compose installed, run first:
```
docker-compose up -d 
```

Then configure ElasticSearch index:
```
python3 initialize_elasticsearch.py
```

An finally, execute libreCadastro as follows in the next step.

**Execution**
```
$ python libreCadastro.py --help

usage: libreCadastro.py [-h] [--coords]
                        [--filenames FILENAMES [FILENAMES ...]]
                        [--provinces PROVINCES [PROVINCES ...]]
                        [--sleep SLEEP] [--html] [--scale SCALE] [--pictures]
                        [--startcity STARTCITY] [--listprovinces]
                        [--listcities LISTCITIES] [--health]

Runs libreCadastro

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
`python3 libreCadastro.py --health` to check if XML and HTML servers are up.

**Time to get the complete DB**
Taking into account that there are restrictions that prevents a crapping faster than 5sec per page,
scrapping can take very long time. so:
1) Go directly to the provinces / cities you need the most. Leave the rest for later.
2) Use different IP addresses and query parallely.
3) Write me an email to jjmcarrascosa@gmail.com to get the full DB.
