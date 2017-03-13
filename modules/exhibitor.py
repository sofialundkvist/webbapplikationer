from modules.user import User
from modules.db_connector import *
from modules.validator import Validator
from modules.label import Label
from modules.connection import Connection
import datetime
import xlsxwriter


class Exhibitor(User):

    __tablename__ = 'exhibitor'
    __table_args__={'extend_existing':True}
    company_name = Column(String)
    last_logged_in = Column(String)
    id = Column(Integer, ForeignKey('program_user.id'), primary_key=True)

    def __init__(self, company_name, email):
        self.company_name = company_name
        self.last_logged_in = None
        User.__init__(self, email, 'Massa2017', auth_level = 1)

    def create_lables(self):
        labels = [
            {'text':'Ring',
            'color':'#663399'
            },
            {'text':'Mejla',
            'color':'#6BB9F0'
            },
            {'text':'Väldigt intresserad!',
            'color':'#00B16A'
            },
        ]
        for label in labels:
            new_label = Label(self, label['text'], label['color'])
            session.add(new_label)
            session.commit()

    def get_labels(self):
        global session
        session = Session()
        label_list = session.query(Label).filter_by(exhibitor_id=self.id).all()
        session.expunge_all()
        session.close()
        new_list = []
        for label in label_list:
            new_list.append(label.get_data())
        return new_list

    def get_id(self):
        return self.id

    def create_excel(self):
        ''' Create excel-file of exhibitor's saved contacts and return it '''
        workbook = xlsxwriter.Workbook('excel/kontaktuppgifter' + str(self.id) + '.xlsx')
        worksheet = workbook.add_worksheet()
        worksheet.write('A1', 'Förnamn')
        worksheet.write('B1', 'Efternamn')
        worksheet.write('C1', 'Email')
        worksheet.write('D1', 'Skola')
        worksheet.write('E1', 'Kommun')
        worksheet.write('F1', 'Yrke')
        worksheet.write('G1', 'Årskurs')
        worksheet.write('H1', 'Ämnen')
        worksheet.write('I1', 'Taggar')
        worksheet.write('J1', 'Kommentar')

        connections = Connection.get_all_connections(self.id)
        for row, connection in enumerate(connections, 2):
            data = connection.get_data()

            str_labels = ""
            for label in data['labels']:
                str_labels += label['text'] + ", "

            str_years = ""
            for year in data['attendant']['teaching_years']:
                str_years += year + ", "

            str_subjects = ""
            for subject in data['attendant']['subjects']:
                str_subjects += subject + ", "

            worksheet.write('A' + str(row), data['attendant']['first_name'])
            worksheet.write('B' + str(row), data['attendant']['surname'])
            worksheet.write('C' + str(row), data['attendant']['email'])
            worksheet.write('D' + str(row), data['attendant']['school'])
            worksheet.write('E' + str(row), data['attendant']['commune'])
            worksheet.write('F' + str(row), data['attendant']['profession'])
            worksheet.write('G' + str(row), str_years)
            worksheet.write('H' + str(row), str_subjects)
            worksheet.write('I' + str(row), str_labels)
            worksheet.write('J' + str(row), data['comment'])

        workbook.close()
        return workbook

    def got_connection(self, attendant_id):
        global session
        session = Session()
        result = session.query(Connection).filter_by(exhibitor=self.id).filter_by(attendant_id = attendant_id).first()
        session.close()
        if result:
            return True
        else:
            return False

    def delete(self):
        global session
        session = Session()
        session.delete(self)
        session.commit()
        session.close()
        return True

    def set_last_logged_in(self):
        session = Session()
        self.last_logged_in = datetime.datetime.now()
        session.query(Exhibitor).filter_by(id = self.id).update({'last_logged_in':self.last_logged_in})
        session.commit()
        session.close()

    def get_last_logged_in(self):
        return self.last_logged_in

    def get_data(self):
        connections = Connection.get_all_connections(self.id)
        data = {
        'id':self.id,
        'company':self.company_name,
        'email':self.email,
        'connections_count':len(connections),
        'connections':[]
        }
        for connection in connections:
            data['connections'].append(connection.get_data())
        return data


    @classmethod
    def create(cls, company_name, email):
        validation_dict = {
            'exists': cls.is_attending(email),
            'email': Validator.email(email),
            'company_name': Validator.is_empty(company_name),
        }

        for key, value in validation_dict.items():
            if not value:
                return False, validation_dict

        global session
        session = Session()
        exhibitor = Exhibitor(company_name, email)
        message = {"email": email, "password": "Massa2017"}
        session.add(exhibitor)
        session.flush()
        exhibitor.create_lables()
        session.expunge_all()
        session.close()
        return True, 'Skapad'

    @classmethod
    def get_exhibitor(cls,id):
        global session
        session = Session()
        result = session.query(Exhibitor).filter_by(id=id).first()
        session.expunge_all()
        session.close()
        return result

    @classmethod
    def get_all_exhibitors(cls):
        global session
        session = Session()
        result = session.query(Exhibitor).filter_by(auth_level=1).all()
        session.close()
        return result
