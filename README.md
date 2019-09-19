#libreCATASTRO
An opensource, MIT-licensed application that scraps the official Spanish 
Cadaster registry and stores information in Elastic Search.

**Features**

_Scrapping_
* From XML webservices. Check http://www.catastro.meh.es/ws/Webservices_Libres.pdf
* From HTML
* Scraps by zone/site and by property in them
* Scraps rural and urban properties
* Retrieves a picture of every property

_Storing_
* Stores in ElasticSearch
* Allows visualization in Kibana

_Visualization_

Includes a configured Kibana that shows.
1) A heatmap in the map of Spain (World) where the properties are
2) All data in tables
3) The picture of the property

**DoS Warning**

Spanish Cadaster has set restrictions, banning temporarily IPs that more than 10 
queries in 5 seconds. A sleep command has been set to 5sec where needed, and can be configured
at your own risk.

**Installation**

Having Docker and Docker-compose installed, run first:
```
docker-compose up -d 
```

Then configure ElasticSearch index:
```
python3 initialize_elasticsearch.py
```

That simple!

**Execution**
```
python main.py[--coords] [--pictures] [--filenames filename1 filename2 ...] [--provinces province1 province2 ...] [--sleep sleep_time] [--html]
```

