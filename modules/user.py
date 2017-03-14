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

    def set_password(self, password):
        new_password = self.hash_password(password)
        global session
        session = Session()
        session.query(User).filter_by(id = self.id).update({'password':new_password})
        session.commit()
        session.close()

    def deactivte_url(self):
        global session
        session = Session()
        session.query(User).filter_by(id = self.id).update({'reset_url':None, 'url_time':None})
        session.commit()
        session.close()

    def forgotten_password(self):
        url_wildcard = str(''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(64)))
        timestamp = datetime.datetime.now()
        global session
        session = Session()
        session.query(User).filter_by(id = self.id).update({'reset_url':url_wildcard, 'url_time':timestamp})
        session.commit()
        session.close()
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

    def generate_key(self):
        key = str(''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(16)))
        self.set_key(key)
        return key

    def set_key(self, key):
        session = Session()
        self.session_token = key
        session.query(User).filter_by(id = self.id).update({'session_token':key})
        session.commit()
        session.close()

    def log_out(self):
        session = Session()
        self.authenticated = False
        self.session_token = "none"
        session.query(User).filter_by(id = self.id).update({'authenticated':self.authenticated})
        session.query(User).filter_by(id = self.id).update({'session_token':self.session_token})
        session.commit()
        session.close()

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
    def is_attending(cls, email):
        global session
        session = Session()
        exists = session.query(User).filter_by(email=email).first()
        session.close()
        if exists:
            return False
        else:
            return True

    @classmethod
    def get_user_by_url(cls, url):
        global session
        session = Session()
        user = session.query(User).filter_by(reset_url=url).first()
        session.close()
        if user:
            return user

    @classmethod
    def log_in(cls, email, user_psw):
        user = cls.get_user(email)
        if user is not None:
            if user_psw == user.password:
                session = Session()
                user.authenticated = True
                user.session_token = urandom(8)
                user.session_token = str(user.session_token)
                session.query(User).filter_by(id = user.id).update({'authenticated':user.authenticated})
                session.query(User).filter_by(id = user.id).update({'session_token':user.session_token})
                session.commit()
                session.close()
                return user
        return None

    @classmethod
    def hash_password(cls, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    @classmethod
    def get_user(cls, email):
        ''' Get user by email '''
        session = Session()
        user = session.query(User).filter_by(email=email).first()
        session.close()
        return user

    @staticmethod
    def get_user_by_id(user_id):
        ''' Get user by id '''
        session = Session()
        user = session.query(User).filter_by(id=user_id).first()
        session.close()
        if user is not None:
            return user
        else:
            return None
