import argparse, sys, pickle, traceback, math, logging
import pandas as pd
from datetime import date
from player import Player
"""
@author: aryan-jain
@version: 0.1
@description: 
    This is an ELO Rating scheme implementation of a leaderboard.
    
    The leaderboard will be stored as a list of player objects in a pickle, which
    will be loaded on each run. The player object contains the log of all games that
    the player has played.
    
    The base rating for a new player is set to 1400.
    
    The K-Factor has been fixed at 10 as an appropriate value for a low number
    of players and a medium number of games. For doubles games, K-Factor will be
    reduced to 5 to dampen the ELO effect for a good player on a losing team, or
    a bad player on a winning team. 
    
    There is a margin-of-victory multiplier that is being applied to the K-Factor
    in an effort to make point differences in games matter more.

    The margin-of-victory multiplier is a logarithmic curve with a base of Euler's 
    number and an aymptote that shifts based on the ELO rating difference between 
    the 2 players. Under smaller ELO rating differentials, the asymptote should be 
    close to 1.75. For doubles games, the margin of victory multiplier will have a 
    base of 10 to reduce the asymptote significantly.
"""

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])


def get_df(players):
    """Takes a list of Player objects and returns a DataFrame
    representation along with rankings for each player.
    
    Arguments:
        players {list[Player]} -- list of Player objects
    """
    ranked = {
        p.name:p.get_dict()
        for p in players
    }
    df = pd.DataFrame.from_dict(ranked, orient='index')
    df.sort_values('Rating', inplace = True, ascending=False)
    df['Rank'] = [ordinal(x + 1) for x in range(len(df))]
    cols = list(df.columns)
    df = df.loc[:, cols[-1:]+cols[:-1]]
    return df

def prob_win(player, opponent):
    """Computes probability of player winning
    against opponent.
    
    Arguments:
        player {Player} 
        opponent {Player}
    
    Returns:
        float
    """
    elo_diff = player.rating - opponent.rating
    return 1 / (10**(-elo_diff/150) + 1)


def margin_mltp(win_elo, loss_elo, result: dict, style:str="singles") -> float:
    """Computes margin of victory multiplier for ELO gains or losses
    
    Arguments:
        player {Player}
        opponent {Player}
        result {dict} -- dict with keys {winner: str, loser: str, point_difference: int, date: datetime.date}
    
    Returns:
        float
    """
    if style == 'singles':
        base = math.e
    if style == 'doubles':
        base = 10
    pd = result['point_difference']
    return math.log10(abs(pd) + 1)/math.log10(base) * (2.2/((win_elo-loss_elo)*0.005 + 2.2))


def get_rank(player: Player, leaderboard: list) -> str:
    return ordinal(sorted(leaderboard).index(player) + 1)


