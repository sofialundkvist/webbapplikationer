from modules.db_connector import *
from modules.validator import Validator
from modules.connection import Connection
from itsdangerous import URLSafeTimedSerializer
from os import urandom
import hashlib
import random, string
import datetime

class User(Base):

    __tablename__ = 'program_user'
    __table_args__={'extend_existing':True}

    id = Column(Integer, primary_key=True)
    email = Column(String)
    password = Column(Text)
    reset_url = Column(Text)
    auth_level = Column(Integer)
    authenticated = Column(Boolean, default=False)
    session_token = Column(Text)
    url_time = Column(DateTime)

    __mapper_args__ = {
        'polymorphic_identity':'user',

    }

    def __init__(self, email, password, auth_level):
        self.email = email
        self.password = self.hash_password(password)
        self.reset_url = None
        self.url_time = None
        self.auth_level = auth_level
        self.authenticated = False

    def set_password(self, session, password):
        new_password = self.hash_password(password)
        session.query(User).filter_by(id = self.id).update({'password':new_password})
        session.commit()

    def deactivte_url(self, session):
        session.query(User).filter_by(id = self.id).update({'reset_url':None, 'url_time':None})
        session.commit()

    def forgotten_password(self, session):
        url_wildcard = str(''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(64)))
        timestamp = datetime.datetime.now()
        session.query(User).filter_by(id = self.id).update({'reset_url':url_wildcard, 'url_time':timestamp})
        session.commit()
        link = "https://massa.avmediaskane.se/glomt_losenord/" + url_wildcard # Ändra till absolut sökväg på servern
        message = {"link": link}

    def get_auth_level(self):
        return self.auth_level

    def get_email(self):
        return self.email

    def get_password(self):
        return self.password

    def validate_url_time(self):
        if self.url_time > datetime.datetime.now()-datetime.timedelta(minutes=60):
            return True
        else:
            return False

    def generate_key(self, session):
        key = str(''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(16)))
        self.set_key(session, key)
        return key

    def set_key(self, session, key):
        self.session_token = key
        session.query(User).filter_by(id = self.id).update({'session_token':key})
        session.commit()

    def log_out(self, session):
        self.authenticated = False
        self.session_token = "none"
        session.query(User).filter_by(id = self.id).update({'authenticated':self.authenticated})
        session.query(User).filter_by(id = self.id).update({'session_token':self.session_token})
        session.commit()

    def is_authenticated(self, token):
        if token == self.session_token:
             return True
        else:
            return False

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        ''' Returns session token '''
        return self.session_token

    def send_new_email(self):
        pwd = 'Massa2017'
        if self.password != self.hash_password(pwd):
            pwd = 'Du har satt ett eget lösenord.'

    @classmethod
    def is_attending(cls, session, email):
        exists = session.query(User).filter_by(email=email).first()
        if exists:
            return False
        else:
            return True

    @classmethod
    def get_user_by_url(cls, session, url):
        user = session.query(User).filter_by(reset_url=url).first()
        if user:
            return user

    @classmethod
    def log_in(cls, session, email, user_psw):
        user = cls.get_user(session, email)
        if user is not None:
            if user_psw == user.password:
                user.authenticated = True
                user.session_token = urandom(8)
                user.session_token = str(user.session_token)
                session.query(User).filter_by(id = user.id).update({'authenticated':user.authenticated})
                session.query(User).filter_by(id = user.id).update({'session_token':user.session_token})
                session.commit()
                return user
        return None

    @classmethod
    def hash_password(cls, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    @classmethod
    def get_user(cls, session, email):
        ''' Get user by email '''
        user = session.query(User).filter_by(email=email).first()
        return user

    @staticmethod
    def get_user_by_id(session, user_id):
        ''' Get user by id '''
        user = session.query(User).filter_by(id=user_id).first()
        if user is not None:
            return user
        else:
            return None
