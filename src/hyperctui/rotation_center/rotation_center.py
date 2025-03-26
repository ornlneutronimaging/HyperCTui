import numpy as np


class RotationCenter:
    def __init__(self, parent=None):
        self.parent = parent

    def initialize(self):
        self.parent.rotation_center_image_view.clear()

        left = int(self.parent.ui.crop_left_label_value.text())
        right = int(self.parent.ui.crop_right_label_value.text())

        self.parent.rotation_center_live_image = self.parent.crop_live_image[:, left : right + 1].copy()
        self.parent.rotation_center_image_view.setImage(np.transpose(self.parent.rotation_center_live_image))