def update_player(player: Player, result: dict, opponent: Player, style:str="singles") -> Player:
    """update player's ELO rating based on result
    
    Arguments:
        player {Player}
        result {dict}
        opponent {Player}
    
    Returns:
        Player
    """
    if style == "singles":
        ro = player.rating
        k = 10
        if result['winner'] == player.name.title():
            multiplier = margin_mltp(ro, opponent.rating, result)
            expected = prob_win(player, opponent)
            diff = k*multiplier*(1 - expected)
            
            logger.info(f"Expected probability of {player.name} winning was = {expected}")
            logger.info(f"Margin of victory multiplier = {multiplier}")

            # rn = ro + diff
            # player.rating = rn
            player.add_result(result)
            return player, diff
        else:
            multiplier = margin_mltp(opponent.rating, ro, result)
            expected = prob_win(player, opponent)
            diff = k*multiplier*(0 - expected)

            logger.info(f"Expected probability of {player.name} winning was = {expected}")
            logger.info(f"Margin of loss multiplier = {multiplier}")

            # rn = ro + diff
            # player.rating = rn
            player.add_result(result)
            return player, diff


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', '-p', default='.', help='Path to a leaderboard pickle.')
    parser.add_argument('--style', '-s', default='singles', choices=['singles', 'doubles'], help='Game format.')
    parser.add_argument('--log', '-l', default='INFO', 
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help='Log level.')

    args = parser.parse_args()

    global logger
    logging.basicConfig(
            level=args.log, 
            format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', 
            datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger('evolve')

    path = f"{args.path}/elo_leaderboard.pkl"
    
    try:
        leaderboard = pickle.load(open(path, 'rb'))
    except:
        logger.error(f"Could not finding exisitng leaderboard at {path}")
        create_new = input(f"Create new leaderboard at {path}? [Y|N] ")
        if str2bool(create_new):
            leaderboard = []
        else:
            logger.fatal("Please re-run with correct path!")
            sys.exit()

    if leaderboard:
        logger.info(f"Here is the preexisiting {args.style} leaderboard:")
        print(get_df(leaderboard))

    valid_teams = False
    players = []
    i = 1
    while not valid_teams:
        pl = input(f"\nState the name of the {ordinal(i)} player (e.g. aryan, Aryan or Aryan Jain are all acceptable)\nFor Doubles, spearate the 2 names with a comma ','\nEnter Name(s):\t").strip()
        if "," in pl:
            args.__setattr__("style", "doubles")
            pls = pl.split(",")
            if len(pls) > 2: 
                raise Exception(f"You cannot have more than 2 players in a team. This is not North Korea")
            team = []
            for pl in pls:
                find = [x for x in leaderboard if pl.lower() in x.name.lower()]
                if find:
                    if len(find) > 1:
                        print("Found more than one player with that name.\n{}".format('\n'.join([f'{num} -- {v.name.title()}' for num,v in enumerate(find)])))
                        disambiguate = input("Enter player number you intended from the list above:\t")
                        disambiguate = int(disambiguate)
                        team.append(find[disambiguate])
                    else:
                        logger.info(f"Player Record Found:\n{str(find)}")
                        team.append(find)
                else:
                    find = input(f"Could not find player record! In order to create a new one, please enter your full name or hit [Enter] to abort: ").strip()
                    if find:
                        new_player = Player(find.title()) 
                        team.append(new_player)
                        leaderboard.append(new_player)
                    else:
                        logger.fatal(f"Please start over!")
                        sys.exit()
            players.append(team)
        else:
            find = [x for x in leaderboard if pl.lower() in x.name.lower()]
            if find:
                if len(find) > 1:
                    print("Found more than one player with that name.\n{}".format('\n'.join([f'{num} -- {v.name.title()}' for num,v in enumerate(find)])))
                    disambiguate = input("Enter player number you intended from the list above:\t")
                    disambiguate = int(disambiguate)
                    players.append(find[disambiguate])
                else:
                    logger.info(f"Player Record Found:\n{str(find[0])}")
                    players.append(find[0])
            else:
                find = input(f"Could not find player record! In order to create a new one, please enter your full name or hit [Enter] to abort: ").strip()
                if find:
                    new_player = Player(find.title()) 
                    players.append(new_player)
                    leaderboard.append(new_player)
                else:
                    logger.fatal(f"Please start over!")
                    sys.exit()
        i += 1
        if len(players) == 2:
            valid_teams = True

    if type(players[0]) == list:
        logger.info(f"Proceeding with doubles weighting for ELO deltas...")
        print("\n\n\n")
        print("Team 1:\n\t{}\n\t{}".format(players[0][0].name, players[0][1].name))
        print("Team 2:\n\t{}\n\t{}".format(players[1][0].name, players[1][1].name))

    else:
        logger.info(f"Proceeding with singles weighting for ELO deltas...")
        print("\n\n\n")
        print("Team 1:\n\t{}".format(players[0]))
        print("Team 2:\n\t{}".format(players[1]))

        valid_winner = False
        while not valid_winner:
            winner = int(input("\nWhich team won; 1 or 2? "))
            if winner in [1,2]:
                point_diff = int(input("By how many points? [2-21]"))
                if 2 <= point_diff <= 21:
                    valid_winner = True
                else:
                    print("The minimum point difference is 2 and the maxiumum is 21.")
            else:
                print("You must enter only a single character; 1 or 2")
        winner -= 1

        winner = players.pop(winner)
        loser = players[0]

        result = {
            "winner": winner.name.title(),
            "loser": loser.name.title(),
            "point_difference": point_diff,
            "date": date.today()
        }

        winner, w_diff = update_player(winner, result, loser)
        loser, l_diff = update_player(loser, result, winner)
        
        print("\n\n\n")
        print(f"{winner.name} defeated {loser.name} by {point_diff} points.")
        if winner > loser:
            print(f"Since {winner.name} had a higher ELO rating than {loser.name}, {winner.name} gains an adjusted rating of {w_diff} points.")
            print(f"Since {loser.name} had a lower ELO rating than {winner.name}, {loser.name} loses an adjusted rating of {l_diff} points.")

        elif winner < loser:
            print(f"Since {winner.name} had a lower ELO rating than {loser.name}, {winner.name} gains an adjusted rating of {w_diff} points.")
            print(f"Since {loser.name} had a higher ELO rating than {winner.name}, {loser.name} loses an adjusted rating of {l_diff} points.")

        winner.rating += w_diff
        winner.won += 1
        loser.rating += l_diff
        loser.lost += 1

        for num, pl in enumerate(leaderboard):
            if pl.name == winner.name:
                leaderboard[num] = winner
            elif pl.name == loser.name:
                leaderboard[num] = loser
                
        print()
        print(get_df(leaderboard))
        pickle.dump(leaderboard, open(path, 'wb'))