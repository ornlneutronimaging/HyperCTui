import numpy as np


class RotationCenter:

    def __init__(self, parent=None):
        self.parent = parent

    def initialize(self):
        self.parent.rotation_center_image_view.clear()
        self.parent.rotation_center_image_view.setImage(np.transpose(self.parent.crop_live_image))
