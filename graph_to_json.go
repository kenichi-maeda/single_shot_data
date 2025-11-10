// Revised with assistance from ChatGPT

package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/mitroadmaps/gomapinfer/common"
)

type Feature struct {
	Type       string                 `json:"type"`
	Geometry   map[string]interface{} `json:"geometry"`
	Properties map[string]interface{} `json:"properties"`
}

type FeatureCollection struct {
	Type     string    `json:"type"`
	Features []Feature `json:"features"`
}

func graphToGeoJSON(inPath, outPath string) error {
	graph, err := common.ReadGraph(inPath)
	if err != nil {
		return fmt.Errorf("read %s: %w", inPath, err)
	}

	fc := FeatureCollection{Type: "FeatureCollection"}
	for _, edge := range graph.Edges {
		seg := edge.Segment()
		p1 := seg.Start
		p2 := seg.End

		f := Feature{
			Type: "Feature",
			Geometry: map[string]interface{}{
				"type": "LineString",
				"coordinates": [][]float64{
					{p1.X, p1.Y},
					{p2.X, p2.Y},
				},
			},
			Properties: map[string]interface{}{
				"edge_id": edge.ID,
				"src":     edge.Src.ID,
				"dst":     edge.Dst.ID,
			},
		}
		fc.Features = append(fc.Features, f)
	}

	bytes, err := json.MarshalIndent(fc, "", "  ")
	if err != nil {
		return fmt.Errorf("marshal geojson for %s: %w", inPath, err)
	}
	if err := os.WriteFile(outPath, bytes, 0644); err != nil {
		return fmt.Errorf("write %s: %w", outPath, err)
	}
	fmt.Printf("OK  %s -> %s  (edges=%d)\n", filepath.Base(inPath), filepath.Base(outPath), len(graph.Edges))
	return nil
}

func main() {
	dir := "data/graphs"
	if len(os.Args) > 1 && os.Args[1] != "" {
		dir = os.Args[1]
	}

	entries, err := os.ReadDir(dir)
	if err != nil {
		panic(fmt.Errorf("readdir %s: %w", dir, err))
	}

	var n int
	for _, e := range entries {
		if e.IsDir() {
			continue
		}
		name := e.Name()
		if !strings.HasSuffix(name, ".graph") {
			continue
		}
		inPath := filepath.Join(dir, name)
		outPath := filepath.Join(dir, strings.TrimSuffix(name, ".graph")+".geojson")

		if err := graphToGeoJSON(inPath, outPath); err != nil {
			fmt.Printf("ERR %s: %v\n", name, err)
			continue
		}
		n++
	}
	fmt.Printf("Done!")
}

