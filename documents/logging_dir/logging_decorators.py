from documents.logging_dir.setup_logger import info_logger, error_logger


def init_logger(func):
    def wrapper(self, user_id, path, primary=False):
        try:
            func(self, user_id, path, primary)
        except ValueError as error:
            error_logger.error(f'Error: {str(error)} occurred with file: {path}')
        else:
            if primary:
                info_logger.info(f'File {path} was initiated')
    return wrapper


def sign_logger(func):
    def wrapper(self):
        try:
            func(self)
        except ValueError as error:
            error_logger.error(f'Error: {str(error)} occurred with file: {self.path}')
        else:
            info_logger.info(f'File {self.path} was signed by user {self.user_id}')
    return wrapper
