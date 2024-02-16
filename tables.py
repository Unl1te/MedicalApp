import sqlalchemy as db
from db_session import SqlAlchemyBase


class Appointments(SqlAlchemyBase):
    __tablename__ = 'appointments'

    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    patientsurname = db.Column('patientsurname', db.String, nullable=False)
    patientname = db.Column('patientname', db.String, nullable=False)
    patientmidname = db.Column('patientmidname', db.String, nullable=False)
    medicament = db.Column('medicament', db.String, nullable=False)
    date = db.Column('date', db.String)


class Doctors(SqlAlchemyBase):
    __tablename__ = 'doctors'

    surname = db.Column('surname', db.String, nullable=False)
    name = db.Column('name', db.String, nullable=False)
    middlename = db.Column('middlename', db.String, nullable=False)
    password = db.Column('password', db.String, nullable=False)


class Medicaments(SqlAlchemyBase):

    __tablename__ = 'medicaments'

    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    medicament = db.Column('medicament', db.String, unique=True, nullable=False)
    amount = db.Column('amount', db.Integer, nullable=False)
    description = db.Column('description', db.String, nullable=False)

# engine = db.create_engine('sqlite:///Medicaments1.db')
# conn = engine.connect()
# metadata = db.MetaData()

