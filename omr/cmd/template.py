import cv2, numpy
import pickle

from omr.utils import *

class OMRTemplate:
    def __init__(self):
        self.qr = (0,0)
        self.aruco0 = (0,0)
        self.aruco1 = (0,0)
        self.aspect_ratio = 0.0
        self.exam_code = []
        self.roll = []
        self.answers = []
        self.avg_w = 0.0
        self.avg_h = 0.0

    def __str__(self):
        return f"""
Aspect Ratio: {self.aspect_ratio:.2f}
Avg W,H: {self.avg_w:.2f},{self.avg_h:.2f}
    ArUco #0: {self.aruco0[0]:.2f},{self.aruco0[1]:.2f}
    ArUco #1: {self.aruco1[0]:.2f},{self.aruco1[1]:.2f}"""

def template(template_path: str, dump_path: str):
    omr_template = OMRTemplate()

    img = cv2.imread(template_path)
    grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    h,w, _ = img.shape
    omr_template.aspect_ratio = w/h

    _, qrcorners = get_omr_qr_code(img)
    (tlx,tly), _,_,_ = qrcorners
    omr_template.qr = tlx * 100/w, tly*100/h

    markers = get_aruco_codes(img)
    assert len(markers) == 2, "Two ArUco codes needed!"

    _, thresh = cv2.threshold(
        grayscale, 60, 200, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
    )

    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    e,r,a = get_bubble_contours(contours, w,h)
    assert len(e) == 25, "25 Exam code bubbles needed!"
    assert len(r) == 70, "70 Roll bubbles needed!"
    assert len(a) == 120, "120 Answer bubbles needed!"

    # Width and Height markers using ArUco
    (tlx,tly), _, _, _ = markers[0].corners
    omr_template.aruco0 = tlx*100/w, tly*100/h
    (tlx,tly), _, _, _ = markers[1].corners
    omr_template.aruco1 = tlx*100/w, tly*100/h
    
    eb,rb,ab = [sort_bounding_boxes(b) for b in [e,r,a]]
    omr_template.exam_code, omr_template.roll, omr_template.answers = [rename(b, w, h) for b in [eb,rb,ab]]

    # avg width and height of a bubble
    whs = [(w,h) for _,_, w,h in eb+rb+ab]

    w_sum = 0
    h_sum = 0

    for (w,h) in whs:
        w_sum +=w
        h_sum +=h


    h,w, _ = img.shape
    omr_template.avg_w = (w_sum / len(whs))*100/w
    omr_template.avg_h = (h_sum / len(whs))*100/h

    with open(dump_path, "wb") as f:
        pickle.dump(omr_template, f)


    print(f"Saved to {dump_path}.")
    print(str(omr_template))

