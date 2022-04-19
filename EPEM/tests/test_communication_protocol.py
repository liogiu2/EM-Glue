import unittest
from fastapi.testclient import TestClient
from API_communication import *
import EPEM_manager
from unittest.mock import patch, PropertyMock
from sql_app import crud
from sql_app.database import SessionLocal
import os
import threading
import time

class TestCommunicationProtocol(unittest.TestCase):

    def setUp(self):
        try:
            os.remove("db/sql_app.db")
        except FileNotFoundError:
            pass
    
    def tearDown(self):
        try:
            os.remove("db/sql_app.db")
        except FileNotFoundError:
            pass
    
    @patch("communication_protocol_phases._wait_and_return_message_for")
    @patch("API_communication.crud.get_shared_data_with_name")
    def test_phase_1_API(self, mock_protocol_phase, mock_wait_and_return_message_for):
        mock_wait_and_return_message_for.return_value = {"text": communication_phase_messages["PHASE_1"]["message_2"]}
        mock_protocol_phase.return_value.value = "PHASE_1"
        with TestClient(app) as client:
            response = client.get("/inizialization_em", params={"text" : "Experience Manager"})
            with SessionLocal() as db:
                em = crud.get_user_with_role(db, "EM")
                self.assertEqual(em.role, "EM")
                message = crud.get_first_message_not_sent_for_platform(db)
                self.assertEqual(message.text, communication_phase_messages["PHASE_1"]["message_1"])
        self.assertTrue(mock_wait_and_return_message_for.called)
        self.assertEqual(mock_wait_and_return_message_for.call_args[0][0], "EM")
        self.assertEqual(response.json(), {"text": communication_phase_messages["PHASE_1"]["message_2"]})

    @patch("communication_protocol_phases._wait_and_return_message_for")
    @patch("EPEM_manager.start_environment")
    @patch.object(EPEM_manager.EPEM_Manager, "_is_platform_online")
    def test_phase_1_Platform(self, mock_is_platform_online, mock_start_environment, mock_wait_and_return_message_for):
        mock_is_platform_online.return_value = True
        mock_wait_and_return_message_for.return_value = {"text": ""}
        with TestClient(app) as client:
            epem = EPEM_manager.EPEM_Manager(testing=True)
            t = threading.Thread(target = epem.main_loop)
            t.start()
            time.sleep(1)
            with SessionLocal() as db:
                self.assertEqual(crud.get_shared_data_with_name(db, "protocol_phase").value, "PHASE_1")
            response = client.get("/inizialization_em", params={"text" : "Experience Manager"})
            time.sleep(1)
            with SessionLocal() as db:
                phase = crud.get_shared_data_with_name(db, "protocol_phase")
                self.assertEqual(phase.value, "PHASE_2")
                message = crud.get_first_message_not_sent_for_EM(db)
                em_id = int(crud.get_user_with_role(db, "EM").id_user)
                self.assertEqual(message.to_user, em_id)
                plt_id = int(crud.get_user_with_role(db, "PLATFORM").id_user)
                self.assertEqual(message.from_user, plt_id)
                self.assertEqual(message.text, communication_phase_messages["PHASE_1"]["message_2"])
            self.assertTrue(mock_start_environment.called)
            mock_is_platform_online.return_value = False
            t.join()
    
    @patch("communication_protocol_phases._wait_and_return_message_for")
    @patch("API_communication.crud.get_shared_data_with_name")
    def test_phase_2_API(self, mock_protocol_phase, mock_wait_and_return_message_for):
        mock_wait_and_return_message_for.return_value = {"text": communication_phase_messages["PHASE_2"]["message_4"]}
        mock_protocol_phase.return_value.value = "PHASE_1"
        with TestClient(app) as client:
            response = client.get("/inizialization_env", params={"text" : "Environment"})
            self.assertEqual(response.status_code, 404)
            mock_protocol_phase.return_value.value = "PHASE_2"
            response = client.get("/inizialization_env", params={"text" : "Environment"})
            self.assertEqual(response.status_code, 200)
            with SessionLocal() as db:
                em = crud.get_user_with_role(db, "ENV")
                self.assertEqual(em.role, "ENV")
                message = crud.get_first_message_not_sent_for_platform(db)
                self.assertEqual(message.text, communication_phase_messages["PHASE_2"]["message_3"])
                self.assertEqual(message.from_user, int(em.id_user))
        self.assertTrue(mock_wait_and_return_message_for.called)
        self.assertEqual(mock_wait_and_return_message_for.call_args[0][0], "ENV")
        self.assertEqual(response.json(), {"text": communication_phase_messages["PHASE_2"]["message_4"]})
    
    @patch("communication_protocol_phases._wait_and_return_message_for")
    @patch.object(EPEM_manager.EPEM_Manager, "_plt_id")
    @patch.object(EPEM_manager.EPEM_Manager, "_is_platform_online")
    def test_phase_2_Platform(self, mock_is_platform_online, mock_plt_id, mock_wait_and_return_message_for):
        mock_is_platform_online.return_value = True
        mock_plt_id.return_value = 1
        mock_wait_and_return_message_for.return_value = {"text": ""}
        with TestClient(app) as client:
            epem = EPEM_manager.EPEM_Manager(testing=True)
            t = threading.Thread(target = epem.main_loop)
            t.start()
            time.sleep(1)
            with SessionLocal() as db:
                crud.update_value_of_shared_data_with_name(db=db, name="protocol_phase", value="PHASE_2")
            response = client.get("/inizialization_env", params={"text" : "Environment"})
            time.sleep(1)
            with SessionLocal() as db:
                phase = crud.get_shared_data_with_name(db, "protocol_phase")
                self.assertEqual(phase.value, "PHASE_3")
                message = crud.get_first_message_not_sent_for_ENV(db)
                plt_id = int(crud.get_user_with_role(db, "PLATFORM").id_user)
                self.assertEqual(message.from_user, plt_id)
                self.assertEqual(message.text, communication_phase_messages["PHASE_2"]["message_4"])
            mock_is_platform_online.return_value = False
            t.join()
    
    @patch("communication_protocol_phases._wait_and_return_message_for")
    @patch("API_communication.crud.get_shared_data_with_name")
    def test_phase_3_API(self, mock_protocol_phase, mock_wait_and_return_message_for):
        mock_wait_and_return_message_for.return_value = {"text": communication_phase_messages["PHASE_3"]["message_7"]}
        mock_protocol_phase.return_value.value = "PHASE_3"
        with TestClient(app) as client:
            response = client.get("/inizialization_em", params={"text" : communication_phase_messages["PHASE_3"]["message_5"]})
            self.assertEqual(response.status_code, 200)
            with SessionLocal() as db:
                em = crud.get_user_with_role(db, "EM")
                message = crud.get_first_message_not_sent_for_platform(db)
                self.assertEqual(message.text, communication_phase_messages["PHASE_3"]["message_5"])
                self.assertEqual(message.from_user, int(em.id_user))
        self.assertTrue(mock_wait_and_return_message_for.called)
        self.assertEqual(mock_wait_and_return_message_for.call_args[0][0], "EM")
        self.assertEqual(response.json(), {"text": communication_phase_messages["PHASE_3"]["message_7"]})


if __name__ == '__main__':
    unittest.main()
