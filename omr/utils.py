import cv2
import numpy
from cv2.typing import MatLike, Rect
from typing import Any, List


def rename(bbox: List[Any], w, h):
    return [
        (((x + bw / 2) / w) * 100, ((y + bh / 2) / h) * 100) for x, y, bw, bh in bbox
    ]


class MarkedOMRBubbles:
    def __init__(self, img, exam_code_contours, roll_contours, answer_contours):
        self.exam_code_bubbles, self.roll_bubbles, self.answer_bubbles = [
            get_marked_bubbles(sort_bounding_boxes(cnt), img)
            for cnt in [exam_code_contours, roll_contours, answer_contours]
        ]


def get_bubble_contours(contours, w, h):
    """
    Groups the given contours
    """

    exam_code_bubble_contours: List[MatLike] = []
    roll_bubble_contours: List[MatLike] = []
    answer_bubble_contours: List[MatLike] = []

    mid_mark_x = w * 0.5
    mark_h = h * 0.4

    for c in contours:
        (x, y, w, h) = cv2.boundingRect(c)
        ratio = w / float(h)

        # signed area
        area = cv2.contourArea(c, True)

        if ratio >= 1.3 and ratio <= 1.7 and w > 30 and w < 120:
            if area < 0:
                if y > mark_h:
                    answer_bubble_contours.append(c)
                elif x > mid_mark_x:
                    roll_bubble_contours.append(c)
                elif x < mid_mark_x:
                    exam_code_bubble_contours.append(c)
    return (exam_code_bubble_contours, roll_bubble_contours, answer_bubble_contours)


def get_marked_omr_bubbles(img, contours, w, h):
    (
        exam_code_bubble_contours,
        roll_bubble_contours,
        answer_bubble_contours,
    ) = get_bubble_contours(contours, w, h)

    return MarkedOMRBubbles(
        img, exam_code_bubble_contours, roll_bubble_contours, answer_bubble_contours
    )


class Marker:
    def __init__(self, id: int, corners: Any):
        self.id = id
        self.corners = corners

    def __repr__(self):
        tl, _, _, _ = self.corners
        return f"ArUco marker: {self.id} @ {tl}"


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
    markers.sort(key=lambda m: m.id)
    return markers


def get_omr_qr_code(img: MatLike) -> tuple[str, Any]:
    """
    Get OMR QR Code data
    """
    qr_det = cv2.QRCodeDetector()
    data = qr_det.detectAndDecode(img)
    return (data[0], data[1].reshape((4, 2)))


def sort_bounding_boxes(contours) -> List[Rect]:
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
        # TODO: magic 2000
        if non_zero > 2000:
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
