# OMR Parsing

This is a project to tinker around with [OpenCV](https://opencv.org/). It aims
to 'parse' OMR sheets and record the information

Currently the OMR sheets are generated using Inkscape. Processing of scanned
OMR copies work 90% of the time, the preprocessing of the images still need
work.

The OMR sheets contains a QR code which can be used for identification and 2
ArUco markers (ArUco markers are currently unused but I have plans for them
soon)

# How to run ?

> Still in WIP, an example image is provided [here](./res/a1.png)

You need to install `opencv-python` and `numpy`

```console
python main.py parse res/a1.png
```

# License

Currently licensed under [GPL3](./LICENSE)
