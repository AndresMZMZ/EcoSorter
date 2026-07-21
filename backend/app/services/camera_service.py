import os

import cv2


class CameraService:
    def __init__(self, camera_index: int | None = None) -> None:
        self.camera_index = (
            camera_index
            if camera_index is not None
            else int(os.getenv("CAMERA_INDEX", "0"))
        )
        self._capture: cv2.VideoCapture | None = None

    def _get_capture(self) -> cv2.VideoCapture:
        if self._capture is None or not self._capture.isOpened():
            self._capture = cv2.VideoCapture(self.camera_index)
            if not self._capture.isOpened():
                raise RuntimeError(
                    f"No se pudo abrir la cámara en el índice {self.camera_index}"
                )
        return self._capture

    def read_frame(self):
        capture = self._get_capture()
        success, frame = capture.read()
        if not success or frame is None:
            raise RuntimeError("No se pudo capturar un frame de la cámara")
        return frame

    def release(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None


camera_service = CameraService()
