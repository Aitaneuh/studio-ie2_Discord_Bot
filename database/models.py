from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database.connection import Base
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
    wins = Column(Integer, nullable=False, default=0)
    losses = Column(Integer, nullable=False, default=0)

    group_memberships = relationship("GroupMember", back_populates="player")
    match_entries = relationship("MatchPlayer", back_populates="player")


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)                   # "Groupe 1"
    discord_role_id = Column(String, nullable=True)         # ID du rôle Discord
    discord_channel_id = Column(String, nullable=True)      # ID du salon Discord

    members = relationship("GroupMember", back_populates="group")
    matches = relationship("Match", back_populates="group")


class GroupMember(Base):
    __tablename__ = "group_members"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    player_id = Column(String, ForeignKey("players.discord_id"), nullable=False)

    group = relationship("Group", back_populates="members")
    player = relationship("Player", back_populates="group_memberships")


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)  # NULL en phase éliminatoire
    stage = Column(String, nullable=False)  # "group" | "quarterfinal" | "semifinal" | "final"
    status = Column(String, default="pending", nullable=False)  # "pending" | "finished"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    group = relationship("Group", back_populates="matches")
    players = relationship("MatchPlayer", back_populates="match")


class MatchPlayer(Base):
    __tablename__ = "match_players"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    player_id = Column(String, ForeignKey("players.discord_id"), nullable=False)
    won = Column(Boolean, default=False, nullable=False)
    reported = Column(Boolean, default=False, nullable=False)  # a-t-il soumis son résultat ?

    match = relationship("Match", back_populates="players")
    player = relationship("Player", back_populates="match_entries")