from datetime import datetime, timedelta
from operator import itemgetter


def dt_floor(t:datetime, scale='day') -> datetime:
    if scale == 'day':
        return t - timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond)
    else:
        return t - timedelta(seconds=t.second, microseconds=t.microsecond)


class Player(object):

    def __init__(self, name):
        self.name = name
        self.rating = 1400
        self.won = 0
        self.lost = 0
        self.games = []

    def daily_games(self):
        today = dt_floor(datetime.now())
        return len([g for g in self.games if dt_floor(g['date']) == today])

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
        return max([g['date'] for g in self.games], default=None)

    def get_form(self):
        if self.games:
            form = ["W" if x['winner'] == self.name else "L" for x in sorted(self.games, key=itemgetter('date'), reverse=True)[:5]]
            return ' '.join(form)
        else:
            return ""

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
                'Last Game': self.last_game(),
                'Rating': self.rating,
                'Form': self.get_form()
        }

    def __str__(self):
        return f"{self.name.title()}: {self.get_dict()}"
