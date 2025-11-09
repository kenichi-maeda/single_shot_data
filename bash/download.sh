#!/bin/bash
#SBATCH --job-name=map_dl
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err
#SBATCH --time=48:00:00
#SBATCH --mem=32G
#SBATCH --cpus-per-task=2

module load go/1.23.3-d3wvs6z

go run 1_sat.go API  ./data/imagery/