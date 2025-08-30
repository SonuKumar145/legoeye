from utils.config import Config
import os
from werkzeug.utils import secure_filename
import importlib
import threading
from utils.paths import Paths
from utils.logger import Logger


logger = Logger.get_logger(__name__)


class scriptManager:

    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                instance = super().__new__(cls)
                instance.config = Config()
                instance.lock = threading.Lock()
                instance.paths = Paths()
                cls._instance = instance
                
        return cls._instance

    def init(self):
        self.mains_of_frame_processing_scripts = self.mains_of_scripts_builder(self.config.get("frame_processing_scripts_settings.TYPE"))
        self.mains_of_pre_picam_init_scripts = self.mains_of_scripts_builder(self.config.get("pre_picam_init_scripts_settings.TYPE"))
        self.mains_of_post_picam_init_scripts = self.mains_of_scripts_builder(self.config.get("post_picam_init_scripts_settings.TYPE"))
        

    def script_detail_returner(self, script_type):
            if(script_type == self.config.get("frame_processing_scripts_settings.TYPE")):
                return {                     
                'script': "frame_processing_scripts_settings.SCRIPTS",
                'script_dir': self.paths.FRAME_PROCESSING_SCRIPTS_DIR
                }
                
            elif(script_type == self.config.get("pre_picam_init_scripts_settings.TYPE")):
                return {                     
                'script' : "pre_picam_init_scripts_settings.SCRIPTS",
                'script_dir' : self.paths.PRE_PICAM_INIT_SCRIPT_DIR
                }

            elif(script_type == self.config.get("post_picam_init_scripts_settings.TYPE")):
                return {
                'script' : "post_picam_init_scripts_settings.SCRIPTS",
                'script_dir' : self.paths.POST_PICAM_INIT_SCRIPT_DIR
                }
            else:
                 raise ValueError(f"Unknown or unsupported script type: {script_type}")

    def addScript(self, dir, file, filename, script_type=None ):

        config_will_be_set = True
        
        if(dir and script_type == None and os.path.exists(os.path.expanduser(dir))):
             config_will_be_set = False
             script_dir = dir
        else:
            script_details = self.script_detail_returner(script_type=script_type)
            script_to_set = script_details['script']
            script_dir = script_details['script_dir']

        with self.lock:
            try:
                file_path = os.path.join(script_dir,secure_filename(filename))
                file.save(file_path)
                if config_will_be_set:
                    self.config.set(script_to_set, self.config.get(script_to_set).append(filename))
                return file_path
            except Exception as e:
                logger.error(f"Error occured while adding script {filename} : {e}")
                return None
    
    
    def deleteScript(self, dir, filename, script_type = None):
        config_will_be_set = True
        if(dir and script_type == None and os.path.exists(os.path.expanduser(dir))):
             config_will_be_set = False
             script_dir = dir
        else:
            script_details = self.script_detail_returner(script_type=script_type)
            script_to_delete_from = script_details['script']
            script_dir = script_details['script_dir']

        with self.lock:
            full_file_path = os.path.join(
                 script_dir,
                 secure_filename(filename)
                 )

            if os.path.exists(full_file_path):
                try:
                    os.remove(full_file_path)
                    if(config_will_be_set and filename in self.config.get(script_to_delete_from)):
                        self.config.set(script_to_delete_from,self.config.get(script_to_delete_from).remove(filename))

                    logger.info(f"File '{full_file_path}' deleted successfully.")
                    return True
                except OSError as e:
                    logger.error(f"Error deleting file '{full_file_path}': {e}")
                    return False
            else:
                logger.warn(f"File '{full_file_path}' does not exist.")
                return False
    
    
    def disableScript(self,script_type, filename):
        script_details = self.script_detail_returner(script_type=script_type)
        script_to_disable_from = script_details['script']
        
        with self.lock:
            try:
                if(filename in self.config.get(script_to_disable_from)):
                        self.config.set(script_to_disable_from,self.config.get(script_to_disable_from).remove(filename))
                        return True
                else: return False
            except Exception as e:
                    logger.error(f"Error disable script '{filename}': {e}")
                    return False
        
        
    def enableScript(self, filename):
        with self.lock:
            try:
                if(filename in self.config.get('scripts_settings.SCRIPTS')):
                        self.config.set('scripts_settings.SCRIPTS',self.config.get('scripts_settings.SCRIPTS').remove(filename))
                        return True
                else : return False
            except Exception as e:
                    logger.log(f"Error disable script '{filename}': {e}")
                    return False
        

    def mains_of_scripts_builder(self, script_type)->list:
            
            script_details = self.script_detail_returner(script_type=script_type)
            script_arr = script_details['script']
            scriptdir = script_details['script_dir']

            frame_processing_type = self.config.get("frame_processing_scripts_settings.TYPE")
            pre_picam_init_type = self.config.get("pre_picam_init_scripts_settings.TYPE")
            post_picam_init_type = self.config.get("post_picam_init_scripts_settings.TYPE")

            if script_type == frame_processing_type:
                rel_script_dir = self.paths.REL_FRAME_PROCESSING_SCRIPTS_DIR
            elif script_type == pre_picam_init_type:
                rel_script_dir = self.paths.REL_PRE_PICAM_INIT_SCRIPT_DIR
            elif script_type == post_picam_init_type:
                rel_script_dir = self.paths.REL_POST_PICAM_INIT_SCRIPT_DIR
            else:
                raise ValueError(f"Unknown or unsupported script type: {script_type}")
      
            logger.debug(f"script dir : {scriptdir}")

            mains=[]
            for s in self.config.get(script_arr):
                full_path = os.path.join(scriptdir, s)

                if not s.endswith('.py'):
                    logger.warn(f"File {s} doesn't end with .py")
                    continue

                if os.path.exists(full_path):
                    module_name = s[:-3]
                    try:
                        logger.info(f"Going to import module {module_name} with rel path : {rel_script_dir.replace('/', '.')}.{module_name}")
                        mod = importlib.import_module(f"{rel_script_dir.replace('/', '.')}.{module_name}")
                        logger.info(f"Module {module_name} imported!")
                    except ImportError as e:
                        logger.error(f"Importing {module_name} failed: {e}")
                        continue
                    if hasattr(mod, 'main'):
                        mains.append(mod.main)
                    else:
                        logger.warn(f"Module {module_name} doesn't have main function")
                else:
                     logger.warn(f"Path {full_path} doesn't exist.")
            return mains
    
    def run_frame_processing_scripts(self, params):
        mains = self.mains_of_frame_processing_scripts
        for m in mains:
            m(params)

    def run_pre_picam_init_scripts(self):
        mains = self.mains_of_pre_picam_init_scripts
        for m in mains:
            m()

    def run_post_picam_init_scripts(self):
        mains = self.mains_of_post_picam_init_scripts
        for m in mains:
            m()


