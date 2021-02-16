#Automated detection and tracking of fish for ecology
#Sample R code for data wrangling of computer vision tracking data
#Sebastian Lopez-Marcano
#16022021


####Read Libraries####
library(tidyverse)
library(sqldf)
library(ggplot2)
library(gridExtra)


#####MOSSE AND SIAMMASK####
#Example data shown here is for MOSSE tracker. A sample tracking file from SiamMask can be found in the Github repo. This code will work for both tracking outputs. 
#Read sample data. Change directory to suit your needs
sample_mosse <- read.csv("~/Dropbox/Automated Tracking of Fish for Ecology/Movement dataset/Sample data/MOSSE/ft-annotation-editor_prediction-results__akVqoIAO_FishID_predict__akVqoIAO_vlc-record-2019-10-02-08h36m17s-10092019_C3_CLOSE_Tweeds_1.MOV-.avi_25fps-tracking-mosse-processed.csv")


#Extract metadata from filename. Optional step
#Extract day
sample_mosse$day<-substr(sample_mosse$filename,33,40)
#Extract camera number
sample_mosse$camera<-substr(sample_mosse$filename, 42,43)


#Optional. Filter rows by specific confidence threshold. This is useful to filter 'low-performing' detections. 
#SQLDF version
#sample_mosse<-sqldf('select * from merged_5fps where detection_score >=0.95')
#TIDYVERSE version
#sample_mosse<-sample_mosse%<%
  #filter(detection_score>=0.95)

#Summarize tracking data
#SQLDF version
summary_tracking_mosse_sql<-sqldf("select count(tracker_angle_simple) as count_tracker, tracker_angle_simple as direction from sample_mosse group by tracker_angle_simple")
#TIDYVERSE version
summary_tracking_mosse_tidy<-sample_mosse%>%
  group_by(tracker_angle_simple)%>%
  summarize(count=n())


#Visualize tracking data
mosse_viz <- ggplot(sample_mosse, aes(x=tracker_center_x, y=tracker_center_y, group=tracker_angle_simple)) + 
  geom_point(size = 5, pch = 21, aes (fill=tracker_angle_simple))+
  xlim(0.25,1)+
  ylim(0.3,0.6)+
  coord_cartesian(clip = 'off') +
  labs(title = "Fish movement smooth (MOSSE)") +
  theme_minimal() +
  theme(plot.margin = margin(5.5, 40, 5.5, 5.5), legend.position = 'bottom')+
  annotation_custom(tableGrob(summary_tracking_mosse_sql, rows = NULL), xmin=0.7, xmax=1, ymin=0.32, ymax=0.4)


#CONCLUSION: The net movement of the fish (tracking angle with the highest count per video) is to the RIGHT. This matches the ground-truth. 


####SEQNMS####
#Example data shown here is for SEQNMS tracker.change directory as required
sample_seqnms <- read.csv("~/Dropbox/Automated Tracking of Fish for Ecology/Movement dataset/Sample data/SEQNMS/FishID_predict__akVqoIAO_vlc-record-2019-10-02-08h36m17s-10092019_C3_CLOSE_Tweeds_1.MOV-.avi_25fps-processed.csv")


#Summarise tracking data
#SQLDF version
summary_tracking_seqnms_sql<-sqldf('select count(spatial_angle_simple) as count_tracker, spatial_angle_simple as direction from sample_seqnms group by spatial_angle_simple')
#TIDYVERSE version
summary_tracking_seqnms_tidy<-sample_seqnms%>%
  group_by(spatial_angle_simple)%>%
  summarize(count=n())

seqnms_viz <- ggplot(sample_seqnms, aes(x=center_smoothed_x, y=center_smoothed_y, group=spatial_angle_simple)) + 
  geom_point(size = 5, pch = 21, aes (fill=spatial_angle_simple))+
  #xlim()+
  ylim(00,720)+
  coord_cartesian(clip = 'off') +
  labs(title = "Fish movement smooth (SEQNMS)") +
  theme_minimal() +
  theme(plot.margin = margin(5.5, 40, 5.5, 5.5), legend.position = 'bottom')+
  annotation_custom(tableGrob(summary_tracking_seqnms_sql, rows = NULL), xmin=1600, xmax=1800, ymin=100, ymax=200)+
  transition_reveal(sample_seqnms$timestamp) +
  shadow_wake(wake_length = 0.1, wrap = FALSE, colour = 'white', falloff = 'quintic-in')

animate(seqnms_viz, nframes = 175, detail = 10)
anim_save(filename = 'fish_movement_animation_seqnms.gif', animation = last_animation(), path ='~/Dropbox/Automated Tracking of Fish for Ecology/Movement dataset/Sample data/SEQNMS/')

#CONCLUSION: The net movement of the fish (tracking angle with the highest count per video) is to the RIGHT. This matches the groundtruth. 
