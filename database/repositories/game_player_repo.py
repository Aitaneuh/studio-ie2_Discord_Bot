from sqlalchemy.orm import Session
from database.models import GamePlayer, Player

class GamePlayerRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_game_player(self, game_id: int, player_id: str):
        game_player = GamePlayer(game_id=game_id, player_id=player_id)
        self.db.add(game_player)
        self.db.commit()
        self.db.refresh(game_player)
        return game_player
    
    def get_game_player_by_game_and_player(self, game_id: int, discord_id: str) -> GamePlayer:
        return (
            self.db.query(GamePlayer)
            .join(GamePlayer.player)
            .filter(GamePlayer.game_id == game_id)
            .filter(Player.discord_id == discord_id)
            .first()
        )

    
    def report_game_win(self, game_id: int, player_id: str):
        game_player = self.get_game_player_by_game_and_player(game_id, player_id)
        game_player.won = True # type: ignore
        self.db.commit()
        self.db.refresh(game_player)
        return game_player