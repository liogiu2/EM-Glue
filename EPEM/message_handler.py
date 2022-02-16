from queue import Queue, Empty
from utilities import singleton

@singleton
class MessageHandler:
    """
    This class is a singleton class that is used to manage the messages from the environment and the experience managers.

    Attributes
    ----------
    environment_messages_IN : Queue
        The queue used to receive messages from the environment.
    environment_messages_OUT : Queue
        The queue used to send messages to the environment.
    em_messages_IN : Queue
        The queue used to receive messages from the experience managers.
    em_messages_OUT : Queue
        The queue used to send messages to the experience managers.
    error_messages : Queue
        The queue used to store error messages coming fromt the environment.
    """

    def __init__(self):
        self.environment_messages_IN = Queue()
        self.environment_messages_OUT = Queue()
        self.em_messages_IN = Queue()
        self.em_messages_OUT = Queue()
        self.error_messages = Queue()
        for i in range(10):
            self.environment_messages_IN.put("OK")
            self.environment_messages_OUT.put("OK")
            self.em_messages_IN.put("OK")
            self.em_messages_OUT.put("OK")
            self.error_messages.put("OK")

    def add_incoming_environment_message(self, message):
        """
        This method is used to add a message to the environment IN message queue.

        Parameters
        ----------
        message : str
            The message to be added to the queue.
        """
        self.environment_messages_IN.put(message)
    
    def get_incoming_environment_message(self):
        """
        This method is used to get a message from the environment IN message queue. It uses a non blocking get, so if the queue is empty it raises an Empty exception.

        Returns
        -------
        str
            The message from the queue.
        """
        try:
            message = self.environment_messages_IN.get_nowait()
        except Empty:
            message = "None"
        return message
    
    def send_environment_message(self, message):
        """
        This method is used to add a message to the environment OUT queue.

        Parameters
        ----------
        message : str
            The message to be sent.
        """
        self.environment_messages_OUT.put(message)

    def get_outgoing_environment_message(self):
        """
        This method is used to get a message from the environment OUT queue. It uses a non blocking get, so if the queue is empty it raises an Empty exception and it returns a "None".

        Returns
        -------
        str
            The message from the queue.
        """
        try:
            message = self.environment_messages_OUT.get_nowait()
        except Empty:
            message = "None"
        return message
    
    def add_incoming_error_message(self, message):
        """
        This method is used to add a message to the error queue.

        Parameters
        ----------
        message : str
            The message to be added to the queue.
        """
        self.error_messages.put(message)
    
    def get_incoming_error_message(self):
        """
        This method is used to get a message from the error queue. It uses a non blocking get, so if the queue is empty it raises an Empty exception and it returns a "None".

        Returns
        -------
        str
            The message from the queue.
        """
        return self.error_messages.get_nowait()
    
    def add_incoming_em_message(self, message):
        """
        This method is used to add a message to the experience manager IN message queue.

        Parameters
        ----------
        message : str
            The message to be added to the queue.
        """
        self.em_messages_IN.put(message)

    def get_incoming_em_message(self):
        """
        This method is used to get a message from the experience manager IN message queue. It uses a non blocking get, so if the queue is empty it raises an Empty exception and it returns a "None".

        Returns
        -------
        str
            The message from the queue.
        """
        try:
            message = self.em_messages_IN.get_nowait()
        except Empty:
            message = "None"
        return message
    
    def send_em_message(self, message):
        """
        This method is used to add a message to the experience manager OUT queue.

        Parameters
        ----------
        message : str
            The message to be sent.
        """
        self.em_messages_OUT.put(message)
    
    def get_outgoing_em_message(self):
        """
        This method is used to get a message from the experience manager OUT queue. It uses a non blocking get, so if the queue is empty it raises an Empty exception and it returns a "None".

        Returns
        -------
        str
            The message from the queue.
        """
        try:
            message = self.em_messages_OUT.get_nowait()
        except Empty:
            message = "None"
        return message