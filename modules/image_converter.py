import cv2
import numpy as np
from PIL import Image


def black_to_transparent(sprite):
    # Load image as Numpy array in BGR order
    np_array = cv2.imread(f"../static/sprites/pokemon/{sprite}")

    # Make a True/False mask of pixels whose BGR values sum to more than zero
    alpha = np.sum(np_array, axis=-1) > 0

    # Convert True/False to 0/255 and change type to "uint8" to match "na"
    alpha = np.uint8(alpha * 255)

    # Stack new alpha layer with existing image to go from BGR to BGRA, i.e. 3 channels to 4 channels
    result = np.dstack((np_array, alpha))

    # Save result
    cv2.imwrite(sprite, result)


def overlay_image(sprite, effect):
    sprite = Image.open(f"../static/sprites/pokemon{sprite}")
    effect = Image.open(effect)

    effect = effect.resize((96, 96))

    sprite.paste(effect)

    return sprite
