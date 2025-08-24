import os
from backend.app.services.data_import_service import DataImportService


class GamificationService:
    def __init__(self):
        # Path to CSV
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        csv_path = os.path.join(base_dir, "data", "hackathon_data.csv")

        # Import CSV
        self.data_importer = DataImportService(csv_path)
        self.users = self.data_importer.load_csv()

        # Initialize gamification scores
        self.scores = {}
        for u in self.users:
            user_id = u.get("user_id")
            if user_id:
                # Base score = donations + call efficiency bonus
                donations = int(u.get("donations_till_date", 0) or 0)
                calls_ratio = float(u.get("calls_to_donations_ratio", 0) or 0.0)
                self.scores[user_id] = donations * 10 + int(calls_ratio * 5)

    def add_points(self, user_id: str, points: int):
        """Add gamification points to a user"""
        if user_id in self.scores:
            self.scores[user_id] += points
        else:
            print(f"[Gamification] User {user_id} not found.")

    def get_leaderboard(self, top_n: int = 5):
        """Return top N donors sorted by score"""
        sorted_scores = sorted(self.scores.items(), key=lambda x: x[1], reverse=True)
        leaderboard = []

        for user_id, score in sorted_scores[:top_n]:
            user = next((u for u in self.users if u.get("user_id") == user_id), None)
            if user:
                leaderboard.append({
                    "name": user.get("role", "Unknown"),  # could change to `role` or add a name column later
                    "user_id": user_id,
                    "score": score,
                    "donations": user.get("donations_till_date", "0"),
                    "blood_group": user.get("blood_group", "Unknown"),
                })
        return leaderboard


if __name__ == "__main__":
    game = GamificationService()
    # Demo: manually add points
    game.add_points("1", 50)
    game.add_points("2", 30)

    print("Leaderboard:")
    for entry in game.get_leaderboard():
        print(entry)
