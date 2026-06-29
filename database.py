from __future__ import annotations
from pathlib import Path
from sqlalchemy import ForeignKey, Integer, String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

DB_PATH = Path("db_orm.db")
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass
class Borne(Base):
    __tablename__ = "borne"
    id: Mapped[int] = mapped_column( primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    borne_type: Mapped[int]= mapped_column(ForeignKey('games_types.id'))
    price: Mapped[float]= mapped_column(nullable=False)
    status_id: Mapped[int] = mapped_column(ForeignKey("status.id"))
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    nb_games: Mapped[int] = mapped_column(nullable=False)
    #Relations
    game: Mapped[Game] = relationship('Game', back_populates="bornes")
    status: Mapped[Status] = relationship("Status", back_populates="bornes")
    type: Mapped[Games_types] = relationship("Games_types", back_populates="bornes")
class Game(Base):
    __tablename__ = "games"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    #Relations
    bornes: Mapped[list[Borne]] = relationship("Borne", back_populates="game")
class Status(Base):
    __tablename__ = "status"
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)

    bornes: Mapped[list[Borne]] = relationship("Borne", back_populates="status")
class Games_types(Base):
    __tablename__="games_types"
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    
    bornes: Mapped[list[Borne]] = relationship("Borne", back_populates="type")

Base.metadata.create_all(engine)
with Session(engine) as session:
    game = [
        Game(name="Sonic"),
        Game(name="Mario"),
        Game(name="Pacman"),
        Game(name="Akira"),
        Game(name="Pokemon Premium"),
        Game(name="Jurassic Park"),
        Game(name="Superblaster"),
        Game(name="Need For Speed"),
        Game(name="Power Boat")
    ]
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
    if session.scalar(select(func.count()).select_from(Game)) == 0:
        session.add_all(game)
        session.commit()
    if session.scalar(select(func.count()).select_from(Status)) == 0:
        session.add_all(statuts)
        session.commit()
    if session.scalar(select(func.count()).select_from(Games_types)) == 0:
        session.add_all(games_type)
        session.commit()
        print('Status ajoutés')

print("Base créée")