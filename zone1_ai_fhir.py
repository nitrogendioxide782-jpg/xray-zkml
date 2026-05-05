import cv2
import numpy as np

def load_image(image_path, size=64):

    # RGB / 3-channel
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)

    if img is None:
        raise ValueError("Image not found")

    # BGR → RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # resize to model size
    img = cv2.resize(img, (size, size))

    # normalize
    img = img / 255.0

    # (H,W,C) → (C,H,W)
    img = np.transpose(img, (2, 0, 1))

    # batch dim
    img = np.expand_dims(img, axis=0)

    return img.astype(np.float32)