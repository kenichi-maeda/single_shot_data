# Credit: ChatGPT

"""
Make GT graph JSONS for all regions.

How to run:
python generate_GT.py \
   --graphs_dir data/graphs \
   --imagery_dir data/imagery \
   --out_dir data/labels \
   --tile_size 4096
"""

import os
import re
import glob
import json
import argparse
from typing import Dict, List, Tuple


def load_region_graph(geojson_path: str):
    """
    Load a region geojson and return node_coord dict and edge list.
    """
    with open(geojson_path, "r") as f:
        gj = json.load(f)

    node_coord: Dict[int, Tuple[float, float]] = {}
    edges: List[Dict[str, int]] = []

    for feat in gj.get("features", []):
        geom = feat.get("geometry", {})
        if geom.get("type") != "LineString":
            continue
        props = feat.get("properties", {})
        src = int(props["src"])
        dst = int(props["dst"])
        eid = int(props.get("edge_id", -1))
        coords = geom["coordinates"]
        if not coords:
            continue
        x1, y1 = coords[0]
        x2, y2 = coords[-1]
        # Record endpoint coords for nodes 
        node_coord[src] = (float(x1), float(y1))
        node_coord[dst] = (float(x2), float(y2))
        edges.append({"edge_id": eid, "src": src, "dst": dst})

    return node_coord, edges

def in_tile(x: float, y: float, tx: int, ty: int, tile_size: int) -> bool:
    return (tx*tile_size <= x < (tx+1)*tile_size) and (ty*tile_size <= y < (ty+1)*tile_size)

def process_region(region: str, graphs_dir: str, imagery_dir: str, out_dir: str, tile_size: int) -> int:
    """Process one region; returns number of GT files written."""
    geojson_path = os.path.join(graphs_dir, f"{region}.geojson")
    if not os.path.exists(geojson_path):
        print(f"[{region}] SKIP: {geojson_path} not found")
        return 0

    print(f"[{region}] Loading graph: {geojson_path}")
    node_coord, edges = load_region_graph(geojson_path)
    if not edges:
        print(f"[{region}] No edges found; skipping.")
        return 0

    # Find tiles for this region
    tile_re = re.compile(rf"^{re.escape(region)}_(-?\d+)_(-?\d+)_sat\.png$")
    tile_paths = []
    for p in glob.glob(os.path.join(imagery_dir, f"{region}_*_*_sat.png")):
        m = tile_re.match(os.path.basename(p))
        if m:
            tx, ty = int(m.group(1)), int(m.group(2))
            tile_paths.append((p, tx, ty))

    if not tile_paths:
        print(f"[{region}] No imagery tiles found in {imagery_dir}; skipping.")
        return 0

    os.makedirs(out_dir, exist_ok=True)

    written = 0
    for img_path, tx, ty in sorted(tile_paths, key=lambda t:(t[1], t[2])):
        x0, y0 = tx*tile_size, ty*tile_size

        # nodes inside this tile
        local_nodes: Dict[int, Dict[str, float]] = {}
        for nid, (gx, gy) in node_coord.items():
            if in_tile(gx, gy, tx, ty, tile_size):
                local_nodes[nid] = {
                    "nid": nid,
                    "x": gx - x0,
                    "y": gy - y0,
                }

        # keep edges whose both endpoints are inside
        local_edges = []
        if local_nodes:
            for e in edges:
                if e["src"] in local_nodes and e["dst"] in local_nodes:
                    local_edges.append(e)

        if not local_nodes and not local_edges:
            # tile has no graph content
            continue

        # Compact local indices for GNN
        idmap = {nid: i for i, nid in enumerate(sorted(local_nodes.keys()))}
        nodes_out = [
            {"nid": nid, "idx": idmap[nid], "x": local_nodes[nid]["x"], "y": local_nodes[nid]["y"]}
            for nid in sorted(local_nodes.keys())
        ]
        edges_out = [
            {"eid": e["edge_id"], "src_idx": idmap[e["src"]], "dst_idx": idmap[e["dst"]]}
            for e in local_edges
        ]

        gt = {
            "region": region,
            "image_path": img_path,
            "tile_xy": [tx, ty],
            "tile_size": tile_size,
            "coord_convention": "pixel_y_down",
            "num_nodes": len(nodes_out),
            "num_edges": len(edges_out),
            "nodes": nodes_out,
            "edges": edges_out,
        }

        out_name = f"{region}_{tx}_{ty}_graph.json"
        out_path = os.path.join(out_dir, out_name)
        with open(out_path, "w") as f:
            json.dump(gt, f, indent=2)
        written += 1
        print(f"[{region}] Wrote {out_path} (nodes={len(nodes_out)}, edges={len(edges_out)})")

    print(f"[{region}] Done. {written} file(s).")
    return written

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graphs_dir", default="data/graphs", help="Directory with REGION.geojson files")
    ap.add_argument("--imagery_dir", default="data/imagery", help="Directory with REGION_x_y_sat.png tiles")
    ap.add_argument("--out_dir", default="data/labels", help="Output base directory")
    ap.add_argument("--tile_size", type=int, default=4096, help="Tile size in pixels")
    ap.add_argument("--regions", nargs="*", default=None,
                    help="Optional list of region basenames to process (default: all *.geojson in graphs_dir)")
    args = ap.parse_args()

    if args.regions:
        regions = args.regions
    else:
        regions = []
        for p in glob.glob(os.path.join(args.graphs_dir, "*.geojson")):
            base = os.path.splitext(os.path.basename(p))[0]
            regions.append(base)
        regions.sort()

    if not regions:
        print("No regions found.")
        return

    os.makedirs(args.out_dir, exist_ok=True)

    total = 0
    for region in regions:
        total += process_region(region, args.graphs_dir, args.imagery_dir, args.out_dir, args.tile_size)

    print(f"All regions done. Total GT files: {total}")

if __name__ == "__main__":
    main()
