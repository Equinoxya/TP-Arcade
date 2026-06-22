from sqlalchemy import create_engine, ForeignKey

DATABASE_URL = "sqlite:///app.db"

engine = create_engine(DATABASE_URL)
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()

class Borne(Base):
    __tablename__ = "borne"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    borne_type= Column(Integer, ForeignKey('games_types.id'))
    price= Column(Float, nullable=False)
    status_id = Column(Integer, ForeignKey("status.id"))
    nb_games = Column(Integer, nullable=False)
class Game(Base):
    __tablename__ = "game"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
class Status(Base):
    __tablename__ = "status"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, nullable=False)
class Games_types(Base):
    __tablename__="games_types"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, nullable=False)

Base.metadata.create_all(engine)
with Session(engine) as session:
    statuts = [
        Status(name='Disponible'),
        Status(name= 'Occupée'),
        Status(name= 'Maintenance')
    ]
    games_type =[
        Games_types(name='Course'),
        Games_types(name='Combat'),
        Games_types(name='Puzzle'),
        Games_types(name='Tir'),
        Games_types(name='Flipper'),
        Games_types(name='Sport')
        
    ]
    if session.query(Status).count() == 0:
        session.add_all(statuts)
        session.commit()
    if session.query(Games_types).count() == 0:
        session.add_all(games_type)
        session.commit()
        print('Status ajoutés')

print("Base créée")