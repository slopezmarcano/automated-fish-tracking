# automated-fish-tracking
**Short summary**: A toolbox for monitoring fish movement in their environment. This repository contains all the training data, test and movement datasets required to reproduce the study: **Automated detection and tracking of fish for ecology**. 

(GIF OF FISH MOVEMENT WILL GO HERE)

# Table of contents

# OVERVIEW
Computer vision (CV), the research field that explores the use of computer algorithms to automate the interpretation of digital images or videos, is revolutionising data collection in science. In marine ecosystems, we have seen an increase in the uptake of CV to study and monitor complex interactions and processes. These applications are related to the two main CV tasks – object detection (OD) and object tracking (OT). While there is evidence OD and OT work in marine ecosystems, no studies have jointly applied OD and OT for animal movement studies. The combination of OD and OT is particularly suited to the subfield of marine animal movement because these tasks can provide the volume of data required to quantify animal movement of numerous individuals

# THE POWER OF COMPUTER VISION TRACKING FOR ECOLOGY
The knowledge of animal movement is fundamental to many research objectives in ecology and collecting movement data is challenging and requires substantial resources. Therefore, the development and applications of emerging technologies (i.e. computer vision) can help advance our understanding of animal movement across a broad range of spatio-temporal dimensions and ecological hierarchies (e.g. individuals, populations, communities). 

# OBJECTIVE
In this study, we aimed to test the ability of deep learning algorithms to track small-scale animal movement of many individuals in underwater videos. We developed a CV pipeline consisting of two steps, OD and OT, and we used the pipeline to quantify underwater animal movement across habitats for ecological research. We tested and applied off-the-shelf OT architectures to determine the efficacy and capacity of these emerging techniques to be used for underwater ecological applications. 

To demonstrate the applications of OD and OT, we deployed a 6-camera network in a known coastal fish estuarine corridor (Tweed River estuary, Australia) and recorded the movement of a common fisheries species (yellowfin bream, Acanthopagrus australis). The corridor, is located between a rockwall passage and a seagrass meadow. Multiple estuarine fish such as sand whiting (Sillago ciliata), river garfish (Hyporhamphus regularis), luderick (Girella tricuspidata), spotted scat (Scatophagus argus), three-bar porcupinefish (Dicotylichthys punctulatus) and yellowfin bream, frequently move back and forth with the tides through this corridor, representing a relatively challenging scenario (i.e. low visibility and with currents also carrying floating debris) to showcase the capacity of CV to detect the target species in a multi-species assemblage and quantify the direction of  movement. Ultimately, we demonstrate that these technologies can complement the collection and analysis of animal movement data.

# SAMPLING METHODOLOGY
We collected two datasets of underwater videos in the Tweed River estuary fish corridor – the training dataset and the movement dataset. Both datasets were collected in the same location but during different months. The training dataset was collected between May and September 2019, whereas the movement dataset was collected in October 2019. 

## Training dataset
We collected video footage of the target species, yellowfin bream in the Tweed River estuary, Australia (-28.169438, 153.547594) between May and September 2019. 

We used six submerged action cameras (1080p Haldex Sports Action Cam HD) deployed for 1 hr over a variety of marine habitats (i.e. rocky reefs and seagrass meadows). We varied the angle and placement of the cameras to ensure the capture of diverse backgrounds and fish angles. We trimmed the videos using VLC media player 3.0.8 for training and split videos into 5 frames per second. We used a total 189 videos of varying durations (1 - 30 seconds) to train the fish detection model. The training videos included 8,700 fish annotated across the video sequences.

(IMAGE OF ANNOTATIONS HERE)

We used software developed at Griffith University for data preparation and annotation tasks FishID <https://globalwetlandsproject.org/tools/fishid/>

##Movement dataset
We collected the fish movement data by submerging two sets of three action cameras (1080p Haldex Sports Action Cam HD) for one hour during a morning flood tide in October 2019. We used this dataset to evaluate the fish detection model and test the OT architectures. We placed the sets of cameras parallel to each other and separated by 20 m. Within each set, the cameras faced the fish corridor and placed at a 90 angle from the seafloor, and were separated by ~ 3 m. The distance between the cameras and between the sets ensured non-overlapping field of views. Set 1 cameras faced north and set 2 faced south. We placed the cameras in a continuous line starting at the harbour entrance and ending at the border of the seagrass meadow. 






