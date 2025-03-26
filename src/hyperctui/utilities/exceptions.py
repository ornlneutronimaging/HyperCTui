class CropError(Exception):
    """
    Raised when something went wrong with the crop process
    """

    def __init__(self, message="Something went wrong during crop"):
        self.message = message
        super().__init__(self.message)


class CenterOfRotationError(Exception):
    """
    raised when the center of rotation initialization goes wrong
    """

    def __init__(self, message="Something went wrong during initialization of center of rotation"):
        self.message = message
        super().__init__(self.message)
