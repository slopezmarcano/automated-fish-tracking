# refactored from original code written in JavaScript
import itertools
import statistics
import math
from pprint import pprint


def flatten(list):
    return [item for sublist in list for item in sublist]


def get_bbox_center(xmin, xmax, ymin, ymax):
    x_center = xmin + (xmax - xmin) / 2
    y_center = ymin + (ymax - ymin) / 2
    return [round(x_center, 4), round(y_center, 4)]


def getDistanceBetween(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def getAngleBetween(p1, p2):
    radians = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
    degrees = (radians * 180) / math.pi
    ## Rotate around so UP is 0/360deg
    absDegrees = (360 + degrees + 90) % 360
    return absDegrees


def getAngleSimple(degrees):
    if degrees is None:
        return None

    if degrees <= 45 or degrees >= 315:
        return "UP"

    if degrees >= 45 and degrees <= 135:
        return "RIGHT"

    if degrees >= 135 and degrees <= 225:
        return "DOWN"

    if degrees >= 225 and degrees <= 315:
        return "LEFT"


"""
KalmanFilter
---
https://github.com/wouterbulten/kalmanjs
    
"""


class KalmanFilter:

    cov = float("nan")
    x = float("nan")

    def __init__(self, R, Q):
        """
        Constructor
        :param R: Process Noise
        :param Q: Measurement Noise
        """
        self.A = 1
        self.B = 0
        self.C = 1

        self.R = R
        self.Q = Q

    def filter(self, measurement):
        """
        Filters a measurement
        :param measurement: The measurement value to be filtered
        :return: The filtered value
        """
        u = 0
        if math.isnan(self.x):
            self.x = (1 / self.C) * measurement
            self.cov = (1 / self.C) * self.Q * (1 / self.C)
        else:
            predX = (self.A * self.x) + (self.B * u)
            predCov = ((self.A * self.cov) * self.A) + self.R

            # Kalman Gain
            K = predCov * self.C * (1 / ((self.C * predCov * self.C) + self.Q))

            # Correction
            self.x = predX + K * (measurement - (self.C * predX))
            self.cov = predCov - (K * self.C * predCov)

        return self.x

    def last_measurement(self):
        """
        Returns the last measurement fed into the filter
        :return: The last measurement fed into the filter
        """
        return self.x

    def set_measurement_noise(self, noise):
        """
        Sets measurement noise
        :param noise: The new measurement noise
        """
        self.Q = noise

    def set_process_noise(self, noise):
        """
        Sets process noise
        :param noise: The new process noise
        """
        self.R = noise


def applyKalmanFilter(items, inputKey, outputKey, R, Q):
    kf = KalmanFilter(R, Q)
    appliedValues = []
    for item in items:
        if inputKey in item:
            inputValue = float(item[inputKey])
            appliedValue = kf.filter(inputValue)
        else:
            appliedValue = None

        item[outputKey] = appliedValue
        appliedValues.append(item)

    return appliedValues


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
    for box1 in detections:
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

    filtered_detections = sort_detections(
        [det for det in detections if det.get("isMaxPath") == True]
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

    for index, detections in enumerate(frames):
        frame = keepMaxByIOU(detections, iou_threshold)
        frames[index] = frame
    # frames = list(
    #     map(
    #         lambda frame: keepMaxByIOU(detections=frame, iou_threshold=iou_threshold),
    #         frames,
    #     )
    # )
    print(len(frames[10]), "frames[10]")

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
    for index, detections in enumerate(frames):
        frame = keepMaxByIOU(detections, iou_threshold)
        frames[index] = frame

    print(len(frames), "frames")

    ## analyse link movement
    print("analyse link movement")
    linksAll = analyseSpatialMovement(linksAll)

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


def analyseSpatialMovement(linksAll):
    chainsProcessed = []
    for index, chain in enumerate(linksAll):
        chainCoords = [
            {
                "detection_center_x": det["detection_center_x"],
                "detection_center_y": det["detection_center_y"],
            }
            for det in chain
        ]

        centerChain_x = applyKalmanFilter(
            items=chainCoords,
            inputKey="detection_center_x",
            outputKey="detection_center_x_smoothed",
            R=1,
            Q=2,
        )
        centerChain_y = applyKalmanFilter(
            items=chainCoords,
            inputKey="detection_center_y",
            outputKey="detection_center_y_smoothed",
            R=1,
            Q=2,
        )

        for index, det in enumerate(chain):
            ## Add smoothed center coords
            det["detection_center_smoothed"] = [
                centerChain_x[index]["detection_center_x_smoothed"],
                centerChain_y[index]["detection_center_y_smoothed"],
            ]
            ## ignore first detection
            if index > 0:
                prevDet = chain[index - 1]
                if prevDet is not None:
                    prevCenter = prevDet["detection_center_smoothed"]
                    prevTimestamp = prevDet["timestamp"]
                    center = det["detection_center_smoothed"]
                    timestamp = det["timestamp"]

                    dist = getDistanceBetween(p1=prevCenter, p2=center)
                    angle = getAngleBetween(p1=prevCenter, p2=center)
                    timeDifference = timestamp - prevTimestamp
                    ## speed = percentage of width per second
                    if dist > 0 and timeDifference > 0:
                        speed = dist / (timeDifference / 1000)
                    else:
                        speed = None
                    det["detection_center_smoothed"] = center
                    det["spatial_dist"] = dist
                    det["spatial_angle"] = angle
                    det["spatial_speed"] = speed
                    det["spatial_duration"] = timeDifference

        # Process spatial_angle with kalman filter
        processedChain = applyKalmanFilter(
            items=chain,
            inputKey="spatial_angle",
            outputKey="spatial_angle_smoothed",
            R=1,
            Q=90,
        )

        for index, det in enumerate(processedChain):
            ## add spatial_angle_smoothed to existing chain detection
            spatial_angle_smoothed = det["spatial_angle_smoothed"]
            chain[index]["spatial_angle_smoothed"] = spatial_angle_smoothed
            ## Add simplified text representation of angle (e.g. LEFT, RIGHT)
            angleSimple = getAngleSimple(
                degrees=spatial_angle_smoothed,
            )
            chain[index]["spatial_angle_simple"] = angleSimple

        chainsProcessed.append(chain)
    return chainsProcessed


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
