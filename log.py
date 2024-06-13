import logging
import os

# Ensure the log file exists
log_filename = 'ecommerce.log'
if not os.path.exists(log_filename):
    open(log_filename, 'w').close()

# Set up logging configuration
logging.basicConfig(filename=log_filename, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
