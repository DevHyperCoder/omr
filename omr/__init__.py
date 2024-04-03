import cv2
import numpy
import os

from omr.utils import *


def generate_aruco(id: int, path: str):
    """
    Command: gen-aruco
    Generates a ArUco tag of given id and saves to disk
    """
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    tag = numpy.zeros((100, 100, 1), dtype="uint8")
    aruco_dict.generateImageMarker(id, 100, tag, 1)
    cv2.imwrite(path, tag)


def generate_qrcode(data: str, path: str):
    """
    Command: gen-qr
    Generates a QR Code with given data and saves to disk
    """
    qr_enc = cv2.QRCodeEncoder()
    qr_img = qr_enc.encode(data)
    cv2.imwrite(path, qr_img)


def omr(fpath: str, temp_dir: str, answer_key):
    """
    Command: omr
    Processes a given OMR sheet image and returns the markings
    """

    img = cv2.imread(fpath)

    grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    cv2.imwrite(os.path.join(temp_dir, "grayscale.png"), grayscale)

    markers = get_aruco_codes(grayscale)
    if len(markers) == 0:
        print("Not valid OMR. ArUco code not found")
        exit(-1)

    omr_id = get_omr_qr_code(grayscale)
    if not omr_id:
        print("Not valid OMR. QR Code not found")
        exit(-1)

    print(f"OMR ID: {omr_id}")

    # thresh
    _, thresh = cv2.threshold(
        grayscale, 60, 200, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
    )
    # thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,23,3)
    cv2.imwrite(os.path.join(temp_dir, "thresh.png"), thresh)

    # thresh = cv2.Canny(grayscale, 60, 200)
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    cntImg = img.copy()
    cv2.drawContours(cntImg, contours, -1, (0, 255, 255), 3)
    cv2.imwrite(os.path.join(temp_dir, "contours.png"), cntImg)

    exam_code_bubble_contours: List[MatLike] = []
    roll_bubble_contours: List[MatLike] = []
    answer_bubble_contours: List[MatLike] = []

    height, width, _ = img.shape
    mid_mark_x = width * 0.5
    mark_h = height * 0.4

    for idx, c in enumerate(contours):
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

    sorted_exam_code_boundaries = sort_bounding_boxes(exam_code_bubble_contours)
    sorted_roll_boundaries = sort_bounding_boxes(roll_bubble_contours)
    sorted_answer_bubble_boundingboxes = sort_bounding_boxes(answer_bubble_contours)

    # bubble finding
    exam_code_bubbles = get_marked_bubbles(sorted_exam_code_boundaries, thresh)
    roll_bubbles = get_marked_bubbles(sorted_roll_boundaries, thresh)
    answer_bubbles = get_marked_bubbles(sorted_answer_bubble_boundingboxes, thresh)

    # {qno: ans}
    markings = {}

    for idx in answer_bubbles:
        row = idx // 12
        col = idx % 12

        choice = chr(ord("A") + col % 4)

        grp = col // 4
        qno = (row + grp * 10) + 1
        markings[qno] = choice

    exam_code_comps = ["", "", "", "", ""]
    for idx in exam_code_bubbles:
        row = idx // 5
        col = idx % 5
        exam_code_comps[col] = {0: "A", 1: "B", 2: "C", 3: "1", 4: "2"}[row]
    exam_code = "".join(exam_code_comps)

    roll_comps = [""] * 7
    for idx in roll_bubbles:
        row = idx // 7
        col = idx % 7

        roll_comps[col] = str((row + 1) % 10)
    roll = "".join(roll_comps)

    print(f"Exam Code: {exam_code}")
    print(f"Roll Code: {roll}")
    display_markings(markings)
    correct, incorrect, _ = grade_markings(markings, answer_key)
    total_marks = calculate_total(correct, incorrect)
    print("Marks:")
    print(f"\t- Correct:     {len(correct)}")
    print(f"\t- Incorrect:   {len(incorrect)}")
    print(f"\t- Total marks: {total_marks}")
