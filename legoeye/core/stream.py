import threading

class StreamManager:

    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                instance = super().__new__(cls)
                instance.streamingCount = 0
                instance.lock = threading.Lock()
                cls._instance = instance
                
        return cls._instance

    def increamentStreamingCount(self):
        with self.lock:
            self.streamingCount += 1

    def decrementStreamingCount(self):
        with self.lock:
            if self.streamingCount > 0:
                self.streamingCount -= 1

    def isStreaming(self):
        with self.lock:
            return self.streamingCount > 0
    