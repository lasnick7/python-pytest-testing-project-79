import os
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def validate_path(output_dir):
    if not isinstance(output_dir, (str, os.PathLike)):
        logger.error('Output_dir must be a path-like object')
        raise TypeError

    if not os.path.exists(output_dir):
        logger.error(f"Directory does not exist: {output_dir}")
        raise FileNotFoundError

    if not os.path.isdir(output_dir):
        logger.error(f"Not a directory: {output_dir}")
        raise NotADirectoryError

    if not os.access(output_dir, os.W_OK | os.X_OK):
        logger.error(f"No write permission for: {output_dir}")
        raise PermissionError