import datetime

from src import app
import src.db as db
from unittest.mock import ANY
import src.models as models
from flask_testing import TestCase
import copy

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


class BaseTestCase(TestCase):
    def setUp(self):
        super().setUp()

        models.Base.metadata.drop_all(db.engine)
        models.Base.metadata.create_all(db.engine)

        self.user_1_data = {
            "username": "unittestuser1",
            "password": "unittestuserpassword1",
            "email": "unittestusermail1@mail.com"
        }

        self.user_1_data_hashed = {
            "username": self.user_1_data["username"],
            "password": bcrypt.generate_password_hash(self.user_1_data["password"]).decode('utf-8'),
            "email": self.user_1_data["email"]
        }

        self.user_2_data = {
            "username": "unittestuser2",
            "password": "unittestuserpassword2",
            "email": "unittestusermail2@mail.com"
        }

        self.user_2_data_hashed = {
            "username": self.user_2_data["username"],
            "password": bcrypt.generate_password_hash(self.user_2_data["password"]).decode('utf-8'),
            "email": self.user_2_data["email"]
        }

        user1 = models.User(username=self.user_1_data_hashed['username'], password=self.user_1_data_hashed['password'],
                            email=self.user_1_data_hashed['email'])
        user2 = models.User(username=self.user_2_data_hashed['username'], password=self.user_2_data_hashed['password'],
                            email=self.user_2_data_hashed['email'])
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        self.user2_id = user2.id

        self.user_1_wallet = {
            "balance": 5000,
            "user_id": user1.id
        }

        self.user_2_wallet = {
            "balance": 6000,
            "user_id": user2.id
        }

        wallet1 = models.Wallet(balance=self.user_1_wallet['balance'],
                                user_id=self.user_1_wallet['user_id'])
        wallet2 = models.Wallet(balance=self.user_2_wallet['balance'],
                                user_id=self.user_2_wallet['user_id'])
        db.session.add(wallet1)
        db.session.add(wallet2)
        db.session.commit()

        self.wallet1_id = wallet1.id
        self.wallet2_id = wallet2.id

        self.trans1 = {
            "wallet_id_1": wallet1.id,
            "wallet_id_2": wallet2.id,
            "amount_of_money": 1000
        }

        transaction1 = models.Transaction(wallet_id_1=self.trans1["wallet_id_1"],
                                          wallet_id_2=self.trans1["wallet_id_2"],
                                          amount_of_money=self.trans1["amount_of_money"])

        db.session.add(transaction1)
        db.session.commit()

        self.trans1_id = transaction1.id

    def tearDown(self):
        db.session.rollback()

    def create_app(self):
        return app

    def get_auth_header(self, credentials):
        resp = self.client.post('user/login', json=credentials)
        access_token = resp.json['token']
        return {"Authorization": f'Bearer {access_token}'}


# User test


class Testlogin(BaseTestCase):
    def test_user_login(self):
        resp = self.client.post('user/login', json=self.user_1_data)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {'token': ANY})

        resp = self.client.post('user/login', json={"wrong": "wrong"})

        self.assertEqual(resp.status_code, 400)

        test_user = copy.deepcopy(self.user_1_data)
        test_user["username"] = "notexistingunittestusername"
        resp = self.client.post('user/login', json=test_user)

        self.assertEqual(resp.status_code, 404)

        test_user = copy.deepcopy(self.user_1_data)
        test_user["password"] = "notexistingunittestpassword"
        resp = self.client.post('user/login', json=test_user)

        self.assertEqual(resp.status_code, 400)


