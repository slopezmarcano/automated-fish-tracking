# automated-fish-tracking

**Short summary**: A toolbox for monitoring fish movement in their environment. This repository contains all the training data, test and movement datasets required to reproduce the study: [Automated detection and tracking of fish for ecology](insert link to paper here].

![Alt Text](https://github.com/slopezmarcano/automated-fish-tracking/blob/main/Movement%20dataset/Sample%20data/sample_video_final.gif)

# Table of Contents

1.  [Overview](https://github.com/slopezmarcano/automated-fish-tracking#overview)
2.  [Objective](https://github.com/slopezmarcano/automated-fish-tracking#objective)
3.  [Data](https://github.com/slopezmarcano/automated-fish-tracking#data)
4.  [Object Detection](https://github.com/slopezmarcano/automated-fish-tracking#object-detection)
5.  [Object Tracking](https://github.com/slopezmarcano/automated-fish-tracking#object-tracking)
6.  [Data Wrangling and Summary](https://github.com/slopezmarcano/automated-fish-tracking#data-wrangling-and-summary)

# OVERVIEW

Here we provide open-source code for automating the detection and tracking of marine fish in under water video footage. We combine an object detection (OD) and three object tracking (OT) computer vision (CV) algorithms to allow fish movement in marine ecosystems to be measured efficiently.

# OBJECTIVE

The datasets and code were developed for the study 'Automated detection and tracking for fish ecology', where we tested the ability of deep learning algorithms to track small-scale movement of fish in underwater videos. We developed a CV pipeline consisting of two steps, OD and OT, and tested several off-the-shelf OT architectures to determine their efficacy.

# DATA

## Training dataset

The training dataset was used to train the OD model. We focused on one target species, yellowfin bream. We collected the footage in the Tweed River estuary, Australia between May and September 2019.

We used six submerged action cameras (1080p Haldex Sports Action Cam HD) deployed for 1 hr over a variety of marine habitats (i.e. rocky reefs and seagrass meadows). We varied the angle and placement of the cameras to ensure the capture of diverse backgrounds and fish angles. We trimmed the videos using VLC media player 3.0.8 for training and split videos into 5 frames per second. We used a total 189 videos of varying durations (1 - 30 seconds) to train the fish detection model. The training videos included approx. 8,700 annotations of yellowfin bream across the video sequences.

We used software developed at Griffith University for data preparation and annotation tasks [FishID](https://globalwetlandsproject.org/tools/fishid/).

## Movement dataset

The movement dataset was used to evaluate the OD model and OT architectures. We collected the movement dataset in the same location as the training dataset, but during October 2019. We placed the cameras parallel to each other and separated by 20 m. The cameras faced the fish corridor and placed at a 90 degree angle from the seafloor, and were separated by \~ 3 m.

The distance between the cameras and between the sets ensured non-overlapping field of views. We placed the cameras in a continuous line starting at the harbour entrance and ending at the border of the seagrass meadow.

We manually trimmed each video using VLC media player 3.0.8 into video snippets with continuous yellowfin bream movement. The trimming resulted in 76 videos of varying durations (between 3 -- 70 seconds) with each video transformed into still frames at 25 frames per second.

All frames with yellowfin bream were annotated using FishID and used as ground truth when evaluating the OD model and OT architectures. We provide the movement dataset in COCO JSON and CSV files, as well as the RAW avi videos exported from VLC.

The videos are named with following nomenclature:

**vlc-record-2019-10-02-08h01m54s-10092019_C1_FAR_Tweeds_1.MOV-.avi**

**Snippet ID**: vlc-record-2019-10-02-08h01m54s

**Date of Deployment**: 10092019

**Camera**: C1

**Location of the Camera**: FAR (three options FAR, MID OR CLOSE to the seagrass meadow)

**Site of Deployment**: Tweeds

**Video Number**: 1

**Note**: original videos were filmed as MOV and after processing in VLC, their extension changed to .avi. To change videos from avi to other formats we recommend using HandBrake <https://handbrake.fr/>

## Datasets Overview

| Dataset          | Raw Videos                                                                                        | Raw Images                                                                                         | Version | Num Annotations | Annotations (CSV/JSON)                                                                                     |
|------------------|---------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------|---------|-----------------|--------------------------------------------------------------------------------------------------|
| Training dataset | N/A                                                                                               | [Download 903.8 MB](https://research-storage.griffith.edu.au/owncloud/index.php/s/m6XQL9nRM7kjhMc)                                                                              | 7       | 8,696           | [Download 5.9 MB](https://research-storage.griffith.edu.au/owncloud/index.php/s/7aqfAnfG8SuIug6) |
| Movement dataset | [Download 2.21 GB](https://research-storage.griffith.edu.au/owncloud/index.php/s/0GyirtQPabRvque) | [Download 676.8 MB](https://research-storage.griffith.edu.au/owncloud/index.php/s/wlIlVd2Ly6lO1yT) | 5       | 5,646           | [Download 4.3 MB](https://research-storage.griffith.edu.au/owncloud/index.php/s/IUBneDXQsNIAU4P) |

## Annotations

Each annotation includes object instance annotations which consists of the following key fields: Labels are provided as a common name: YellowfinBream for *Acanthopagrus australis*; bounding boxes that enclose the species in each frame are provided in "[x,y,width,height]" format, in pixel units; Segmentation masks which outline the species as a polygon are provided as a list of pixel coordinates in the format "9x,y,x,y,...]".

The corresponding image is provided as an image filename. All image coordinated (bounding box and segmentation masks) are measured from the top left mage corner and or 0-indexed.

Annotations are provided in both CSV format and COCO JSON format which is a commonly used data format for integration with object detection frameworks including PyTorch and TensorFlow. For more information on annotations files in COCO JSON and/or CSV formats go [here](https://github.com/globalwetlands/luderick-seagrass#coco-json).

# OBJECT DETECTION

We trained the Mask Regional Convolutional Neural Network (Mask R-CNN) OD model using a ResNet50 architecture with a learning rate of 0.0025. We used a randomly selected 90% sample of the annotated dataset for the training, with the remaining 10% for validation. To minimise overfitting, we used the early-stopping technique, where we assessed mAP50 on the validation set at intervals of 2,500 iterations and determined where the performance began to drop. We used a confidence threshold of 80%, meaning that we selected OD outputs where the model was 80% or more confident that it was a yellowfin bream. We developed the models and analysed the videos using a Microsoft Azure Data Science Virtual Machine powered with either NVIDIA V100 GPUs or Tesla K80 GPUs. We did not modify or adapt the original Mask R-CNN code and it be found [here](https://github.com/facebookresearch/maskrcnn-benchmark).

# OBJECT TRACKING

We developed a pipeline where the OT architecture activates once the OD model detected a fish of the target species. This approach resulted in an automated detection and subsequent tracking of fish from the underwater videos. Additionally, we benchmarked the performance of three OT architectures (MOSSE, Seq-NMS and SiamMask) by using movement dataset collected from a well-known coastal fish corridor in the Tweed River estuary, Australia.

## Minimum Output Sum of Squared Error (MOSSE)

The MOSSE algorithm produces adaptive correlation filters over target objects, and tracking is performed via convolutions (process of combining outputs to form more outputs). Here, we modified the MOSSE tracking process by activating the tracker with the OD output. The object detection model and the object tracking architecture interacted to maintain the consistency of the tracker on yellowfin bream individuals. When a fish was detected, the entry was used to initialise the tracker.

MOSSE then tracked the fish for 4 frames and then a check was made on the subsequent frame to verify the accuracy of the tracker. In this check, if the detection bounding box overlapped by more or equal than 30% with the existing tracker bounding box, then the tracker continues on the same object. If the detection bounding box does not overlap with the existing tracker bounding box, then a new tracker entry starts. This interaction between the detection and tracking occurred for every yellowfin bream detected in a frame and stopped when no more detections were found.

An implementation of the MOSSE tracker can be found [here](https://github.com/TianhongDai/mosse-object-tracking/blob/master/mosse.py); and our adaptation of the MOSSE tracker to activate once the OD model detected a fish can be found [here](https://github.com/slopezmarcano/automated-fish-tracking/tree/main/Trackers/Interaction_between_OD_OT).

## Sequential non-maximum suppression (Seq-NMS)

Sequential non-maximum suppression (Seq-NMS) is an algorithm developed to improve the classification results and consistency of deep learning outputs. Seq-NMS works by linking detections of neighbouring frames, which means that a detection in the first frame can be connected with a detection in the second frame if there is an intersection above a defined threshold. In our case, we used the principles of Seq-NMS to create detection linkages for OT of fish when there was an overlap of bounding box in consecutives frames of more or equal than 30%.

We determined the movement direction by calculating the distance and angle (vector) between the two coordinates at the centres of bounding boxes of Detections 1 and 2. Our adaptation of the SeqNMS code and a sample implementation of the tracker can be found [here](https://github.com/slopezmarcano/automated-fish-tracking/tree/main/Trackers/SeqNMS).

## Siamese Mask (SiamMask)

SiamMask is a tracking algorithm that uses outputs of deep learning models for estimating the rotation and location of objects. SiamMask is based on the concepts of Siamese network-based tracking. Similar to MOSSE, we slightly modified the tracking process by activating the tracker with the deep learning object detection model. The tracking with SiamMask started once a yellowfin bream was detected. The original SiamMask code was not modified and it can be found [here](https://github.com/foolwood/SiamMask) and our modification to the SiamMask tracker to activate once the OD model detected a fish can be found [here](https://github.com/slopezmarcano/automated-fish-tracking/tree/main/Trackers/Interaction_between_OD_OT).

## Movement dataset
We collected the fish movement data by submerging two sets of three action cameras (1080p Haldex Sports Action Cam HD) for one hour during a morning flood tide in October 2019. We used this dataset to evaluate the fish detection model and test the OT architectures. We placed the sets of cameras parallel to each other and separated by 20 m. Within each set, the cameras faced the fish corridor and placed at a 90 degree angle from the seafloor, and were separated by ~ 3 m. The distance between the cameras and between the sets ensured non-overlapping field of views. Set 1 cameras faced north and set 2 faced south. We placed the cameras in a continuous line starting at the harbour entrance and ending at the border of the seagrass meadow.

## Hardware and Software Overview

| Component | Hardware | Software |
|------------------|------------------|------------------|
| Underwater videos             | [1080p Haldex Sports Action Cam HD](https://www.google.com/search?q=1080p+Haldex+Sports+Action+Cam+HD&oq=1080&aqs=chrome.0.69i59j69i57.1248j0j7&sourceid=chrome&ie=UTF-8) to collect videos | VLC media player 3.0.8 for trimming videos|                                                                                                                                                             
| Annotations of fish in videos | N/A | [FishID](https://globalwetlandsproject.org/tools/fishid/)|                                                                 
| Training of OD model| [Microsoft Azure Data Science Virtual Machine](https://docs.microsoft.com/en-us/azure/virtual-machines/sizes-gpu) powered with either NVIDIA V100 GPUs or Tesla K80 GPUs| Mask Regional Convolutional Neural Network[Mask R-CNN](https://github.com/facebookresearch/maskrcnn-benchmark)|
| Evaluation and tracking | [Microsoft Azure Data Science Virtual Machine](https://docs.microsoft.com/en-us/azure/virtual-machines/sizes-gpu) powered with either NVIDIA V100 GPUs or Tesla K80 GPUs| [MOSSE](https://github.com/TianhongDai/mosse-object-tracking/blob/master/mosse.py) [Seq-NMS](https://github.com/slopezmarcano/automated-fish-tracking/tree/main/Trackers/SeqNMS) and [SiamMask](https://github.com/foolwood/SiamMask) |


# DATA WRANGLING AND SUMMARY

We have provided a sample output of our CV pipeline for the three trackers (MOSSE, SEQNMS and SIAMMASK). These can be found [here](https://github.com/slopezmarcano/automated-fish-tracking/tree/main/Movement%20dataset/Sample%20data). An R code for data wrangling, summary and visualisation of the tracking data can be found [here](https://github.com/slopezmarcano/automated-fish-tracking/tree/main/Tracking%20Wrangling%20and%20Summary).

The R code is divided into three sections: 1) Libraries 2) MOSSE and SiamMask and 3) SEQ-NMS. The summaries are done with common data wrangling packages (tidyverse and sqldf). An animation of the tracking process is provided for SeqNMS -- view [here](https://github.com/slopezmarcano/automated-fish-tracking/blob/main/Movement%20dataset/Sample%20data/SEQNMS/fish_movement_animation_seqnms.gif)


