import logging
import os
from dotenv import load_dotenv

# Absolute path (/app/)
base_path = os.path.dirname(os.path.abspath(__file__))

load_dotenv()

def setup_logger(name, log_file, level=logging.INFO):
    log_directory = os.path.join(base_path, 'logs')
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    
    handler = logging.FileHandler(os.path.join(log_directory, log_file), encoding='utf-8')
    formatter = logging.Formatter("[%(asctime)s - %(filename)18s:%(lineno)4s - %(funcName)20s()] %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
    
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    return logger

# Configurar el logger principal de la aplicación
app_logger = setup_logger('app_logger', 'app.log', logging.DEBUG)

# Configurar el logger para la ejecución de crontab
cron_logger = setup_logger('cron_logger', 'cron.log', logging.INFO)

# Desactivar la propagación para ambos loggers
app_logger.propagate = False
cron_logger.propagate = False