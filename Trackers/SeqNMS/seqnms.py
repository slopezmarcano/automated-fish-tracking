# refactored from original code written in JavaScript
import itertools
import statistics
from pprint import pprint


def flatten(list):
    return [item for sublist in list for item in sublist]


def get_bbox_center(xmin, xmax, ymin, ymax):
    x_center = xmin + (xmax - xmin) / 2
    y_center = ymin + (ymax - ymin) / 2
    return [round(x_center, 4), round(y_center, 4)]


def calculateIOU(box1, box2):
    x_left = max(box1["xmin"], box2["xmin"])
    y_top = max(box1["ymin"], box2["ymin"])
    x_right = min(box1["xmax"], box2["xmax"])
    y_bottom = min(box1["ymax"], box2["ymax"])

    if (x_right < x_left) or (y_bottom < y_top):
        return {}

    intersection_area = (x_right - x_left) * (y_bottom - y_top)

    box1_area = (box1["xmax"] - box1["xmin"]) * (box1["ymax"] - box1["ymin"])
    box2_area = (box2["xmax"] - box2["xmin"]) * (box2["ymax"] - box2["ymin"])
    iou = intersection_area / (box1_area + box2_area - intersection_area)
    return {
        "iou": iou,
        "intersection_area": intersection_area,
        "intersectionBox": {
            "xmin": x_left,
            "xmax": x_right,
            "ymin": y_top,
            "ymax": y_bottom,
        },
    }


def isOverlapping(box1, box2, iou_threshold):
    iou = calculateIOU(box1, box2)
    return iou.get("iou", 0) >= iou_threshold


def isValidDetection(detection):
    if float(detection.get("is_tracker")):
        return False
    else:
        return True


def sort_detections(detections):
    return sorted(detections, key=lambda det: det["timestamp"])


def keepMaxByIOU(detections, iou_threshold):
    detections = sort_detections(detections)
    for index, box1 in enumerate(detections):
        # reset isMaxPath
        box1["isMaxPath"] = False
        # find new isMaxPath
        current_max = None

        for box2 in detections:
            is_overlapping = isOverlapping(box1, box2, iou_threshold)
            is_same_class = int(box1["species_id"]) == int(box2["species_id"])
            if is_overlapping and is_same_class == True:
                box2_score = box2["detection_score"]
                if current_max is None or box2_score > current_max["detection_score"]:
                    if not float(box2.get("is_tracker")):
                        current_max = box2

        if current_max is not None:
            current_max["isMaxPath"] = True

    filtered_detections = sorted(
        [detection for detection in detections if detection.get("isMaxPath") == True],
        key=lambda det: det["timestamp"],
    )
    return filtered_detections


def identifyLinks(detectionsA, detectionsB, iou_threshold, links):
    # print(len(detectionsA))
    for box1 in detectionsA:
        ## start a new array of linked detections
        ## or continue an existing array if overlapping iou above threshold
        linkIndex = box1.get("linkIndex", len(links))

        # check for previous links or start a new list
        try:
            prevLinks = links[linkIndex]
        except IndexError:
            ## start a new link if none
            prevLinks = [box1]

        # get find overlapping detections
        matchesB = [
            box2
            for box2 in detectionsB
            if (box2.get("linkIndex") == None)
            and (isOverlapping(box1, box2, iou_threshold))
        ]

        # define linkIndex for each matching box
        box1["linkIndex"] = linkIndex
        for box in matchesB:
            box["linkIndex"] = linkIndex

        if len(prevLinks) == 1:
            # is new list
            links.append(prevLinks + matchesB)
        else:
            # update existing
            links[linkIndex] = prevLinks + matchesB

    return links


def determine_detection_chain_class_scores(chain):
    # print(len(chain), "chain")
    scorePerClass = {}

    validLinkedDetections = [
        detection for detection in chain if isValidDetection(detection)
    ]

    for detection in validLinkedDetections:
        classNum = detection["species_id"]

        score = float(detection["detection_score"])

        if classNum not in scorePerClass.keys():
            scorePerClass[classNum] = {"count": 0, "detection_score": 0}
        existing = scorePerClass[classNum]
        scorePerClass[classNum] = {
            "detection_score": existing["detection_score"] + score,
            "count": existing["count"] + 1,
        }

    scoresRanked = []
    for classNum, classScores in scorePerClass.items():
        score = classScores["detection_score"]
        count = classScores["count"]

        scoresRanked.append(
            {
                "species_id": classNum,
                "score_total": round(score, 4),
                "score_average": round(score / count, 4),
            }
        )

    scoresRanked = sorted(
        scoresRanked, key=lambda classScores: classScores["score_total"], reverse=True
    )
    return scoresRanked


