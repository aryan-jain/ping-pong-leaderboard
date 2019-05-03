import pickle
import datetime
import traceback
import pandas as pd
from argparse import ArgumentParser
import math

def update_players(leaderboard, winner, loser):
    """Update players details on the leaderboard
    
    Arguments:
        leaderboard {pd.DataFrame} -- [description]
        winner {str} -- Name of the winning player
        loser {str} -- Name of the losing player
    """
    today = datetime.date.today().strftime("%Y-%m-%d")

    # Using rating_diff here is case we want to weight the difference in the future
    rating_diff = leaderboard.loc[winner, "Rating"] - leaderboard.loc[loser, "Rating"]

    # First check for each players number of games today
    if leaderboard.loc[winner, 'Games Today'] >= 3 and leaderboard.loc[winner, "Last Day"] == today:
        print(f"\n{winner} already played three games today so their score cannot be updated until tomorrow!")
    else:
        # Update wins
        leaderboard.loc[winner, "Won"] += 1

        # Update ratings
        if rating_diff == 0:
            print(f"Since, the 2 players were of the same rating, {winner} gains 7 rating points.")
            leaderboard.loc[winner, "Rating"] += 7
        elif rating_diff > 0:
            print(f"Since, {winner} was of a higher rating than {loser}, {winner} gains 5 rating points.")
            leaderboard.loc[winner, "Rating"] += 5
        else:
            print(f"Since, {winner} was of a lower rating than {loser}, {winner} gains 10 rating points.")
            leaderboard.loc[winner, "Rating"] += 10
        
        # Update number of games played today
        if leaderboard.loc[winner, "Last Day"] == today:
            leaderboard.loc[winner, "Games Today"] += 1
        else:
            leaderboard.loc[winner, "Games Today"] = 1
            leaderboard.loc[winner, "Last Day"] = today

    # First check for each players number of games today
    if leaderboard.loc[loser, "Games Today"] >= 3 and leaderboard.loc[loser, "Last Day"] == today:
        print(f"\n{loser} already played three games today so their score cannot be updated until tomorrow!")
    else:
        leaderboard.loc[loser, "Lost"] += 1

        if rating_diff == 0:
            print(f"Since, the 2 players were of the same rating, {loser} loses 7 rating points.")
            leaderboard.loc[loser, "Rating"] -= 7
        elif rating_diff > 0:
            print(f"Since, {loser} was of a lower rating than {winner}, {loser} loses 5 rating points.")
            leaderboard.loc[loser, "Rating"] -= 5
        else:
            print(f"Since, {loser} was of a higher rating than {winner}, {loser} loses 10 rating points.")
            leaderboard.loc[loser, "Rating"] -= 10

        # Update number of games played today
        if leaderboard.loc[loser, "Last Day"] == today:
            leaderboard.loc[loser, "Games Today"] += 1
        else:
            leaderboard.loc[loser, "Games Today"] = 1
            leaderboard.loc[loser, "Last Day"] = today

    return leaderboard

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--path', '-p', default='.', help='Path to a leaderboard pickle.')
    parser.add_argument('--style', '-s', default='singles', choices=['singles', 'doubles'], help='Modifying either the singles or doubles leaderboard.')
    args = parser.parse_args()

    path = f"{args.path}/leaderboard_{args.style}.pkl"
    try:
        leaderboard = pd.read_pickle(path)
    except:
        print(f"Could not find {path}.")
        leaderboard = pd.DataFrame(columns=['Name', 'Won', 'Lost', 'Rating', 'Games Today', 'Last Day', 'Rank'])
        leaderboard.set_index("Name", inplace = True)

    if not leaderboard.empty:
        print(f"Here is the preexisiting {args.style} leaderboard:")
        print(leaderboard)
    else:
        print("Could not find an exisitng leaderboard, creating a fresh one.")

    players = []
    valid_teams = False
    i=1
    while not valid_teams:
        pl = input(f"\nState the name of the {ordinal(i)} player (e.g. aryan, Aryan or Aryan Jain are all acceptable)\nFor Doubles, spearate the 2 names with a comma ','\nEnter Name(s):\t").strip()
        if "," in pl:
            pls = pl.split(",")
            if len(pls) > 2: 
                raise Exception(f"You cannot have more than 2 players in a team. This is not North Korea")
            team = []
            for pl in pls:
                player = leaderboard[leaderboard.index.str.match(pl, case=False)]
                if not player.empty:
                    print(f"Player Record Found:\n{player}")
                elif len(player) > 1:
                    print(f"Found more than one player with that name.\n{pd.Series(player.index.values)}")
                    disambiguate = input("Enter player number you intended from the list above:\t")
                    disambiguate = int(disambiguate)
                    player = player.iloc[disambiguate]
                else:
                    print(f"Player Record Not Found. Creating new entry...")
                    leaderboard[pl.title(),:] = [0,0,1440.0,0,datetime.date.today().strftime("%Y-%m-%d"), len(leaderboard)]
                    player = leaderboard[pl.title(),:]
                team.append(player.index.values[0])
            players.append(team)
        
        else:
            player = leaderboard[leaderboard.index.str.match(pl, case=False)]
            if not player.empty:
                print(f"Player Record Found:\n{player}")
            elif len(player) > 1:
                print(f"Found more than one player with that name.\n{pd.Series(player.index.values)}")
                disambiguate = input("Enter player number you intended from the list above:\t")
                disambiguate = int(disambiguate)
                player = player.iloc[disambiguate]
            else:
                print(f"Player Record Not Found. Creating new entry...")
                leaderboard[pl.title()] = [0,0,1440.0,0,datetime.date.today().strftime("%Y-%m-%d"), len(leaderboard)]

            players.append(player.index.values[0])
        
        if len(players) == 2:
            valid_teams = True
        
        i += 1

    print("\n\n\n")
    print("TeamA: ", players[0])
    print("TeamB: ", players[1])

    teamA_members, teamB_members = players

    valid_winner = False
    while not valid_winner:
        winner = input("\nWhich team won; A or B? ").strip().upper()
        if winner in ['A', 'B']:
            valid_winner = True
        else:
            print("You must enter only a single character; A or B")

    print("\n\n\n")
    if args.style == 'singles':
        w = teamA_members if winner == 'A' else teamB_members
        l = teamA_members if winner == 'B' else teamB_members

        leaderboard = update_players(leaderboard, w, l)

        leaderboard["Total Games"] = leaderboard.apply(lambda r: r["Won"] + r["Lost"], axis=1)
        leaderboard.sort_values('Total Games', inplace=True, ascending=False)

        leaderboard["Rank"] = leaderboard["Rating"].rank(method="first", ascending=False)
        leaderboard.sort_values('Rank', inplace=True)

    else:
        print("Doubles is not yet implemented.")

    print(f"\nUpdated {args.style} leaderboard:\n{leaderboard}")
    leaderboard.to_pickle(f'{path}')
