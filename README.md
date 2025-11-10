Dataset Preparation for RoadGrpahPlus
--------------------------------------


### Step 1: Download Images and Graphs from Google Maps and OpenStreetMap
**Acknowledgment:** This repository builds upon the dataset module from https://github.com/mitroadmaps/roadtracer/tree/master/dataset.

The following an excerpt:<br>

The bounding boxes for the dataset regions are defined in `lib/regions.go`. There are 40 regions in all, with 25 used for training and 15 for testing.

First, obtain the satellite imagery from Google Maps. You will need an API key from https://developers.google.com/maps/documentation/static-maps/.

```
mkdir /data/imagery/
go run 1_sat.go APIKEY /data/imagery/
```

Next, download the OpenStreetMap dataset and extract crops of the road network graph from it. We convert the coordinates from longitude/latitude a coordinate system that matches the pixels from the imagery.

```
wget https://planet.openstreetmap.org/pbf/planet-latest.osm.pbf -O /data/planet.osm.pbf
mkdir /data/rawgraphs/
go run 2_mkgraphs.go /data/planet.osm.pbf /data/rawgraphs/
mkdir /data/graphs/
go run 3_convertgraphs.go /data/rawgraphs/ /data/graphs/
```

### Step2: Obtain Grount Truth (GT) Graphs for Each Image in .`geojson` Format
The code above generates graphs for each region in `.graph` format. Here, we convert them to `.geojson` for Python compatibility.
```
go run graph_to_json.go ./data/graphs
```

In the imagenary folder, each file is named `{region}_{i}_{j}_sat.img`. Based on the generated `geojson` files, we create GT graphs for each image in `.json` format (`{region}_{i}_{j}_graph.json`).

```
python generate_GT.py \
   --graphs_dir data/graphs \
   --imagery_dir data/imagery \
   --out_dir data/labels \
   --tile_size 4096
```

Once all procedures are complete, the directory should look like this:
```
- data
    - graphs
        - amsterdam.geojson
        - amsterdam.graph
        ...
    - imagery
        - amsterdam_-1_-1_sat.png
        ...
    - labels
        - amsterdam_-1_-1_graph.json
        ...
    - rawgraphs
```

