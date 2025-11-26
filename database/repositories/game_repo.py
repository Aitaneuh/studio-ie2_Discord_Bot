from sqlalchemy.orm import Session
from database.models import Game, GamePlayer, Player

class GameRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_game(self, type: str):
        game = Game(type=type)
        self.db.add(game)
        self.db.commit()
        self.db.refresh(game)
        return game

    def get_game_by_id(self, game_id: int) -> Game:
        return self.db.query(Game).filter(Game.id == game_id).first()

    def finish_game_by_id(self, game_id: int):
        game = self.get_game_by_id(game_id)
        if not game:
            return None
        game.status = "finished" # type: ignore
        self.db.commit()
        self.db.refresh(game)
        return game

    def get_game_player_playing(self, discord_id: str):
        return (
            self.db.query(Game)
            .filter(Game.status == "pending")
            .filter(Game.players.any(GamePlayer.player.has(Player.discord_id == discord_id)))
            .first()
        )

