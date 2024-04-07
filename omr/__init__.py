import pickle
import cv2
import numpy
import os

from omr.utils import *

from omr.cmd.generate import generate_aruco, generate_qrcode
from omr.cmd.template import template, OMRTemplate


def omr(template_path: str, fpath: str, temp_dir: str, answer_key):
    """
    Command: omr
    Processes a given OMR sheet image according to template and returns the markings

    Template is used for accurate positioning of bubbles.
    """

    # Loading the template, exit if unable to load
    omr_template: OMRTemplate | None = None
    with open(template_path, "rb") as f:
        omr_template = pickle.load(f)

    if not omr_template:
        print("Unable to load omr_template")
        exit(-1)

    img = cv2.imread(fpath)
    h, w, _ = img.shape

    grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    markers = get_aruco_codes(img)
    if len(markers) == 0:
        print("Not valid OMR. ArUco code not found")
        exit(-1)

    a1x, a1y = omr_template.aruco1
    (tlx, tly), _, _, _ = markers[1].corners
    A1x, A1y = tlx * 100 / w, tly * 100 / h
    _, d1y = a1x - A1x, a1y - A1y

    omr_id, _ = get_omr_qr_code(grayscale)
    if not omr_id:
        print("Not valid OMR. QR Code not found")
        exit(-1)

    print(f"OMR ID: {omr_id}")

    # thresh
    _, thresh = cv2.threshold(
        grayscale, 75, 200, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
    )

    contours, _ = cv2.findContours(
        cv2.GaussianBlur(thresh, (9, 9), 5), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
    )

    exam_contours = []
    roll_contours = []
    anws_contours = []

    for c in contours:
        area = cv2.contourArea(c, True)

        if area < 0:
            (_, _, cw, ch) = cv2.boundingRect(c)
            ratio = cw / ch
            if ratio >= 1.3 and ratio <= 1.7 and cw > 30 and cw < 130:
                for wperc, hperc in omr_template.exam_code:
                    x = int(wperc * w / 100)
                    y = int(hperc * h / 100)
                    if cv2.pointPolygonTest(c, (x, y), False) >= 0.0:
                        exam_contours.append(c)
                for wperc, hperc in omr_template.roll:
                    x = int(wperc * w / 100)
                    y = int(hperc * h / 100)
                    if cv2.pointPolygonTest(c, (x, y), False) >= 0.0:
                        roll_contours.append(c)

                for wperc, hperc in omr_template.answers:
                    x = int(wperc * w / 100)
                    y = int((hperc - d1y) * h / 100)
                    if cv2.pointPolygonTest(c, (x, y), False) >= 0.0:
                        anws_contours.append(c)

    assert len(exam_contours) == 25, "25 Exam code bubbles not found!"
    assert len(roll_contours) == 70, "70 Roll code bubbles not found!"
    assert len(anws_contours) == 30 * 4, "120 Answer code bubbles not found!"

    marked_omr_bubbles = MarkedOMRBubbles(
        thresh, exam_contours, roll_contours, anws_contours
    )

    # {qno: ans}
    markings = {}

    for idx in marked_omr_bubbles.answer_bubbles:
        row = idx // 12
        col = idx % 12

        choice = chr(ord("A") + col % 4)

        grp = col // 4
        qno = (row + grp * 10) + 1
        markings[qno] = choice

    exam_code_comps = ["", "", "", "", ""]
    for idx in marked_omr_bubbles.exam_code_bubbles:
        row = idx // 5
        col = idx % 5
        exam_code_comps[col] = {0: "A", 1: "B", 2: "C", 3: "1", 4: "2"}[row]
    exam_code = "".join(exam_code_comps)

    roll_comps = [""] * 7
    for idx in marked_omr_bubbles.roll_bubbles:
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
