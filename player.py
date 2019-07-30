from datetime import date
from operator import itemgetter

class Player(object):
    
    def __init__(self, name):
        self.name = name
        self.rating = 1400
        self.won = 0
        self.lost = 0
        self.games = []
    
    def daily_games(self):
        today = date.today()
        return len([g for g in self.games if g['date'] == today])

    def total_played(self):
        return len(self.games)

    def add_result(self, result):
        """Add result of new game to game log for this player
        
        Arguments:
            result {dict} -- dict with keys {winner: str, loser: str, point_difference: int, date: datetime.date}
        """
        self.games.append(result)
        self.games = sorted(self.games, key=itemgetter('date'))

    def last_game(self):
        return max([g['date'] for g in self.games])

    def __lt__(self, other):
        return self.rating < other.rating

    def __eq__(self, other):
        return self.rating == other.rating

    def get_dict(self):
        return {
                'Won': self.won,
                'Lost': self.lost,
                'Total Played': self.total_played(),
                'Games Today': self.daily_games(),
                'Rating': self.rating
        }

    def __str__(self):
        return f"{self.name.title()}: {self.get_dict()}"