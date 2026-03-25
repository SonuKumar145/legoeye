# ██╗░░██╗██╗░█████╗░██╗░░██╗░██████╗████████╗░█████╗░██████╗░████████╗
# ██║░██╔╝██║██╔══██╗██║░██╔╝██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝
# █████═╝░██║██║░░╚═╝█████═╝░╚█████╗░░░░██║░░░███████║██████╔╝░░░██║░░░
# ██╔═██╗░██║██║░░██╗██╔═██╗░░╚═══██╗░░░██║░░░██╔══██║██╔══██╗░░░██║░░░
# ██║░╚██╗██║╚█████╔╝██║░╚██╗██████╔╝░░░██║░░░██║░░██║██║░░██║░░░██║░░░
# ╚═╝░░╚═╝╚═╝░╚════╝░╚═╝░░╚═╝╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░

def update_configs(config, overrides=None):
    if(overrides == None):
        return
    for path, value in overrides.items():
        # skip None values
        if value is None:
            continue
        config.set(path,value)
        print(f"{path}={value} updated")
    if(len(overrides)>0):
        config.save()
        config.reload()
        print("config saved and reloaded")


def init_utils(overrides=None):
    from utils.config import Config
    from utils.paths import Paths
    from utils.logger import Logger

    config = Config()
    update_configs(config,overrides)

    path = Paths()
    logger = Logger()

    #* need to do this because config needs logger and logger needs config and path but path needs config
    #* to prevent deadlock situation, not import logger in config but passing logger as parameter and initialising config, path and logger later on
    logger.init()
    config.init(logger=Logger)
    path.init()
    logger.init()   #* need to reinitialize as config and path gets initialized to setup with actual config variables

    logger = Logger.get_logger(__name__)
    logger.info("Config, Paths and Logger got initialised")
    
    return config, path, logger


def init_core():
    from core.picam import PicamManager
    from core.database import DBHandler
    from core.stream import StreamManager
    from core.record import recordManager
    from core.scripts import scriptManager

    DBHandler()
    PicamManager()
    recordManager()
    scriptMngr = scriptManager()
    StreamManager()

    scriptMngr.init()

    return scriptMngr

def kickstart(overrides=None):
    """Initializes all essential 
    - singleton managers,
    - application configurations and 
    - other stuffs that are needed to be initialised in the startup.

    Args:
        None: This function does not accept any arguments.

    Returns:
        None: This function does not return any value.

    Note:
        Each instantiated class (`Config`, `Paths`, `Logger`, etc.)
        is designed as a singleton, meaning repeated calls to its
        constructor will return the same or globally managed instance.
    """

    print('''
    █▄▀ █ █▀▀ █▄▀ █▀ ▀█▀ ▄▀█ █▀█ ▀█▀ █ █▄░█ █▀▀   █░░ █▀▀ █▀▀ █▀█ █▀▀ █▄█ █▀▀
    █░█ █ █▄▄ █░█ ▄█ ░█░ █▀█ █▀▄ ░█░ █ █░▀█ █▄█   █▄▄ ██▄ █▄█ █▄█ ██▄ ░█░ ██▄
    ''')



    from recovery.recovery import recover
    from recovery.last_time import time_writer_thread
    from server.server import server_app

    # █░█ ▀█▀ █ █░░ █▀
    # █▄█ ░█░ █ █▄▄ ▄█
    config,_,logger = init_utils(overrides)
    if (not config.config_loaded_status):
        logger("Config loading failed. Unable to start Legoeye.")

    # █▀▀ █▀█ █▀█ █▀▀
    # █▄▄ █▄█ █▀▄ ██▄
    logger.info("Initialising core modules")
    scriptMngr = init_core()
    logger.info("Core modules initialised")

    
    # █▀█ █▀▀ █▀▀ █▀█ █░█ █▀▀ █▀█ █▄█
    # █▀▄ ██▄ █▄▄ █▄█ ▀▄▀ ██▄ █▀▄ ░█░
    logger.info("Recovery process initiated")
    recover()


    # ▀█▀ █ █▀▄▀█ █▀▀   █░█░█ █▀█ █ ▀█▀ █▀▀ █▀█
    # ░█░ █ █░▀░█ ██▄   ▀▄▀▄▀ █▀▄ █ ░█░ ██▄ █▀▄
    logger.info("Initializing time_writer_thread...")
    time_writer_thread()


    # █▀ █▀▀ █▀█ █ █▀█ ▀█▀ █▀
    # ▄█ █▄▄ █▀▄ █ █▀▀ ░█░ ▄█
    logger.info("Executing default scripts...")

    scriptMngr.run_pre_picam_init_scripts()
    logger.info("Pre-Picam initialization scripts executed.")

    scriptMngr.run_post_picam_init_scripts()
    logger.info("Post-Picam initialization scripts executed.")


    # █▀ █▀▀ █▀█ █░█ █▀▀ █▀█
    # ▄█ ██▄ █▀▄ ▀▄▀ ██▄ █▀▄
    logger.info("Starting Flask server!")
    return server_app()


#--------------------------------------------
#--------------------------------------------
# █▄▀ █ █▀▀ █▄▀ █▀ ▀█▀ ▄▀█ █▀█ ▀█▀ █ █▄░█ █▀▀
# █░█ █ █▄▄ █░█ ▄█ ░█░ █▀█ █▀▄ ░█░ █ █░▀█ █▄█
#--------------------------------------------
#--------------------------------------------

if __name__ == "__main__":
    # For dev mode: Run full kickstart, get app, then start dev server
    app = kickstart()  # This runs all init
    if app:
        ssl_cert = "/home/lulbro/.sslkeys/cert.pem"
        ssl_key = "/home/lulbro/.sslkeys/key.pem"

        app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False, ssl_context=(ssl_cert, ssl_key))
    else:
        print("Failed to initialize app.")