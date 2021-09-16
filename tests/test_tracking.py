"""Test cases for the tracking."""
from os import path

import pandas as pd

from laptrack import track

DEFAULT_PARAMS = dict(
    track_distance_cutoff=15,
    track_start_cost=30,
    track_end_cost=30,
    gap_closing_cutoff=15,
    gap_closing_max_frame_count=2,
    splitting_cutoff=False,
    no_splitting_cost=30,
    merging_cutoff=False,
    no_merging_cost=30,
)

FILENAME_SUFFIX_PARAMS = [
    (
        "without_gap_closing",
        {
            **DEFAULT_PARAMS,
            "gap_closing_cutoff": False,
            "splitting_cutoff": False,
            "merging_cutoff": False,
        },
    ),
    #    (
    #        "with_gap_closing",
    #        {
    #            **DEFAULT_PARAMS,
    #            "splitting_cutoff": False,
    #            "merging_cutoff": False,
    #        },
    #    ),
    #    ("with_splitting",{
    #       **DEFAULT_PARAMS,
    #       "merging_cutoff":False,
    #       }),
    #    ("with_merging",{
    #        **DEFAULT_PARAMS,
    #        "splitting_cutoff":False,
    #        }),
]


def test_tracking(shared_datadir: str) -> None:
    for filename_suffix, params in FILENAME_SUFFIX_PARAMS:
        filename = path.join(shared_datadir, f"trackmate_tracks_{filename_suffix}")
        spots_df = pd.read_csv(filename + "_spots.csv")
        frame_max = spots_df["frame"].max()
        coords = []
        spot_ids = []
        for i in range(frame_max):
            df = spots_df[spots_df["frame"] == i]
            coords.append(df[["position_x", "position_y"]].values)
            spot_ids.append(df["id"].values)
        track_tree = track(coords, **params)

        spot_id_to_coord_id = {}
        for i, spot_ids_frame in enumerate(spot_ids):
            for j, spot_id in enumerate(spot_ids_frame):
                assert not spot_id in spot_id_to_coord_id
                spot_id_to_coord_id[spot_id] = (i, j)

        edges_df = pd.read_csv(filename + "_edges.csv", index_col=0)
        edges_df["coord_source_id"] = edges_df["spot_source_id"].map(
            spot_id_to_coord_id
        )
        edges_df["coord_target_id"] = edges_df["spot_target_id"].map(
            spot_id_to_coord_id
        )
        valid_edges_df = edges_df[~pd.isna(edges_df["coord_target_id"])]
        edges_arr = valid_edges_df[["coord_source_id", "coord_target_id"]].values

        assert set(list(map(tuple, (edges_arr)))) == set(track_tree.edges)
