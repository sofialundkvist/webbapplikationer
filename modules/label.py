from modules.db_connector import *
from modules.validator import Validator


class Label(Base):

    __tablename__ = 'label'
    __table_args__={'extend_existing':True}

    id = Column(Integer, primary_key=True)
    exhibitor_id = Column(ForeignKey('exhibitor.id'))
    label = Column(String)
    color = Column(String)

    def __init__(self, exhibitor, label, color):
        self.exhibitor_id = exhibitor.id
        self.label = label
        self.color = color

    def get_data(self):
        return {'text':self.label, 'color':self.color, 'id':self.id}

    def get_exhibitor(self):
        return self.exhibitor_id

    def set_text(self, session, text):
        session.query(Label).filter_by(id = self.id).update({'label':text})
        session.commit()

    def set_color(self, session, color):
        session.query(Label).filter_by(id = self.id).update({'color':color})
        session.commit()

    def update(self,session, text, color):

        if self.label != text:
            self.set_text(session, text)

        if self.color != color:
            self.set_color(session, color)

    def delete(self, session):
        session.delete(self)
        session.commit()
        return True

    @classmethod
    def get_label(cls, session, id):
        result = session.query(Label).filter_by(id=id).first()
        return result