def createLinks(
    frames,
    min_link_length,
    iou_threshold,
    ## trackerMaxSustain, // ms to sustain tracker in chain without matching prediction
):
    print(min_link_length, iou_threshold)
    print(len(flatten(frames)), "detections")

    # for index, detections in enumerate(frames):
    #     frame = keepMaxByIOU(detections, iou_threshold)
    #     frames[index] = frame
    frames = list(
        map(
            lambda frame: keepMaxByIOU(detections=frame, iou_threshold=iou_threshold),
            frames,
        )
    )

    print(len(flatten(frames)), "detections keepMaxByIOU")

    print(len(frames), "frames")

    linksAll = []
    for frame_index, frame in enumerate(frames):
        detectionsA = frame
        # print(len(frame))
        try:
            detectionsB = frames[frame_index + 1]
            linksAll = identifyLinks(
                detectionsA, detectionsB, iou_threshold, links=linksAll
            )
        except IndexError:
            ## skip if no next frame detections
            continue

    print(len(flatten(linksAll)), "linksAll")

    average_chain_length = statistics.mean([len(chain) for chain in linksAll])
    print(average_chain_length, "average_chain_length")

    ## Vote on class
    for chain in linksAll:
        scoresRanked = determine_detection_chain_class_scores(chain)
        linkLength = len(chain)
        highestScore = scoresRanked[0]
        if highestScore is not None:
            highestClassScoreAverage = float(highestScore["score_average"])
            highestClassNum = int(highestScore["species_id"])

            # apply to all linkedDetections (including non-valid e.g. tracker)
            for det in chain:
                # Add bboxCenterPoints
                xmin = det["xmin"]
                xmax = det["xmax"]
                ymin = det["ymin"]
                ymax = det["ymax"]

                center = get_bbox_center(xmin, xmax, ymin, ymax)
                det["detection_center_x"] = center[0]
                det["detection_center_y"] = center[1]
                det["species_id_orig"] = det["species_id"]
                det["species_id"] = highestClassNum
                # det["scores_ranked"] = scoresRanked
                det["detection_score_orig"] = det["detection_score"]
                det["detection_score"] = highestClassScoreAverage
                det["linkLength"] = linkLength

    ## Filter out overlapping matches after class vote
    frames = list(
        map(
            lambda frame: keepMaxByIOU(detections=frame, iou_threshold=iou_threshold),
            frames,
        )
    )

    print(len(frames), "frames")

    # un-group links/chains
    detections = flatten(linksAll)
    print(len(detections), "keepMaxByIOU detections")
    # Sort by timestamp
    detections = sort_detections(detections)
    print(len(detections), "sorted detections")
    # Filter out non-max paths
    detections = [det for det in detections if det["isMaxPath"] == True]
    print(len(detections), "filter non-max detections")
    # Filter out chains under min_link_length threshold
    detections = [det for det in detections if det["linkLength"] >= min_link_length]
    print(len(detections), "filter linkLength detections")

    return detections


def calculateSEQNMS(
    detections, min_link_length=2, iou_threshold=0.3, group_by_key="timestamp"
):
    # Required columns
    # species_id INT,
    # detection_id VARCHAR(10),
    # detection_score DECIMAL(5,4),
    # timestamp INT,
    # is_tracker BIT,
    # xmax DECIMAL(5,4) NOT NULL,
    # xmin DECIMAL(5,4) NOT NULL,
    # ymax DECIMAL(5,4) NOT NULL,
    # ymin DECIMAL(5,4) NOT NULL

    # trackerMaxSustain = 0, // ms

    print("calculateSEQNMS")
    print("min_link_length", min_link_length)
    print("iou_threshold", iou_threshold)

    # group by timestamp/frame_num
    grouped = itertools.groupby(detections, key=lambda det: det[group_by_key])
    frames = []
    frame_keys = []
    for key, dets in grouped:
        frames.append(list(dets))  # Store group iterator as a list
        frame_keys.append(key)

    # print(f"{len(frames)} frames")

    processed_detections = createLinks(
        frames=frames,
        min_link_length=min_link_length,
        iou_threshold=iou_threshold,
        # trackerMaxSustain,
    )

    return processed_detections

