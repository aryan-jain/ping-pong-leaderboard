import argparse
import itertools


def main():
    matchups = []
    if args.type == "singles":
        for player in itertools.combinations(args.players, 2):
            sit_out = tuple([p for p in args.players if p not in player])
            matchups.append((player[0], player[1], sit_out))

    elif args.type == "doubles":
        teams = list(itertools.combinations(args.players, 2))
        for team in itertools.combinations(teams, 2):
            players = set(team[0]).union(set(team[1]))
            if len(players) == 4:
                sit_out = tuple([p for p in args.players if p not in players])
                matchups.append((team[0], team[1], sit_out))

    print(f"There are {len(matchups)} possible games.")
    matchups = [
        y
        for x in zip(
            *[
                [j for j in i]
                for _, i in itertools.groupby(
                    sorted(matchups, key=lambda x: x[-1]), lambda x: x[-1]
                )
            ]
        )
        for y in x
    ]
    for match in matchups:
        print(f"{match[0]} vs. {match[1]} -- {','.join(match[2])} sits out.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a list of matchups given a list of players."
    )
    parser.add_argument("--players", "-p", type=str, nargs="+", required=True)
    parser.add_argument(
        "--type",
        "-t",
        type=str,
        choices=["singles", "doubles"],
        help="Game type. [singles, doubles] Default: doubles",
        default="doubles",
    )
    args = parser.parse_args()
    main()
