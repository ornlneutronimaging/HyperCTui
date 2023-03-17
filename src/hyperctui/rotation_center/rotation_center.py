import numpy as np


class RotationCenter:

    def __init__(self, parent=None):
        self.parent = parent

    def initialize(self):
        self.parent.rotation_center_image_view.clear()

        left = self.parent.ui.crop_left_spinBox.value()
        right = self.parent.ui.crop_right_spinBox.value()
        top = self.parent.ui.crop_top_spinBox.value()
        bottom = self.parent.ui.crop_bottom_spinBox.value()

        self.parent.rotation_center_live_image = self.parent.crop_live_image[top: bottom+1, left: right+1].copy()
        self.parent.rotation_center_image_view.setImage(np.transpose(self.parent.rotation_center_live_image))
