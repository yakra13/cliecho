from datetime import datetime
import time
from shared.module_logger import LOGGER

def sample_run():
    print("in sample run")
    start = datetime.now()
    for i in range(20):
        now = datetime.now()
        LOGGER.console_raw(f'{i}: elapsed time: {now - start}')
        time.sleep(10)
        
    LOGGER.console_raw('Complete')