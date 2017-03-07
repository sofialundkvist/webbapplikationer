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

    def set_text(self, text):
        global session
        session = Session()
        session.query(Label).filter_by(id = self.id).update({'label':text})
        session.commit()
        session.close()

    def set_color(self, color):
        global session
        session = Session()
        session.query(Label).filter_by(id = self.id).update({'color':color})
        session.commit()
        session.close()

    def update(self, text, color):

        if self.label != text:
            self.set_text(text)

        if self.color != color:
            self.set_color(color)

    def delete(self):
        global session
        session = Session()
        session.delete(self)
        session.commit()
        session.close()
        return True

    @classmethod
    def get_label(cls,id):
        global session
        session = Session()
        result = session.query(Label).filter_by(id=id).first()
        session.close()
        return result
