import logging


# info_logger_setup
info_logger = logging.getLogger('Info_Logger')
info_logger.setLevel(logging.INFO)
fh_info = logging.FileHandler('good_log.log', encoding='utf-8')
fh_info.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh_info.setFormatter(formatter)
info_logger.addHandler(fh_info)

# error_logger_setup
error_logger = logging.getLogger('Error_Logger')
error_logger.setLevel(logging.ERROR)
fh_error = logging.FileHandler('error_log.log', encoding='utf-8')
fh_error.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh_error.setFormatter(formatter)
error_logger.addHandler(fh_error)
