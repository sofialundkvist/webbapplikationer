from modules.db_connector import *
from modules.label import Label
from modules.attendant import Attendant

class Connection(Base):
    __tablename__ = 'connection'
    __table_args__ = {'extend_existing':True}

    id = Column(Integer, primary_key=True)
    attendant_id = Column(ForeignKey('attendant.id'))
    exhibitor = Column(ForeignKey('exhibitor.id'))
    comment = Column(String)


    def __init__(self, exhibitor_id, attendant):
        self.attendant_id = attendant
        self.exhibitor = exhibitor_id
        self.comment = None
        self.labels = []

    def get_exhibitor(self):
        return self.exhibitor

    def add_comment(self, comment):
        global session
        session = Session()
        session.query(Connection).filter_by(id = self.id).update({'comment':comment})
        session.flush()
        session.commit()
        session.close()

    def add_label(self, label):
        global session
        session = Session()
        label_connection = Label_to_Connection(label.id, self.id)
        session.add(label_connection)
        session.commit()
        session.close()

    def get_labels(self):
        global session
        session = Session()
        labels = session.query(Label).join(Label_to_Connection).filter_by(connection_id=self.id).all()
        session.expunge_all()
        session.close()
        return labels

    def get_data(self):
        labels = self.get_labels()
        session = Session()

        attendant = session.query(Attendant).filter_by(id=self.attendant_id).first()
        session.expunge_all()
        session.close()

        connection_data = {
            'comment': self.comment,
            'labels':[],
            'attendant': attendant.get_data(),
            'id':self.id
        }
        for label in labels:
            connection_data['labels'].append(label.get_data())
        return connection_data


    @classmethod
    def get_connection(cls, connection_id):
        global session
        session = Session()
        connection = session.query(Connection).filter_by(id=connection_id).first()
        session.expunge_all()
        session.close()
        return connection

    @classmethod
    def get_connection_by_users(cls, exhibitor_id, attendant_id):
        global session
        session = Session()
        connection = session.query(Connection).filter_by(exhibitor=exhibitor_id).filter_by(attendant_id = attendant_id).first()
        session.expunge_all()
        session.close()
        return connection

    @classmethod
    def get_all_connections(cls, exhibitor_id):
        global session
        session = Session()
        connections = session.query(Connection).filter_by(exhibitor=exhibitor_id).all()
        session.close()
        return connections

    @classmethod
    def get_every_connection(cls):
        global session
        session = Session()
        result = session.query(Connection).all()
        session.close()
        return result


class Label_to_Connection(Base):
    __tablename__ = 'label_to_connection'
    __table_args__ = {'extend_existing':True}

    label_id = Column(ForeignKey('label.id'), primary_key=True)
    connection_id = Column(ForeignKey('connection.id'), primary_key=True)

    def __init__(self, label, connection):
        self.label_id = label
        self.connection_id = connection


    @classmethod
    def remove(cls, connection_id):
        global session
        session = Session()
        connections = session.query(Label_to_Connection).filter_by(connection_id=connection_id).delete()
        session.commit()
        session.close()
        return connections
