from singleton_decorator import singleton
import requests
import json
import time
import threading
import queue
import debugpy


@singleton
class PlatformCommunication:
    """
    This class is used to send and receive messages to the platform.
    """    
    communication_protocol_phase_messages = None

    def __init__(self):
        self.base_link  = "http://127.0.0.1:8080/"
        self.__message_queue = queue.Queue()
        self.__input_thread = threading.Thread(target=self.__receive_message_thread, args=(self.__message_queue), daemon=True)
        self.communication_protocol_phase_messages = requests.get(self.base_link + "get_protocol_messages").json()
        self.initial_message_link = "inizialization_em"
        self.protocol_phase_link = "protocol_phase"
        self.receive_message_link = ""
        self.send_message_link = ""
    
    def get_handshake_message(self, phase : str, message: str) -> str:
        """
        This method is used to get the handshake messages for the communication protocol.

        Parameters
        ----------
        phase : str
            The phase of the communication protocol.
        message : str
            The message to be sent.

        Returns
        -------
        str
            The handshake message.
        """
        if phase in self.communication_protocol_phase_messages:
            if message in self.communication_protocol_phase_messages[phase]:
                return self.communication_protocol_phase_messages[phase][message]
        return ""
    
    def get_handshake_phase(self) -> str:
        """
        This method is used to get the handshake phase of the communication protocol.

        Returns
        -------
        str
            The handshake phase.
        """
        if self._is_platform_online():
            response = requests.get(self.base_link + self.protocol_phase_link)
            return response.text
        return ""

    def __receive_message_thread(self, message_queue: queue.Queue):
        """
        This method is used to create a thread that continuosly makes request to the platform to receive a new message when available.
        """
        while self._is_platform_online():
            message = self._receive_message()
            if message != "":
                message_queue.put(message)
            time.sleep(0.2)

    def send_message(self, message, inizialization = False):
        """
        This method is used to send a message to the platform.

        Parameters 
        ----------
        message : str
            The message to be sent.
        """
        if self._is_platform_online():
            if inizialization:
                if type(message) == str:
                    data = {'text': message}
                    response = requests.post(self.base_link + self.initial_message_link, json = data)
                elif type(message) == dict:
                    response = requests.post(self.base_link + self.initial_message_link, json = message)
                else:
                    return None
            else:
                response = requests.post(self.base_link + self.send_message_link, json = json.dumps({'text':message}))

            if response.status_code == 200:
                return response.json()
            else:
                return None
    
    def get_received_message(self):
        """
        This method is used to get the received message from the platform.

        Returns
        -------
        str
            The received message. "" if no message is available.
        """
        try:
            return self.__message_queue.get_nowait()
        except queue.Empty:
            return ""

    def _receive_message(self) -> str:
        """
        This method is used to receive a message from the platform.

        Returns
        -------
        str
            The message received from the platform.
        """
        if self._is_platform_online():
            response = requests.get(self.base_link + self.receive_message_link)
            return response.json()['text']
        return ""
    
    def send_error_message(self, message):
        """
        This method is used to send an error message to the platform.

        Parameters
        ----------
        message : str
            The error message to be sent.
        """
        if self._is_platform_online():
            response = requests.post(self.base_link + "add_error_message", data = json.dumps({'text':message, "error_type": ""}))
            pass

    def _is_platform_online(self):
        """
        This method is used to check if the platform is online.
        """
        try:
            response = requests.head(self.base_link, timeout=0.5)
            if response.status_code == 200:
                return True
            else:
                return False
        except:
            return False

