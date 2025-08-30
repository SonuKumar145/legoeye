import threading

class RecordingError(Exception):
    """Base exception for recording-related issues."""
    pass

class RecordingStartError(RecordingError):
    """Raised when an attempt is made to start recording while one is already active."""
    pass

class RecordingStopError(RecordingError):
    """Raised when an attempt is made to stop recording while no recording is active"""
    pass

class recordManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                instance = super().__new__(cls)
                instance._isRecording = False

                instance.lock = threading.Lock()

                instance.recordingVideoID = None
                instance.recordingStartTimestamp = None
                cls._instance = instance

        return cls._instance


    @property
    def isRecording(self) -> bool:
        return self._isRecording
    
    @isRecording.setter
    def isRecording(self, v: bool):
        with self.lock:
            self._isRecording = v
    