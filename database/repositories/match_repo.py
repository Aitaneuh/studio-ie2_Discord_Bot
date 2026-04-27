from sqlalchemy.orm import Session
from database.models import Match, MatchPlayer, Player


class MatchRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_match_by_id(self, match_id: int) -> Match | None:
        return self.db.query(Match).filter(Match.id == match_id).first()

    def get_pending_match_for_player(self, discord_id: str) -> Match | None:
        """Retourne le match en cours (pending) d'un joueur, s'il existe."""
        return (
            self.db.query(Match)
            .join(MatchPlayer)
            .filter(
                Match.status == "pending",
                MatchPlayer.player_id == discord_id,
            )
            .first()
        )

    def get_match_player(self, match_id: int, discord_id: str) -> MatchPlayer | None:
        return (
            self.db.query(MatchPlayer)
            .filter(
                MatchPlayer.match_id == match_id,
                MatchPlayer.player_id == discord_id,
            )
            .first()
        )

    def get_opponent(self, match_id: int, discord_id: str) -> MatchPlayer | None:
        return (
            self.db.query(MatchPlayer)
            .filter(
                MatchPlayer.match_id == match_id,
                MatchPlayer.player_id != discord_id,
            )
            .first()
        )

    def report_win(self, match_id: int, winner_discord_id: str) -> Match | None:
        """
        Enregistre le résultat d'un match.
        On attend que les DEUX joueurs aient reporté pour valider.
        Retourne le match si les deux ont reporté ET sont d'accord, None sinon.
        Lève ValueError si les deux ont reporté mais leurs déclarations sont contradictoires.
        """
        winner_entry = self.get_match_player(match_id, winner_discord_id)
        if not winner_entry or winner_entry.reported:
            return None

        winner_entry.won = True
        winner_entry.reported = True

        opponent_entry = self.get_opponent(match_id, winner_discord_id)
        opponent_entry.won = False

        self.db.commit()

        # Vérifier si l'adversaire a déjà reporté
        self.db.refresh(opponent_entry)
        if not opponent_entry.reported:
            return None  # On attend l'adversaire

        # Les deux ont reporté — vérifier la cohérence
        if winner_entry.won == opponent_entry.won:
            # Conflit : les deux disent avoir gagné
            raise ValueError("conflict")

        # Tout est cohérent → finaliser le match
        return self._finalize_match(match_id)

    def _finalize_match(self, match_id: int) -> Match:
        match = self.get_match_by_id(match_id)
        match.status = "finished"

        # Mettre à jour wins/losses sur les joueurs
        for entry in match.players:
            player = entry.player
            if entry.won:
                player.wins += 1
            else:
                player.losses += 1

        self.db.commit()
        self.db.refresh(match)
        return match

    def create_elimination_match(self, stage: str, p1_id: str, p2_id: str) -> Match:
        match = Match(group_id=None, stage=stage, status="pending")
        self.db.add(match)
        self.db.flush()
        self.db.add(MatchPlayer(match_id=match.id, player_id=p1_id))
        self.db.add(MatchPlayer(match_id=match.id, player_id=p2_id))
        self.db.commit()
        self.db.refresh(match)
        return match

    def get_elimination_matches_by_stage(self, stage: str) -> list[Match]:
        return self.db.query(Match).filter(Match.stage == stage).all()