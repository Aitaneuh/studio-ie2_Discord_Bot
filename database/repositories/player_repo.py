from sqlalchemy.orm import Session
from database.models import Player

class PlayerRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_player(self, discord_id: str, first_name: str, last_name: str, cr_tag: str, cr_username: str, cr_trophy_count: int) -> Player:
        player = Player(discord_id=discord_id, first_name=first_name, last_name=last_name, cr_tag=cr_tag, cr_username=cr_username, cr_trophy_count=cr_trophy_count, wins=0, losses=0)
        self.db.add(player)
        self.db.commit()
        self.db.refresh(player)
        return player

    def get_player_by_discord_id(self, discord_id: str) -> Player | None:
        return self.db.query(Player).filter(Player.discord_id == discord_id).first()

    def get_all_players(self) -> list[Player]:
        return self.db.query(Player).all()
