from modules.db_connector import *
from modules.validator import Validator
import qrcode
import random, string
import os.path
from PIL import Image
from modules.mailmaster import Mailmaster

class Attendant(Base):

    __tablename__ = 'attendant'
    __table_args__={'extend_existing':True}

    id = Column(Integer, primary_key=True)
    email = Column(String)
    first_name = Column(String)
    surname = Column(String)
    birth_month = Column(Integer)
    birth_day = Column(Integer)
    school = Column(String)
    commune = Column(String)
    front_end_id = Column(String)
    qr = Column(String)
    profession = Column(String)
    subjects = relationship("Subject", backref="attendant")
    years = relationship("Teaching_year", backref="attendant")


    def __init__(self, contact_info):
        self.email = contact_info['email']
        self.first_name = contact_info['first_name']
        self.surname = contact_info['surname']
        self.birth_month = contact_info['month']
        self.birth_day = contact_info['day']
        self.school = contact_info['school']
        self.commune = contact_info['commune']
        self.profession = contact_info['profession']
        self.front_end_id = self.set_front_end_id()

    def set_subjects(self, subjects):
        attendant_id = self.get_id()
        for subject in subjects:
            subjecter = Subject(subject, self)
            session.add(subjecter)
            session.commit()

    def set_teach_years(self, years):
        attendant_id = self.get_id()
        for year in years:
            yearer = Teaching_year(year, self)
            session.add(yearer)
            session.commit()

    def get_info(self):
        return {
            'email': self.email,
            'first_name': self.first_name,
            'surname': self.surname,
            'birth_day': self.birth_day,
            'birth_month': self.birth_month,
            'school': self.school,
            'year': self.year,
            'commune': self.commune
        }

    def get_name(self):
        return self.first_name

    def get_email(self):
        return self.email

    def get_front_end_id(self):
        return self.front_end_id

    def get_id(self):
        user_id = session.query(Attendant).filter_by(email=self.email).first()
        return user_id.id

    def get_data(self):
        subjects = self.get_subjects()
        teaching_years = self.get_teaching_years()
        return {
        'id':self.id,
        'front_end_id':self.front_end_id,
        'email':self.email,
        'first_name':self.first_name,
        'surname':self.surname,
        'school':self.school,
        'commune':self.commune,
        'profession':self.profession,
        'subjects':subjects,
        'teaching_years':teaching_years
        }

    def get_subjects(self):
        session = Session()
        subjects = session.query(Subject).filter_by(attendant_id=self.id).all()
        session.close()
        subjects_text = []
        for subject in subjects:
            subject_text = subject.get_subject_text()
            subjects_text.append(subject_text)
        return subjects_text

    def get_teaching_years(self):
        session = Session()
        years = session.query(Teaching_year).filter_by(attendant_id=self.id).all()
        session.close()
        years_2 = []
        for year in years:
            years_2.append(year.get_year())
        return years_2

    def set_front_end_id(self):
        if len(self.birth_month) == 1:
            self.birth_month = "0" + self.birth_month
        if len(self.birth_day) == 1:
            self.birth_month = "0" + self.birth_day
        return self.first_name[0] + self.surname[0] + str(self.birth_month) + str(self.birth_day)

    def generate_qr(self):
        user_id = self.get_id()
        img = qrcode.make('https://massa.avmediaskane.se/attendant/'+self.front_end_id+'/'+str(user_id))

        img.filename = str(''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(16)))+'.png'
        while os.path.isfile('static/img/qr/' + img.filename) == True:
            img.filename = str(''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(16)))+'.png'
        save_path = "static/img/qr"
        file_path = "{path}/{file}".format(path=save_path, file=img.filename)
        img.save(file_path)
        session.query(Attendant).filter_by(id = user_id).update({'qr':img.filename})
        return img.filename

    def resend_email(self):
        message={
            'name': self.first_name,
            'front_end_id': self.front_end_id,
            'qr':'https://www.massa.avmediaskane.se/static/img/qr/'+self.qr,
            'link': 'https://www.massa.avmediaskane.se/thanks/'+str(self.front_end_id)+'/'+str(self.id)
        }
        Mailmaster.send(self.email, message)



    def delete(self):
        global session
        session = Session()
        session.delete(self)
        session.commit()
        session.close()

    @classmethod
    def check_month(cls, month):
        ''' Check if birthmonth is a valid number '''
        try:
            if int(month) in range(1, 13):
                return True
            else:
                return False
        except:
            return False

    @classmethod
    def check_day(cls, day):
        ''' Check if date of birthday is a valid number '''
        try:
            if int(day) in range(1, 32):
                return True
            else:
                return False
        except:
            return False

    @classmethod
    def create(cls, contact_info):
        if not contact_info['day']:
            contact_info['day'] = 'Finns inte'

        # Validering
        validation_dict = {
        'exists': cls.is_attending(contact_info['email']),
        'first_name': Validator.is_empty(contact_info['first_name']),
        'surname': Validator.is_empty(contact_info['surname']),
        'email': Validator.email(contact_info['email']),
        'birth_month': Attendant.check_month(contact_info['month']),
        'birth_day': Attendant.check_day(contact_info['day'])
        }

        for key, value in validation_dict.items():
            if not value:
                return False, validation_dict

        # Konvertering
        contact_info['list_subjects'] = Validator.remove_empty(contact_info['list_subjects'])
        contact_info['list_years'] = Validator.remove_empty(contact_info['list_years'])

        global session
        session = Session()
        attendant = Attendant(contact_info)
        session.add(attendant)
        session.flush()
        attendant.set_subjects(contact_info['list_subjects'])
        attendant.set_teach_years(contact_info['list_years'])
        attendant_qr = attendant.generate_qr()
        message={
            'name': attendant.get_name(),
            'front_end_id': attendant.get_front_end_id(),
            'qr':'https://www.massa.avmediaskane.se/static/img/qr/'+attendant_qr,
            'link': 'https://www.massa.avmediaskane.se/thanks/'+str(attendant.front_end_id)+'/'+str(attendant.id)
        }
        return_data = {
            'front_end_id':attendant.front_end_id,
            'id':attendant.id
        }
        session.commit()
        session.close()
        Mailmaster.send(contact_info['email'], message)
        return True, return_data

    @classmethod
    def is_attending(cls, email):
        global session
        session = Session()
        exists = session.query(Attendant).filter_by(email=email).first()
        session.close()
        if exists:
            return False
        else:
            return True

    @classmethod
    def get_user(cls,id):
        global session
        session = Session()
        result = session.query(Attendant).filter_by(id=id).first()
        session.close()
        return result

    @classmethod
    def get_user_multi(cls, front_end_id, id):
        global session
        session = Session()
        result = session.query(Attendant).filter_by(id=id).filter_by(front_end_id=front_end_id).first()
        session.expunge_all()
        session.close()
        return result

    @classmethod
    def get_from_front_id(cls, front_end_id):
        global session
        session = Session()
        attendants = session.query(Attendant).filter_by(front_end_id=front_end_id).all()
        attendant_list =[]
        for attendant in attendants:
            attendant_list.append(attendant.get_data())
        session.close()
        return attendant_list

    @classmethod
    def get_all_attendants(cls):
        global session
        session = Session()
        result = session.query(Attendant).all()
        session.close()
        return result

class Subject(Base):

    __tablename__ = 'subjects'
    __table_args__={'extend_existing':True}

    id = Column(Integer, primary_key=True)
    attendant_id = Column(ForeignKey('attendant.id'))
    subject = Column(String)

    def __init__(self, subject_name, attendant_id):
        self.subject = subject_name
        self.attendant = attendant_id

    def get_subject_text(self):
        return self.subject

class Teaching_year(Base):
    __tablename__ = 'teaching_year'
    __table_args__={'extend_existing':True}

    id = Column(Integer, primary_key=True)
    attendant_id = Column(ForeignKey('attendant.id'))
    year = Column(String)

    def __init__(self, teaching_year, attendant_id):
        self.year = teaching_year
        self.attendant = attendant_id

    def get_year(self):
        return self.year
