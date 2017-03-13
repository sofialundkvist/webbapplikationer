from flask_sqlalchemy import SQLAlchemy, declarative_base
from sqlalchemy import create_engine, Table, Column, Integer, String, ForeignKey, Boolean, Text, update, DateTime
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.associationproxy import association_proxy
import pymysql
pymysql.install_as_MySQLdb()
import MySQLdb

engine = create_engine('mysql://Doltishkey:trapporochkaffe@Doltishkey.mysql.pythonanywhere-services.com/Doltishkey$webbapp')
Base = declarative_base()
Base.metadata.reflect(engine)
Session = sessionmaker(bind=engine)
