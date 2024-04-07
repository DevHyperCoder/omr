# OMR Parsing

This is a project to tinker around with [OpenCV](https://opencv.org/). It aims
to 'parse' OMR sheets and record the information

Currently the OMR sheets are generated using Inkscape. Processing of scanned
OMR copies work 90% of the time, the preprocessing of the images still need
work.

The OMR sheets contains a QR code which can be used for identification and 2
ArUco markers.


# How to run ?


You need to install `opencv-python` and `numpy`

## Trying with given samples:

```console
# Generating template
python main.py template res/omr.png res/omr.template

# Parsing a sample OMR
python main.py parse res/sample1.jpg res/omr.template
```

A few sample images are provided in res/

## Generating template:

```console
python main.py template omr.png omr.template
```

Here `omr.png` is a "soft-copy" of the OMR sheet (designed in Inkscape), `omr.template` will contain the relative positions of markers on the OMR (QRCode and the 2 ArUco codes) and bubbles.

> NOTE: You can print `omr.png` in a A4 sized paper, fill it out and scan it in 300 dpi (2580x3507) for parsing. Automatic resizing of scanned images is being worked on.

## Parsing OMR

```console
python main.py parse image.png omr.template
```

Here `image.png` is the scanned OMR image

# License

Currently licensed under [GPL3](./LICENSE)
