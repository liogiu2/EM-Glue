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
        #Handshake -- Phase 1
        message = self.platform_communication.get_handshake_message("PHASE_1", "message_1") + " Experience Manager"
        response = self.platform_communication.send_message(message, inizialization = True)
        if response is None:
            raise Exception("Error: Communication with platform failed.")
        if response['text'] == self.platform_communication.get_handshake_message("PHASE_1", "message_2"):
            print("Handshake -- phase 1 successful.")
        #Handshake -- Phase 3
        while self.platform_communication.get_handshake_phase() != "PHASE_3":
            time.sleep(1)
        message = self.platform_communication.get_handshake_message("PHASE_3", "message_5")
        response = self.platform_communication.send_message(message, inizialization = True)
        if response is None:
            raise Exception("Error: Communication with platform failed.")
        if response['text'] == self.platform_communication.get_handshake_message("PHASE_3", "message_7"):
            self.PDDL_domain_text = str(response['domain'])
            self.PDDL_problem_text = str(response['problem'])
            print("Handshake -- phase 3 successful.")
        #Handshake -- Phase 4
        message = self.platform_communication.get_handshake_message("PHASE_4", "message_8")
        response = self.platform_communication.send_message(message, inizialization = True)
        if response is None:
            raise Exception("Error: Communication with platform failed.")
        if response['text'] == self.platform_communication.get_handshake_message("PHASE_4", "message_10"):
            self.platform_communication.receive_message_link = response['get_message_url']
            self.platform_communication.send_message_link = response['add_message_url']
            print("Handshake -- phase 4 successful.")

    def main_loop(self):
        while True:
            time.sleep(1)

if __name__ == '__main__':
    experience_manager = ExperienceManager()
    experience_manager.start_platform_communication()
    experience_manager.main_loop()