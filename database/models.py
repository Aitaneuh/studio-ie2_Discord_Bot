from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database.connection import Base
from datetime import datetime
from sqlalchemy.sql import func

class Player(Base):
    __tablename__ = "players"

    discord_id = Column(String, primary_key=True, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    cr_tag = Column(String, unique=True, nullable=False)
    cr_username = Column(String, nullable=False)
    cr_trophy_count = Column(Integer, nullable=False)
    acc_wins = Column(Integer, nullable=False)
    seed = Column(Integer, nullable=True)
    wins = Column(Integer, nullable=False)
    losses = Column(Integer, nullable=False)

    games = relationship("GamePlayer", back_populates="player")

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="pending", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    type = Column(String, nullable=False) # Examples : swiss stage 0-0 / swiss stage 2-1 / 8 of final / semi final

    players = relationship("GamePlayer", back_populates="game")

class GamePlayer(Base):
    __tablename__ = "game_players"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.discord_id"), nullable=False)

    won = Column(Boolean, default=False)

    # Relations
    game = relationship("Game", back_populates="players")
    player = relationship("Player", back_populates="games")
