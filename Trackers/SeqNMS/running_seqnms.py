#04022021
#Python script to run seqnms tracker on computer vision fish detections

# 1st Step: Import libraries
import pandas as pd
from pathlib import Path
import glob
from seqnms import calculateSEQNMS #seqnms.py must be in the same directory as running_seqnms.py


# I've added the apply_seq_nms function above which was missing, it handles the conversion to/from dataframe <-> dict
def apply_seq_nms(detections, min_link_length=1, iou_threshold=0.3):
    detections_dict = detections.to_dict("records")
    detections_dict = calculateSEQNMS(
        detections=detections_dict,
        min_link_length=min_link_length,
        iou_threshold=iou_threshold,
    )
    detections_processed = pd.DataFrame().from_dict(detections_dict)
    return detections_processed

# read all csvs within folder. Step is ok.
# make sure no other random CSVs in folder, like exported/processed results. I've made that mistake before!
files = glob.glob("*.csv")
names = [
    "row_id",
    "model_id",
    "timestamp",
    "id",
    "species_id",
    "detection_id",
    "detection_score",
    "segmentation",
    "detection_center_x",
    "detection_center_y",
    "xmax",
    "xmin",
    "ymax",
    "ymin",
    "is_tracker",
    "tracker_id",
    "tracker_type",
    "tracker_angle",
    "tracker_angle_simple",
    "tracker_center_x",
    "tracker_center_y",
    "common_name",
    "filename",
    "cumul_sum",
]
dfs = [pd.read_csv(f, header=0, names=names, sep=",") for f in files]
detections = dfs

detections_processed = []
for df in detections:
    processed = apply_seq_nms(detections=df, min_link_length=1, iou_threshold=0.3)
    # I also had a mistake here previously
    # detections_processed = detections_processed.append(processed)
    detections_processed.append(processed)

# turn all separate dataframes into 1 dataframe
detections_all = pd.concat(detections_processed)

output_path = "~/OneDrive - Griffith University/PhD/MBEEC/seqnms_processed/detections_1_0.3_nofilter.csv"
detections_all.to_csv(output_path, index=False)

print(f"Saved to {output_path}")