class TestGetUser(BaseTestCase):
    def test_get_user(self):
        resp = self.client.get('user/', headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(f'user/{999999}', headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 404)


class TestdeleteUser(BaseTestCase):
    def test_delete_user(self):
        test_token = self.get_auth_header(self.user_1_data)
        resp = self.client.delete('user/', headers=self.get_auth_header(self.user_1_data))

        self.assertEqual(resp.status_code, 200)

        resp = self.client.delete('user/', headers=test_token)

        self.assertEqual(resp.status_code, 404)


class TestLogoutUser(BaseTestCase):
    def test_logout_user(self):
        resp = self.client.post('user/logout', headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 200)


class TestpostUser(BaseTestCase):
    def test_post_user(self):
        resp = self.client.post('user/', json={"wrong": "wrong"})

        self.assertEqual(resp.status_code, 400)

        resp = self.client.post('user/', json=self.user_1_data)

        self.assertEqual(resp.status_code, 400)

        testuser = self.user_1_data
        testuser["username"] = "unittestuser3"
        resp = self.client.post('user/', json=testuser)

        self.assertEqual(resp.status_code, 200)


class TestPutUser(BaseTestCase):
    def test_put_user(self):
        test_token = self.get_auth_header(self.user_2_data)

        resp = self.client.put('user/', json={"wrong": "wrong"}, headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 400)

        test_user = copy.deepcopy(self.user_2_data)
        test_user["password"] = "wrong password"
        resp = self.client.put('user/', json=test_user, headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 400)

        test_user = copy.deepcopy(self.user_2_data)
        test_user["username"] = self.user_1_data["username"]
        resp = self.client.put('user/', json=test_user, headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 400)

        test_user = copy.deepcopy(self.user_2_data)
        test_user["new_password"] = "new_password"
        resp = self.client.put('user/', json=test_user, headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 200)

        self.client.delete('user/', headers=test_token)
        resp = self.client.put('user/', json=self.user_2_data, headers=test_token)

        self.assertEqual(resp.status_code, 404)


# Wallet test


class TestCreateWallet(BaseTestCase):
    def test_create_wallet(self):
        test_token = self.get_auth_header(self.user_2_data)

        resp = self.client.post('wallet/', json={"wrong": "wrong"}, headers=test_token)

        self.assertEqual(resp.status_code, 400)

        resp = self.client.post('wallet/', json={"balance": self.user_2_wallet["balance"]},
                                headers=test_token)

        self.assertEqual(resp.status_code, 200)

        self.client.delete('user/', headers=test_token)
        resp = self.client.post('wallet/', json={"balance": self.user_2_wallet["balance"]},
                                headers=test_token)

        self.assertEqual(resp.status_code, 500)


class TestGetWalletById(BaseTestCase):
    def test_get_wallet_by_id(self):
        resp = self.client.get(f'wallet/{999999}',
                               headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 404)

        resp = self.client.get(f'wallet/{self.wallet1_id}')

        self.assertEqual(resp.status_code, 401)

        resp = self.client.get(f'wallet/{self.wallet1_id}', headers=self.get_auth_header(self.user_1_data))

        self.assertEqual(resp.status_code, 200)


class TestPutWallet(BaseTestCase):
    def test_put_wallet(self):
        resp = self.client.put(f'wallet/{self.wallet2_id}', json={"wrong": "wrong"},
                               headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 400)

        resp = self.client.put(f'wallet/{999999}', json={"new_balance": self.user_2_wallet["balance"]},
                               headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 404)

        resp = self.client.get(f'wallet/{self.wallet2_id}', json={"new_balance": self.user_2_wallet["balance"]})

        self.assertEqual(resp.status_code, 401)

        resp = self.client.put(f'wallet/{self.wallet2_id}', json={"new_balance": self.user_2_wallet["balance"]},
                               headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 200)


class TestDeleteWallet(BaseTestCase):
    def test_delete_playlists(self):
        resp = self.client.delete(f'wallet/{999999}', headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 404)

        resp = self.client.delete(f'wallet/{self.wallet1_id}', headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 403)

        resp = self.client.delete(f'wallet/{self.wallet2_id}', headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 200)


# Transaction test


class TestCreateTransaction(BaseTestCase):
    def test_create_transaction(self):
        test_token = self.get_auth_header(self.user_1_data)

        resp = self.client.post('transaction/', json={"wrong": "wrong"}, headers=test_token)

        self.assertEqual(resp.status_code, 400)

        resp = self.client.post('transaction/', json={"wallet_id_1": 9999,
                                                      "wallet_id_2": self.wallet2_id,
                                                      "amount_of_money": 1000}, headers=test_token)

        self.assertEqual(resp.status_code, 404)

        resp = self.client.post('transaction/', json={"wallet_id_1": self.wallet1_id,
                                                      "wallet_id_2": 9999,
                                                      "amount_of_money": 1000}, headers=test_token)

        self.assertEqual(resp.status_code, 404)

        resp = self.client.post(f'transaction/', json={"wallet_id_1": self.wallet1_id,
                                                       "wallet_id_2": self.wallet2_id,
                                                       "amount_of_money": 1000},
                                headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 403)

        resp = self.client.post(f'transaction/', json={"wallet_id_1": self.wallet1_id,
                                                       "wallet_id_2": self.wallet2_id,
                                                       "amount_of_money": -1000},
                                headers=test_token)

        self.assertEqual(resp.status_code, 404)

        resp = self.client.post(f'transaction/', json={"wallet_id_1": self.wallet1_id,
                                                       "wallet_id_2": self.wallet2_id,
                                                       "amount_of_money": 8000},
                                headers=test_token)

        self.assertEqual(resp.status_code, 404)

        resp = self.client.post(f'transaction/', json={"wallet_id_1": self.wallet1_id,
                                                       "wallet_id_2": self.wallet2_id,
                                                       "amount_of_money": 1000},
                                headers=test_token)

        self.assertEqual(resp.status_code, 200)


class TestGetTransaction(BaseTestCase):
    def test_get_transaction(self):
        test_token = self.get_auth_header(self.user_1_data)

        resp = self.client.get(f'transaction/{9999}', headers=test_token)

        self.assertEqual(resp.status_code, 404)

        resp = self.client.get(f'transaction/{self.wallet1_id}', headers=self.get_auth_header(self.user_2_data))

        self.assertEqual(resp.status_code, 403)

        resp = self.client.get(f'transaction/{self.wallet1_id}', headers=test_token)

        self.assertEqual(resp.status_code, 200)


class TestDeleteTransaction(BaseTestCase):
    def test_delete_transaction(self):
        resp = self.client.delete(f'transaction/{9999}')

        self.assertEqual(resp.status_code, 404)

        resp = self.client.delete(f'transaction/{self.trans1_id}')

        self.assertEqual(resp.status_code, 200)
