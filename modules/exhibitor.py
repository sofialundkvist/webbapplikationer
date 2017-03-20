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

    def create_lables(self, session):
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

    def get_labels(self, session):
        label_list = session.query(Label).filter_by(exhibitor_id=self.id).all()
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

        connections = Connection.get_all_connections(session, self.id)
        for row, connection in enumerate(connections, 2):
            data = connection.get_data(session)

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

    def got_connection(self, session, attendant_id):
        result = session.query(Connection).filter_by(exhibitor=self.id).filter_by(attendant_id = attendant_id).first()
        if result:
            return True
        else:
            return False

    def set_last_logged_in(self, session):
        self.last_logged_in = datetime.datetime.now()
        session.query(Exhibitor).filter_by(id = self.id).update({'last_logged_in':self.last_logged_in})
        session.commit()

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
    def get_exhibitor(cls, session, id):
        result = session.query(Exhibitor).filter_by(id=id).first()
        return result
