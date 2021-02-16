video_fps = 25
predict_fps = 5

all_predictions = []
all_tracker_results = []
active_trackers = []

current_frame_number = 0

for frame in video:
    # check if keyframe
    is_prediction_keyframe = current_frame_number % predict_fps == 0
    if is_prediction_keyframe:
        # run predictions
        frame_predictions = compute_predictions(frame)
        all_predictions.append(frame_predictions)

        # For each prediction BBOX
        # - check for overlapping trackers
        # - create a new tracker if no overlapping tracker exists
        for prediction in frame_predictions:
            # - check for overlapping trackers
            matched_trackers = get_overlapping_tracker_box(prediction["bbox"])

            # - if matching tracker found:
            if len(matched_trackers) > 0:
                # Update tracker at index with prediction BBOX
                matched_trackers[0].update_bbox(frame, prediction["bbox"])
                # deactivate rest of overlapping trackers
                for tracker in matched_trackers[1:]:
                    tracker.remove()

            # - no matching tracker found, start new tracker
            else:
                # - start a new tracker with BBOX from prediction
                new_tracker = start_new_tracker(frame, prediction["bbox"])
                active_trackers.append(new_tracker)

    # Now that we've run predictions and created/updated trackers on prediction keyframes
    # We'll update active trackers and deactivate stale trackers
    # Every frame of video

    for tracker in active_trackers:
        # update this tracker with frame image data
        tracker.update(frame)

        # Check this tracker against all existing active trackers for overlap, disregarding itself
        matched_trackers = get_overlapping_tracker_box(tracker.bbox)

        if len(matched_trackers) > 0:
            for matched_tracker in matched_trackers:
                if matched_tracker.id != tracker.id:
                    # If matched tracker exists (overlapping tracker) then deactivate
                    # More recent trackers are removed first from tracker stack
                    # Allowing oldest tracker to remain active
                    matched_tracker.remove()

        # Update tracker results output with tracker data
        all_tracker_results.append(tracker.state)

    # Finally, increment frame_number and restart loop
    current_frame_number += 1
