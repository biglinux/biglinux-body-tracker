import cv2
import numpy as np
from PIL import Image

class VideoSource:
    def __init__(self, flip=False, display=False, dtype=np.uint8):
        self._name = "VideoSource"
        self._capture = None
        self._display = display
        self._dtype = dtype
        self._flip = flip

    def get_fps(self):
        return self._capture.get(cv2.CAP_PROP_FPS)

    def get_frame_count(self):
        return int(self._capture.get(cv2.CAP_PROP_FRAME_COUNT))

    def get_image_size(self):
        width = self._capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        return width, height

    def release(self):
        self._capture.release()
        cv2.destroyAllWindows()

    def __iter__(self):
        self._capture.isOpened()
        return self

    def __next__(self):
        ret, frame = self._capture.read()

        if self._flip:
            frame = cv2.flip(frame, 3)

        if not ret:
            raise StopIteration

        if cv2.waitKey(1) & 0xFF == ord("q"):
            raise StopIteration

        cv2_im_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = np.asarray(Image.fromarray(cv2_im_rgb), dtype=self._dtype)

        return frame, frame_rgb

    def __del__(self):
        self.release()

    def gain(self, gain):

        Gain = self._capture.get(cv2.CAP_PROP_GAIN)
        Brightness = self._capture.get(cv2.CAP_PROP_BRIGHTNESS)
        Contrast = self._capture.get(cv2.CAP_PROP_CONTRAST)
        Gamma = self._capture.get(cv2.CAP_PROP_GAMMA)
        Backlight = self._capture.get(cv2.CAP_PROP_BACKLIGHT)

        if gain == 1:
            self._capture.set(cv2.CAP_PROP_GAIN, Gain + 2)
            self._capture.set(cv2.CAP_PROP_BRIGHTNESS, Brightness + 1)
            self._capture.set(cv2.CAP_PROP_CONTRAST, Contrast + 2)
            self._capture.set(cv2.CAP_PROP_GAMMA, Gamma + 1)
            self._capture.set(cv2.CAP_PROP_BACKLIGHT, Backlight + 1)
        elif gain == 0:
            self._capture.set(cv2.CAP_PROP_GAIN, Gain - 2)
            self._capture.set(cv2.CAP_PROP_BRIGHTNESS, Brightness - 1)
            self._capture.set(cv2.CAP_PROP_CONTRAST, Contrast - 2)
            self._capture.set(cv2.CAP_PROP_GAMMA, Gamma - 2)
            self._capture.set(cv2.CAP_PROP_BACKLIGHT, Backlight - 1)


    def show(self, frame, webcamx, webcamy):
        cv2.namedWindow("BigHeadTrack", cv2.WINDOW_GUI_NORMAL)
        cv2.imshow("BigHeadTrack", frame)
        cv2.resizeWindow("BigHeadTrack", webcamx, webcamy)


class WebcamSource(VideoSource):
    def __init__(
        self,
        camera_id=0,
        width=1024,
        height=768,
        fps=15,
        autofocus=0,
        absolute_focus=75,
        flip=True,
        display=False,
    ):
        super().__init__(flip, display)
        self._capture = cv2.VideoCapture(camera_id, cv2.CAP_V4L2)
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        self._capture.set(cv2.CAP_PROP_GAIN, 0)
        self._capture.set(cv2.CAP_PROP_EXPOSURE, (1 / (fps / 10000)))
        self._capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        self._capture.set(cv2.CAP_PROP_FPS, fps)
        self._capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3)
        self._capture.set(cv2.CAP_PROP_FOCUS, absolute_focus / 255)


class FileSource(VideoSource):
    def __init__(self, file_path, flip=False, display=False):
        super().__init__(flip, display)
        self._capture = cv2.VideoCapture(str(file_path))
