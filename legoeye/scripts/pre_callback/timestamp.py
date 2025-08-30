import cv2
import time
from picamera2 import MappedArray
from utils.config import Config
from core.picam import PicamManager


def font_returner(font_text):
    match font_text:
        case "Hershey Simplex":
            return cv2.FONT_HERSHEY_SIMPLEX
        case "Hershey Plain":
            return cv2.FONT_HERSHEY_PLAIN
        case "Hershey Duplex":
            return cv2.FONT_HERSHEY_DUPLEX
        case "Hershey Complex":
            return cv2.FONT_HERSHEY_COMPLEX
        case "Hershey Triplex":
            return cv2.FONT_HERSHEY_TRIPLEX
        case "Hershey Complex Small":
            return cv2.FONT_HERSHEY_COMPLEX_SMALL
        case "Hershey Script Simplex":
            return cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
        case "Hershey Script Complex":
            return cv2.FONT_HERSHEY_SCRIPT_COMPLEX

def main():

    config = Config()
    picamMngr = PicamManager()

    COLOR_R = config.get("timestamp.COLOR_R")
    COLOR_G = config.get("timestamp.COLOR_G")
    COLOR_B = config.get("timestamp.COLOR_B")
    ORIGIN_X = config.get("timestamp.ORIGIN_X")
    ORIGIN_Y = config.get("timestamp.ORIGIN_Y")
    SCALE = config.get("timestamp.SCALE")
    THICKNESS = config.get("timestamp.THICKNESS")
    ITALIC = config.get("timestamp.ITALIC")
    FONT = config.get("timestamp.FONT")

    colour = (COLOR_R, COLOR_G, COLOR_B)
    origin = (ORIGIN_X, ORIGIN_Y)

    def apply_timestamp(request):
        timestamp = time.strftime("%Y-%m-%d %X")
        with MappedArray(request, "main") as m:
            cv2.putText(m.array, timestamp, origin, ((font_returner(FONT) | cv2.FONT_ITALIC) if ITALIC else font_returner(FONT) ), SCALE, colour, THICKNESS)
    
    picamMngr.picam2.pre_callback = [apply_timestamp]


                    