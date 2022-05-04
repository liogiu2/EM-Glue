from platform_communication import PlatformCommunication
import time

class ExperienceManager:

    PDDL_domain_text = ""
    PDDL_problem_text = ""

    def __init__(self) -> None:
        self.platform_communication = PlatformCommunication()

    def start_platform_communication(self):
        """
        This method is used to start the communication with the platform using the communication protocol.
        """
        print("Starting platform communication")
        self.wait_platform_online()
        #Handshake -- Phase 1
        print("Handshake -- Phase 1")
        message = self.platform_communication.get_handshake_message("PHASE_1", "message_1") + " Experience Manager"
        response = self.platform_communication.send_message(message, inizialization = True)
        if response is None:
            raise Exception("Error: Communication with platform failed.")
        if response['text'] == self.platform_communication.get_handshake_message("PHASE_1", "message_2"):
            print("Handshake -- phase 1 successful.")
        else:
            raise Exception("Error: Received unexpected message: " + response['text'])
        #Handshake -- Phase 3
        print("Handshake -- Phase 3")
        print("Waiting for phase 3 to start")
        self.wait_phase_3_start()
        print("Phase 3 started")
        message = self.platform_communication.get_handshake_message("PHASE_3", "message_5")
        print("Sending message: " + message)
        response = self.platform_communication.send_message(message, inizialization = True)
        if response is None:
            raise Exception("Error: Communication with platform failed.")
        if response['text'] == self.platform_communication.get_handshake_message("PHASE_3", "message_7"):
            self.PDDL_domain_text = str(response['domain'])
            self.PDDL_problem_text = str(response['problem'])
            print("Handshake -- phase 3 successful.")
        else:
            raise Exception("Error: Received unexpected message: " + response['text'])
        #Handshake -- Phase 4
        print("Handshake -- Phase 4")
        message = self.platform_communication.get_handshake_message("PHASE_4", "message_8")
        response = self.platform_communication.send_message(message, inizialization = True)
        if response is None:
            raise Exception("Error: Communication with platform failed.")
        if response['text'] == self.platform_communication.get_handshake_message("PHASE_4", "message_10"):
            self.platform_communication.receive_message_link = response['get_message_url']
            self.platform_communication.send_message_link = response['add_message_url']
            print("Handshake -- phase 4 successful.")
        else:
            raise Exception("Error: Received unexpected message: " + response['text'])
    
    def wait_platform_online(self):
        """
        This method is used to wait until the platform is online.
        """
        while not self.platform_communication.is_platform_online():
            time.sleep(1)
    
    def wait_phase_3_start(self):
        """
        This method is used to wait until the platform starts the phase 3.
        """
        while self.platform_communication.get_handshake_phase() != "PHASE_3":
            time.sleep(0.1)

    def main_loop(self):
        while True:
            time.sleep(1)

if __name__ == '__main__':
    print("Starting Experience Manager...")
    experience_manager = ExperienceManager()
    experience_manager.start_platform_communication()
    experience_manager.main_loop()