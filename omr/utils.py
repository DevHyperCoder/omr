import cv2
import numpy
from cv2.typing import MatLike
from typing import Any, List


class Marker:
    def __init__(self, id: int, corners: Any):
        self.id = id
        self.corners = corners


def get_aruco_codes(img: MatLike) -> List[Marker]:
    """
    Get all ArUco markers in given image
    """
    detector = cv2.aruco.ArucoDetector()
    corners, ids, _ = detector.detectMarkers(img)

    markers: List[Marker] = []

    ids = ids.flatten()
    for markerCorner, markerID in zip(corners, ids):
        corners = markerCorner.reshape((4, 2))
        markers.append(Marker(int(markerID), corners))
    return markers


def get_omr_qr_code(img: MatLike) -> str:
    """
    Get OMR QR Code data
    """
    qr_det = cv2.QRCodeDetector()
    data = qr_det.detectAndDecode(img)
    return data[0]


def sort_bounding_boxes(contours):
    """
    Sort rects left to right, then top to bottom

    Illustration:
    0 1 2 3 4
    5 6 7 8 9
    """

    bboxes = [cv2.boundingRect(c) for c in contours]
    max_height = max(map(lambda k: k[3], bboxes))

    # TODO: Magic value 1.2
    nearest = max_height * 1.2

    bbxs = list(bboxes)
    bbxs.sort(key=lambda r: [int(nearest * round(float(r[1]) / nearest)), r[0]])

    return bbxs


def get_marked_bubbles(boundaries, thresh):
    bubbled = []
    for idx, box in enumerate(boundaries):
        mask = numpy.zeros(thresh.shape, dtype="uint8")
        x, y, w, h = box
        cv2.rectangle(mask, (x, y), (x + w, y + h), (255, 255, 255), -1)
        masked = cv2.bitwise_and(thresh, thresh, mask=mask)

        non_zero = cv2.countNonZero(masked)
        # TODO: magic 200
        if non_zero > 400:
            bubbled.append(idx)
    return bubbled


def display_markings(markings):
    """
    Displays the answer markings done by the user in a nice "table" format
    """
    for qno, choice in sorted(markings.items(), key=lambda a: a[0]):
        numsp = abs(len(str(qno)) - 3) * " "
        print(f"{qno}:{numsp}{choice}")


def grade_markings(markings, answer_key):
    """
    Sorts the given markings into 3 sets
    """
    incorrect_qs = set()
    correct_qs = set()
    unmarked_qs = set()

    for qno, choice in markings.items():
        if choice == answer_key[qno]:
            correct_qs.add(qno)
        else:
            incorrect_qs.add(qno)

    all_qs = set(answer_key.keys())
    unmarked_qs = all_qs.difference(correct_qs.union(incorrect_qs))

    return correct_qs, incorrect_qs, unmarked_qs


def calculate_total(correct, incorrect):
    """
    Calculates final marks obtained.
    Each correct answer gets +3, while a wrong answer gets -1
    """
    return len(correct) * 3 - len(incorrect)
