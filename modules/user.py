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

    def get_password(self):
        return self.password

    def generate_key(self, session):
        key = str(''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(16)))
        self.set_key(session, key)
        return key

    def set_key(self, session, key):
        self.session_token = key
        session.query(User).filter_by(id = self.id).update({'session_token':key})
        session.commit()

    '''def log_out(self, session):
        self.authenticated = False
        self.session_token = "none"
        session.query(User).filter_by(id = self.id).update({'authenticated':self.authenticated})
        session.query(User).filter_by(id = self.id).update({'session_token':self.session_token})
        session.commit()'''

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

    @classmethod
    def is_attending(cls, session, email):
        exists = session.query(User).filter_by(email=email).first()
        if exists:
            return False
        else:
            return True

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
