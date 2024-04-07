import cv2
import numpy


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
