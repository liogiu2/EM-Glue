import os
import sys

if os.name == 'nt':
    pddl_path = "C:\\Users\\giulio17\\Documents\\Camelot_work\\EV_PDDL"
else:
    pddl_path = "/Users/giuliomori/Documents/GitHub/EV_PDDL/"

sys.path.insert(0, pddl_path)
from platform_communication import PlatformCommunication
import time
import jsonpickle
from ev_pddl.PDDL import PDDL_Parser

class ExperienceManager:

    PDDL_domain_text = ""
    PDDL_problem_text = ""

    def __init__(self) -> None:
        self.platform_communication = PlatformCommunication()
        self._PDDL_parser = PDDL_Parser()
        self.domain = None
        self.problem = None

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
            print("--------------------------------------Domain received--------------------------------------")
            print(self.PDDL_domain_text)
            self.PDDL_problem_text = str(response['problem'])
            print("--------------------------------------Problem received--------------------------------------")
            print(self.PDDL_problem_text)
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
            self.platform_communication.receive_message_link = response['get_message_url'].replace("/", "")
            print("Receive message link received: /" + self.platform_communication.receive_message_link)
            self.platform_communication.send_message_link = response['add_message_url'].replace("/", "")
            print("Send message link received: /" + self.platform_communication.send_message_link)
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
        """
        This is the main loop of the experience manager.
        """
        self.platform_communication.start_receiving_messages()
        
        # import debugpy
        # debugpy.listen(5678)
        # debugpy.wait_for_client()
        # debugpy.breakpoint()

        self.domain = self._PDDL_parser.parse_domain(domain_str = self.PDDL_domain_text)
        print("Domain parsed correcly")
        self.problem = self._PDDL_parser.parse_problem(problem_str = self.PDDL_problem_text)
        print("Problem parsed correcly")

        print("Starting normal communication...")
        while True:
            message = self.platform_communication.get_received_message()
            if message is not None:
                changed_relations = []
                for item in message:
                    rel = jsonpickle.decode(item['text'])
                    changed_relations.append(rel)
                print("Received message: " + str(changed_relations))
            time.sleep(1)

if __name__ == '__main__':
    print("Starting Experience Manager...")
    experience_manager = ExperienceManager()
    experience_manager.start_platform_communication()
    experience_manager.main_loop()