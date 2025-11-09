#!/bin/bash
#SBATCH --job-name=donwload_graph
#SBATCH --output=logs/na_graph/%x_%j.out
#SBATCH --error=logs/na_graph/%x_%j.err
#SBATCH --time=48:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=2

module load go/1.23.3-d3wvs6z

go run 3_convertgraphs.go ./data/rawgraphs_na/ ./data/graphs_na/
