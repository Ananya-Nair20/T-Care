# backend/app/services/leaderboard_service.py
from sqlalchemy.orm import Session
from ..models.gamification import GamificationProfile

class LeaderboardService:
    @staticmethod
    def calculate_score(profile: GamificationProfile) -> int:
        """
        Calculate a gamified score for a donor based on multiple factors:
        - donations_milestone: each donation = 10 points
        - emergency donations: each emergency donation = 20 points
        - current streak: each day in streak = 5 points
        - longest streak bonus: each day = 2 points
        """
        donations_points = profile.donations_milestone * 10
        emergency_points = profile.achievements.get("emergency_donations", 0) * 20
        streak_points = profile.current_streak * 5
        longest_streak_points = profile.longest_streak * 2

        total_score = donations_points + emergency_points + streak_points + longest_streak_points
        return total_score

    @staticmethod
    def get_points_leaderboard(session: Session, top_n: int = 10):
        """
        Returns the top N donors based on calculated gamified points.
        """
        profiles = session.query(GamificationProfile).all()

        # Create a sortable list with scores
        leaderboard_list = []
        for profile in profiles:
            score = LeaderboardService.calculate_score(profile)
            leaderboard_list.append({
                "user_id": profile.user_id,
                "score": score,
                "donations": profile.donations_milestone,
                "emergency_donations": profile.achievements.get("emergency_donations", 0),
                "current_streak": profile.current_streak,
                "longest_streak": profile.longest_streak,
                "badges": profile.badges
            })

        # Sort descending by score
        leaderboard_list.sort(key=lambda x: x["score"], reverse=True)

        # Assign ranks
        for rank, entry in enumerate(leaderboard_list, start=1):
            entry["rank"] = rank

        return leaderboard_list[:top_n]
    def add_points(self, user_id: str, points: int):
        """Add points to a donor’s score"""
        profile = self.session.query(GamificationProfile).filter_by(user_id=user_id).first()
        if not profile:
            print(f"[Gamification] User {user_id} not found. Creating profile.")
            profile = GamificationProfile(user_id=user_id)
            self.session.add(profile)
            self.session.commit()

        profile.total_points += points
        self.session.commit()

