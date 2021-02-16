#04022021
#Python script to run seqnms tracker on computer vision fish detections

# 1st step: Import libraries
import pandas as pd
from pathlib import Path
import glob
from seqnms import calculateSEQNMS #seqnms.py must be in the same directory as running_seqnms.py


# Code from seqnms.py. It handles the conversion to/from data frame <-> dict
def apply_seq_nms(detections, min_link_length=1, iou_threshold=0.3):
    detections_dict = detections.to_dict("records")
    detections_dict = calculateSEQNMS(
        detections=detections_dict,
        min_link_length=min_link_length,
        iou_threshold=iou_threshold,
    )
    detections_processed = pd.DataFrame().from_dict(detections_dict)
    return detections_processed

# 2nd step: Read all csvs in directory. csv files should be the detections files from the object detection model. 
# Check that there are no other random csv files in folder, like exported/processed results.
files = glob.glob("*.csv") #a list of files should appear in python environment
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
] #these are the column names that 'should' be exported by the object detection file. Can be modified depending on object detection model used. 
dfs = [pd.read_csv(f, header=0, names=names, sep=",") for f in files] #code that reads the csv
detections = dfs #assing new name to dfs -> detections (to be used by seqnms function)

#3rd step: run the seqnms function
seqnms function
#the min_link_length and iou_threshold can be changed depending on the sensitivity of the model. Link length controls how many links (detections) are required to create a detection chain #(i.e. tracker). IOU Threshold controls the overlap between detection 1 and detection 2 of the same object. Default values are as shown in this code. 
detections_processed = []
for df in detections:
    processed = apply_seq_nms(detections=df, min_link_length=1, iou_threshold=0.3)
    # I also had a mistake here previously
    # detections_processed = detections_processed.append(processed)
    detections_processed.append(processed)

# This will turn all separate dataframes into 1 dataframe (if you have multiple videos processed)
detections_all = pd.concat(detections_processed)

#Export final csv to output_path
output_path = "~/Downloads/detections_1_0.3_nofilter.csv" #change the directory here
detections_all.to_csv(output_path, index=False)

print(f"Saved to {output_path}")
