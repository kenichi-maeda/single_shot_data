#!/bin/bash
#SBATCH --job-name=donwload_row_graph
#SBATCH --output=logs/na_row_graph/%x_%j.out
#SBATCH --error=logs/na_row_graph/%x_%j.err
#SBATCH --time=48:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=2

module load go/1.23.3-d3wvs6z

go run 2_mkgraphs.go /users/kmaeda2/scratch/data/north-america.osm.pbf ./data/rawgraphs_na/