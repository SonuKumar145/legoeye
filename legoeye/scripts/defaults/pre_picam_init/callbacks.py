#TODO: implement the automatic imports of all main functions from all the scripts from pre_callback directory (set in the config file)
#? for now we are just manually calling all the callback functions from the pre_callback directory manually

from ..pre_callback.timestamp import main as timestamp_main
from core.picam import PicamManager
from utils.logger import Logger

picamMngr = PicamManager()
logger = Logger.get_logger(__name__)

def main(request):
    '''call your callback functions here'''

    timestamp_main(request)
