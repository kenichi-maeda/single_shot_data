#!/bin/bash
#SBATCH --job-name=convert_graph
#SBATCH --output=logs/convert_geojson/%x_%j.out
#SBATCH --error=logs/convert_geojson/%x_%j.err
#SBATCH --time=48:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=2

module load go/1.23.3-d3wvs6z

go run graph_to_json.go ./data/graphs
