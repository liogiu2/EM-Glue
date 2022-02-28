from utilities import singleton
import time

@singleton
class EPEM_Manager:

    def __init__(self):
        pass

    def main_loop(self):
        """
        This method is the main loop of the EPEM. 
        """
        while True:
            time.sleep(1)