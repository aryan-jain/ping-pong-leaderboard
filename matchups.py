import argparse
import itertools


def main():
    matchups = []
    if args.type == "singles":
        for player in itertools.combinations(args.players, 2):
            matchups.append(player)

    elif args.type == "doubles":
        teams = list(itertools.combinations(args.players, 2))
        for team in itertools.combinations(teams, 2):
            players = set(team[0]).union(set(team[1]))
            if len(players) == 4:
                matchups.append(team)

    print(f"There are {len(matchups)} possible games.")
    for match in matchups:
        print(f"{match[0]} vs. {match[1]}")


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
