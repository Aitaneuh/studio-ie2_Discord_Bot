from sqlalchemy.orm import Session
from database.models import Group, GroupMember, Player, Match, MatchPlayer
from itertools import combinations


class GroupRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_group(self, name: str, discord_role_id: str, discord_channel_id: str) -> Group:
        group = Group(name=name, discord_role_id=str(discord_role_id), discord_channel_id=str(discord_channel_id))
        self.db.add(group)
        self.db.commit()
        self.db.refresh(group)
        return group

    def add_member(self, group_id: int, player_id: str) -> GroupMember:
        member = GroupMember(group_id=group_id, player_id=player_id)
        self.db.add(member)
        self.db.commit()
        return member

    def get_all_groups(self) -> list[Group]:
        return self.db.query(Group).all()

    def get_group_by_id(self, group_id: int) -> Group | None:
        return self.db.query(Group).filter(Group.id == group_id).first()

    def get_group_of_player(self, discord_id: str) -> Group | None:
        member = (
            self.db.query(GroupMember)
            .filter(GroupMember.player_id == discord_id)
            .first()
        )
        return member.group if member else None

    def generate_round_robin_matches(self, group_id: int) -> list[Match]:
        """Génère tous les matchs Round Robin pour un groupe."""
        members = self.db.query(GroupMember).filter(GroupMember.group_id == group_id).all()
        player_ids = [m.player_id for m in members]
        created_matches = []

        for p1_id, p2_id in combinations(player_ids, 2):
            match = Match(group_id=group_id, stage="group", status="pending")
            self.db.add(match)
            self.db.flush()  # pour obtenir match.id

            self.db.add(MatchPlayer(match_id=match.id, player_id=p1_id))
            self.db.add(MatchPlayer(match_id=match.id, player_id=p2_id))
            created_matches.append(match)

        self.db.commit()
        return created_matches

    def get_group_standings(self, group_id: int) -> list[dict]:
        """Retourne le classement d'un groupe trié par victoires puis goal average."""
        members = self.db.query(GroupMember).filter(GroupMember.group_id == group_id).all()
        standings = []

        for member in members:
            player = member.player
            # Matchs du groupe terminés impliquant ce joueur
            finished_entries = (
                self.db.query(MatchPlayer)
                .join(Match)
                .filter(
                    Match.group_id == group_id,
                    Match.status == "finished",
                    MatchPlayer.player_id == player.discord_id,
                )
                .all()
            )
            wins = sum(1 for e in finished_entries if e.won)
            losses = sum(1 for e in finished_entries if not e.won)
            standings.append({
                "player": player,
                "wins": wins,
                "losses": losses,
                "goal_average": wins - losses,
            })

        standings.sort(key=lambda x: (x["wins"], x["goal_average"]), reverse=True)
        return standings

    def all_group_matches_finished(self, group_id: int) -> bool:
        pending = (
            self.db.query(Match)
            .filter(Match.group_id == group_id, Match.status == "pending")
            .count()
        )
        return pending == 0