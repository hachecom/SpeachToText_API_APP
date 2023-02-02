from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import os
from gcloud import datastore


class User(UserMixin):

    def __init__(self):
        self.username = 0
        self.password = 0
        self.admin = False
        self.id = self.username

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def get_user(self, usern):
        datastore_client = datastore.Client()
        query = datastore_client.query(kind='Users')
        results = list(query.fetch())
        for result in results:
            if usern == result['userName']:
                self.username = usern
                self.password = result['password']
                self.admin = result['admin']
                self.id = self.username
                return self
        return None

    def get_password(self, passw):
        if self.password == passw:
            return True
        else:
            return False
