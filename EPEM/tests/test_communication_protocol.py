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
        self.communication_phase_messages = read_json_file("messages.json")
        self.communication_urls = read_json_file("parameters.json")['url']
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
        mock_wait_and_return_message_for.return_value = {"text": self.communication_phase_messages["PHASE_1"]["message_2"]}
        mock_protocol_phase.return_value.value = "PHASE_1"
        with TestClient(app) as client:
            response = client.get("/inizialization_em", params={"text" : self.communication_phase_messages["PHASE_1"]["message_1"] + "Experience Manager"})
            with SessionLocal() as db:
                em = crud.get_user_with_role(db, "EM")
                self.assertEqual(em.role, "EM")
                self.assertEqual(em.name, "Experience Manager")
                message = crud.get_first_message_not_sent_for_platform(db)
                self.assertEqual(message.text, self.communication_phase_messages["PHASE_1"]["message_1"] + "Experience Manager")
        self.assertTrue(mock_wait_and_return_message_for.called)
        self.assertEqual(mock_wait_and_return_message_for.call_args[0][0], "EM")
        self.assertEqual(response.json()['text'], self.communication_phase_messages["PHASE_1"]["message_2"])

    @patch("communication_protocol_phases._wait_and_return_message_for")
    @patch("EPEM_manager.start_environment")
    @patch.object(EPEM_manager.EPEM_Manager, "_is_platform_online")
    def test_phase_1_Platform(self, mock_is_platform_online, mock_start_environment, mock_wait_and_return_message_for):
        mock_is_platform_online.return_value = True
        mock_wait_and_return_message_for.return_value = {"text": ""}
        with TestClient(app) as client:
            epem = EPEM_manager.EPEM_Manager()
            t = threading.Thread(target = epem.main_loop)
            t.start()
            time.sleep(1)
            with SessionLocal() as db:
                self.assertEqual(crud.get_shared_data_with_name(db, "protocol_phase").value, "PHASE_1")
            response = client.get("/inizialization_em", params={"text" : self.communication_phase_messages["PHASE_1"]["message_1"] + "Experience Manager"})
            time.sleep(1)
            with SessionLocal() as db:
                phase = crud.get_shared_data_with_name(db, "protocol_phase")
                self.assertEqual(phase.value, "PHASE_2")
                message = crud.get_first_message_not_sent_for_EM(db)
                em_id = int(crud.get_user_with_role(db, "EM").id_user)
                self.assertEqual(message.to_user, em_id)
                plt_id = int(crud.get_user_with_role(db, "PLATFORM").id_user)
                self.assertEqual(message.from_user, plt_id)
                self.assertEqual(message.text, self.communication_phase_messages["PHASE_1"]["message_2"])
            self.assertTrue(mock_start_environment.called)
            mock_is_platform_online.return_value = False
            t.join()
    
    @patch("communication_protocol_phases._wait_and_return_message_for")
    @patch("API_communication.crud.get_shared_data_with_name")
    def test_phase_2_API(self, mock_protocol_phase, mock_wait_and_return_message_for):
        mock_wait_and_return_message_for.return_value = {"text": self.communication_phase_messages["PHASE_2"]["message_4"]}
        mock_protocol_phase.return_value.value = "PHASE_1"
        with TestClient(app) as client:
            response = client.post("/inizialization_env", json={"text" : "Environment"})
            self.assertEqual(response.status_code, 404)
            mock_protocol_phase.return_value.value = "PHASE_2"
            response = client.post("/inizialization_env", json={"text" : self.communication_phase_messages["PHASE_2"]["message_3"] + "Environment"})
            self.assertEqual(response.status_code, 200)
            with SessionLocal() as db:
                em = crud.get_user_with_role(db, "ENV")
                self.assertEqual(em.role, "ENV")
                self.assertEqual(em.name, "Environment")
                message = crud.get_first_message_not_sent_for_platform(db)
                self.assertEqual(message.text, self.communication_phase_messages["PHASE_2"]["message_3"] + "Environment")
                self.assertEqual(message.from_user, int(em.id_user))
        self.assertTrue(mock_wait_and_return_message_for.called)
        self.assertEqual(mock_wait_and_return_message_for.call_args[0][0], "ENV")
        self.assertEqual(response.json()['text'], self.communication_phase_messages["PHASE_2"]["message_4"])
    
    @patch("communication_protocol_phases._wait_and_return_message_for")
    @patch.object(EPEM_manager.EPEM_Manager, "_plt_id")
    @patch.object(EPEM_manager.EPEM_Manager, "_is_platform_online")
    def test_phase_2_Platform(self, mock_is_platform_online, mock_plt_id, mock_wait_and_return_message_for):
        mock_is_platform_online.return_value = True
        mock_plt_id.return_value = 1
        mock_wait_and_return_message_for.return_value = {"text": ""}
        with TestClient(app) as client:
            epem = EPEM_manager.EPEM_Manager()
            t = threading.Thread(target = epem.main_loop)
            t.start()
            time.sleep(1)
            with SessionLocal() as db:
                crud.update_value_of_shared_data_with_name(db=db, name="protocol_phase", value="PHASE_2")
            response = client.post("/inizialization_env", json={"text" : self.communication_phase_messages["PHASE_2"]["message_3"] + "Environment"})
            time.sleep(1)
            with SessionLocal() as db:
                phase = crud.get_shared_data_with_name(db, "protocol_phase")
                self.assertEqual(phase.value, "PHASE_3")
                message = crud.get_first_message_not_sent_for_ENV(db)
                plt_id = int(crud.get_user_with_role(db, "PLATFORM").id_user)
                self.assertEqual(message.from_user, plt_id)
                self.assertEqual(message.text, self.communication_phase_messages["PHASE_2"]["message_4"])
            mock_is_platform_online.return_value = False
            t.join()
    
    @patch("communication_protocol_phases._wait_and_return_message_for")
    @patch("API_communication.crud.get_shared_data_with_name")
    def test_phase_3_API_EM(self, mock_protocol_phase, mock_wait_and_return_message_for):
        mock_wait_and_return_message_for.return_value = {
            "text": self.communication_phase_messages["PHASE_3"]["message_7"] + "###" + "this is a domain" + "###" + "this is a problem"
        }
        mock_protocol_phase.return_value.value = "PHASE_3"
        with TestClient(app) as client:
            with SessionLocal() as db:
                crud.create_user(db=db, item=schemas.UserCreate(name="EM", role="EM"))
                crud.create_user(db=db, item=schemas.UserCreate(name="ENV", role="ENV"))
            response = client.get("/inizialization_em", params={"text" : "wrong"})
            self.assertEqual(response.status_code, 400)
            response = client.get("/inizialization_em", params={"text" : self.communication_phase_messages["PHASE_3"]["message_5"]})
            self.assertEqual(response.status_code, 200)
            with SessionLocal() as db:
                em = crud.get_user_with_role(db, "EM")
                message = crud.get_first_message_not_sent_for_platform(db)
                self.assertEqual(message.text, self.communication_phase_messages["PHASE_3"]["message_5"])
                self.assertEqual(message.from_user, int(em.id_user))
        self.assertTrue(mock_wait_and_return_message_for.called)
        self.assertEqual(mock_wait_and_return_message_for.call_args[0][0], "EM")
        self.assertEqual(response.json(), {"text": self.communication_phase_messages["PHASE_3"]["message_7"], "domain": "this is a domain", "problem": "this is a problem", "add_message_url": None, "get_message_url" : None })

    @patch("communication_protocol_phases._wait_and_return_message_for")
    @patch("API_communication.crud.get_shared_data_with_name")
    def test_phase_3_4_API_ENV(self, mock_protocol_phase, mock_wait_and_return_message_for):
        mock_wait_and_return_message_for.return_value = {"text": "example ###add_message_url###get_message_url"}
        mock_protocol_phase.return_value.value = "PHASE_3"
        with TestClient(app) as client:
            with SessionLocal() as db:
                crud.create_user(db=db, item=schemas.UserCreate(name="EM", role="EM"))
                crud.create_user(db=db, item=schemas.UserCreate(name="ENV", role="ENV"))
            response = client.post("/inizialization_env", json={"text" : "wrong"})
            self.assertEqual(response.status_code, 400)
            response = client.post("/inizialization_env", json={"text" : self.communication_phase_messages["PHASE_3"]["message_6"], "domain": "this is a domain", "problem": "this is a problem"})
            self.assertEqual(response.status_code, 200)
            with SessionLocal() as db:
                env = crud.get_user_with_role(db, "ENV")
                message = crud.get_first_message_not_sent_for_platform(db)
                self.assertEqual(message.text.startswith(self.communication_phase_messages["PHASE_3"]["message_6"]), True)
                self.assertEqual(message.from_user, int(env.id_user))
                self.assertEqual(message.text, self.communication_phase_messages["PHASE_3"]["message_6"] + "###" + "this is a domain" + "###" + "this is a problem")
        self.assertTrue(mock_wait_and_return_message_for.called)
        self.assertEqual(mock_wait_and_return_message_for.call_args[0][0], "ENV")
    
    @patch.object(EPEM_manager.EPEM_Manager, "_env_id", 3)
    @patch.object(EPEM_manager.EPEM_Manager, "_em_id", 2)
    @patch.object(EPEM_manager.EPEM_Manager, "_plt_id", 1)
    @patch("communication_protocol_phases._wait_and_return_message_for")
    @patch.object(EPEM_manager.EPEM_Manager, "_is_platform_online")
    def test_phase_3_Platform(self, mock_is_platform_online, mock_wait_and_return_message_for):
        mock_is_platform_online.return_value = True
        mock_wait_and_return_message_for.return_value = {"text" : self.communication_phase_messages["PHASE_3"]["message_6"] + "###" + "this is a domain" + "###" + "this is a problem"}
        with TestClient(app) as client:
            epem = EPEM_manager.EPEM_Manager()
            t = threading.Thread(target = epem.main_loop)
            t.start()
            time.sleep(1)
            with SessionLocal() as db:
                crud.update_value_of_shared_data_with_name(db=db, name="protocol_phase", value="PHASE_3")
                crud.create_user(db=db, item=schemas.UserCreate(name="EM", role="EM"))
                crud.create_user(db=db, item=schemas.UserCreate(name="ENV", role="ENV"))
            response = client.get("/inizialization_em", params={"text" : self.communication_phase_messages["PHASE_3"]["message_5"]})
            time.sleep(1)
            with SessionLocal() as db:
                phase = crud.get_shared_data_with_name(db, "protocol_phase")
                self.assertEqual(phase.value, "PHASE_3")
                message = crud.get_first_message_not_sent_for_EM(db)
                self.assertIsNone(message)
            self.assertTrue(epem.phase3_part1_received)
            self.assertFalse(epem.phase3_part2_received)
            response = client.post("/inizialization_env", json={"text" : self.communication_phase_messages["PHASE_3"]["message_6"], "domain": "this is a domain", "problem": "this is a problem"})
            time.sleep(1)
            self.assertTrue(epem.phase3_part2_received)
            with SessionLocal() as db:
                phase = crud.get_shared_data_with_name(db, "protocol_phase")
                self.assertEqual(phase.value, "PHASE_4")
                message = crud.get_first_message_not_sent_for_EM(db)
                self.assertIsNotNone(message)
            mock_is_platform_online.return_value = False
            t.join()

    @patch("communication_protocol_phases._wait_and_return_message_for")
    @patch("API_communication.crud.get_shared_data_with_name")
    def test_phase_4_API_EM(self, mock_protocol_phase, mock_wait_and_return_message_for):
        mock_wait_and_return_message_for.return_value = {"text": self.communication_phase_messages["PHASE_4"]["message_10"] + "###" + self.communication_urls["in_em"] + "###" + self.communication_urls["out_em"]}
        mock_protocol_phase.return_value.value = "PHASE_4"
        with TestClient(app) as client:
            with SessionLocal() as db:
                crud.create_user(db=db, item=schemas.UserCreate(name="EM", role="EM"))
                crud.create_user(db=db, item=schemas.UserCreate(name="ENV", role="ENV"))
            response = client.get("/inizialization_em", params={"text" : "wrong"})
            self.assertEqual(response.status_code, 400)
            response = client.get("/inizialization_em", params={"text" : self.communication_phase_messages["PHASE_4"]["message_8"]})
            self.assertEqual(response.status_code, 200)
            with SessionLocal() as db:
                em = crud.get_user_with_role(db, "EM")
                message = crud.get_first_message_not_sent_for_platform(db)
                self.assertEqual(message.text, self.communication_phase_messages["PHASE_4"]["message_8"])
                self.assertEqual(message.from_user, int(em.id_user))
        self.assertTrue(mock_wait_and_return_message_for.called)
        self.assertEqual(mock_wait_and_return_message_for.call_args[0][0], "EM")
        self.assertEqual(response.json()['text'], self.communication_phase_messages["PHASE_4"]["message_10"])
        self.assertIsNotNone(response.json()['add_message_url'])
        self.assertIsNotNone(response.json()['get_message_url'])

    @patch.object(EPEM_manager.EPEM_Manager, "_env_id", 3)
    @patch.object(EPEM_manager.EPEM_Manager, "_em_id", 2)
    @patch.object(EPEM_manager.EPEM_Manager, "_plt_id", 1)
    @patch("communication_protocol_phases._wait_and_return_message_for")
    @patch.object(EPEM_manager.EPEM_Manager, "_is_platform_online")
    def test_phase_4_Platform(self, mock_is_platform_online, mock_wait_and_return_message_for):
        mock_is_platform_online.return_value = True
        mock_wait_and_return_message_for.return_value = {"text": "let's try###url###url"}
        with TestClient(app) as client:
            epem = EPEM_manager.EPEM_Manager()
            t = threading.Thread(target = epem.main_loop)
            t.start()
            time.sleep(1)
            with SessionLocal() as db:
                crud.update_value_of_shared_data_with_name(db=db, name="protocol_phase", value="PHASE_4")
                crud.create_user(db=db, item=schemas.UserCreate(name="EM", role="EM"))
                crud.create_user(db=db, item=schemas.UserCreate(name="ENV", role="ENV"))
            response = client.get("/inizialization_em", params={"text" : self.communication_phase_messages["PHASE_4"]["message_8"]})
            time.sleep(1)
            with SessionLocal() as db:
                phase = crud.get_shared_data_with_name(db, "protocol_phase")
                self.assertEqual(phase.value, "DONE")
                message = crud.get_first_message_not_sent_for_EM(db)
                self.assertEqual(message.text, self.communication_phase_messages["PHASE_4"]["message_10"] + "###" + self.communication_urls["in_em"] + "###" + self.communication_urls["out_em"])
                message = crud.get_first_message_not_sent_for_ENV(db)
                self.assertEqual(message.text, self.communication_phase_messages["PHASE_4"]["message_9"] + "###" + self.communication_urls["in_env"] + "###" + self.communication_urls["out_env"])
            mock_is_platform_online.return_value = False
            t.join()

    @patch("API_communication.crud.get_shared_data_with_name")
    @patch("communication_protocol_phases._wait_and_return_message_for")
    def test_normal_communication(self, mock_wait_and_return_message_for, mock_protocol_phase):
        mock_wait_and_return_message_for.return_value = {"text": ""}
        mock_protocol_phase.return_value.value = "PHASE_X"
        param = {
            "text" : "text",
            "to_user_role" : "ENV"
        }
        err = {
            "text" : "text",
            "error_type" : "err"
        }
        with TestClient(app) as client:
            with SessionLocal() as db:
                crud.create_user(db=db, item=schemas.UserCreate(name="EM", role="EM"))
                crud.create_user(db=db, item=schemas.UserCreate(name="ENV", role="ENV"))

            response = client.post(self.communication_urls["in_em"], json=param)
            self.assertEqual(response.status_code, 404)
            param["to_user_role"] = "EM"
            response = client.post(self.communication_urls["in_env"], json=param)
            self.assertEqual(response.status_code, 404)
            response = client.post(self.communication_urls["err_in"], json=err)
            self.assertEqual(response.status_code, 404)
            response = client.get(self.communication_urls["out_env"])
            self.assertEqual(response.status_code, 404)
            response = client.get(self.communication_urls["out_em"])
            self.assertEqual(response.status_code, 404)
            response = client.get(self.communication_urls["err_out"])
            self.assertEqual(response.status_code, 404)

            mock_protocol_phase.return_value.value = "DONE"
            param["to_user_role"] = "ENV"
            response = client.post(self.communication_urls["in_em"], json=param)
            self.assertEqual(response.status_code, 200)
            param["to_user_role"] = "EM"
            response = client.post(self.communication_urls["in_env"], json=param)
            self.assertEqual(response.status_code, 200)
            response = client.post(self.communication_urls["err_in"], json=err)
            self.assertEqual(response.status_code, 200)

            response = client.get(self.communication_urls["out_env"])
            self.assertEqual(response.status_code, 200)
            self.assertNotEqual(response.json(), [])
            response = client.get(self.communication_urls["out_em"])
            self.assertEqual(response.status_code, 200)
            self.assertNotEqual(response.json(), [])
            response = client.get(self.communication_urls["err_out"])
            self.assertEqual(response.status_code, 200)
            self.assertNotEqual(response.json(), [])

            

if __name__ == '__main__':
    unittest.main()
