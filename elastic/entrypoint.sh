#!/bin/bash

if [ ! -f /usr/share/elasticsearch/initialized ]; then
  elasticsearch &

  echo 'Waiting for Elasticsearch to start...'
  until curl -s http://localhost:9200; do sleep 5; done
  echo 'Elasticsearch started. Creating repository...'

  curl -X PUT 'http://localhost:9200/_snapshot/my_backup' -H 'Content-Type: application/json' -d'
  {
    "type": "fs",
    "settings": {
      "location": "/usr/share/elasticsearch/snapshots"
    }
  }'
  echo 'Repository created. Restoring indices...'

  curl -X POST 'http://localhost:9200/_snapshot/my_backup/snapshot/_restore' -H 'Content-Type: application/json' -d'
  {
    "indices": "movies,genres,persons",
    "ignore_unavailable": true,
    "include_global_state": false
  }'
  echo 'Indices restored. Starting Elasticsearch...'

  touch /usr/share/elasticsearch/initialized
else
  echo 'Initialization already done. Starting Elasticsearch...'
fi

exec elasticsearch