try:
    import cv2

    print("cv2: available")
except ImportError:
    print("cv2: missing")

try:
    import numpy

    print("numpy: available")
except ImportError:
    print("numpy: missing")

try:
    import scipy.ndimage

    print("scipy: available")
except ImportError:
    print("scipy: missing")

try:
    import skimage.measure

    print("skimage: available")
except ImportError:
    print("skimage: missing")
