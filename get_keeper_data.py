#!/usr/bin/env python3

import re
import sys
import argparse
import yaml

# Globals for team mapping
team_owner_map = {}
team_owner_map_loaded = False
unknown_owners = []

# Roster reguglar expressions
#
# Team example:
# ~~
# Y Not Zoidberg?!
# Player  Cost
# ~~
#
# Player example
# ~~
# No new player Notes$
# Ben Roethlisberger Pit - QB$
# Mon 7:10 pm @ Washington
# ~~
ROSTER_TEAM_RE = re.compile(r'(?P<team>.*)\nPlayer[ \t]+Cost\n')
ROSTER_PLAYER_RE = re.compile(r'.*[nN]ote.*\n((?P<name>.+) (?P<team>[a-zA-Z]{2,3}) - (?P<pos>[A-Z]{1,3})\n((Out|Probable|Questionable|Suspended|PUP-P|Doubtful)\n)?.*(@|vs).*|(?P<empty>--empty--))\n?')

# Draft regular expressions
#
# Round example:
# ~
# Round 10
# ~
#
# Player example:
# ~
# 1.	LeSean McCoy
# (Buf - RB)
# Game of Foles
# ~
DRAFT_ROUND_RE = re.compile(r'Round (?P<round>[1-9][0-9]?)\n')
DRAFT_PLAYER_RE = re.compile(r'(?P<pick>[1-9][0-9]*)\.\s+(?P<player>.+)\n(.\n)?\((?P<team>[a-zA-Z]{2,3}) - (?P<pos>[A-Z]{1,3})\)\n(?P<owner>[^\n]+)\n?')


def main():
    args = parse_cmd()

    # Parse roster
    roster = parse_roster(args)
    if not roster:
        print('No valid roster, exiting')
        sys.exit()

    # Add keeper data
    roster = add_keeper_data(args, roster)
    if not roster:
        print('No valid keeper data, exiting')
        sys.exit()

    js_dict = ','.join(['"{}":{}'.format(p['name'], p['keeper_round']) for k, p in roster.items()])

    print('')
    print('To import to Yahoo\'s keeper page:')
    print('var k={{{}}};'.format(js_dict))


def parse_cmd():
    parser = argparse.ArgumentParser(description='Computes keeper value')

    parser.add_argument(
        '-d',
        metavar='FILE',
        type=argparse.FileType('r'),
        dest='f_draft',
        help='Yahoo draft results for last year',
    )

    parser.add_argument(
        '-r',
        metavar='FILE',
        type=argparse.FileType('r'),
        dest='f_roster',
        help='Yahoo final roster for last year',
    )

    parser.add_argument(
        '-o',
        metavar='FILE',
        type=argparse.FileType('r'),
        dest='f_owners',
        help='Mapping of team names to owners',
    )

    parser.add_argument(
        '-k',
        metavar='NUM_OF_ROUNDS',
        type=int,
        default=3,
        dest='keeper_sub_rounds',
        help='Number of rounds drafted players appreciate'
    )

    parser.add_argument(
        '-f',
        metavar='ROUND',
        type=int,
        default=12,
        dest='fa_round',
        help='Round for players that were free agent pick ups',
    )

    parser.add_argument(
        '--unkeepable-rounds',
        metavar='ROUND',
        type=int,
        default=5,
        dest='unkeepable_rounds',
        help='The number of top rounds that are unkeepable',
    )

    parser.add_argument(
        '-unkeepable-round-id',
        metavar='ROUND',
        type=int,
        default=999,
        dest='unkeepable_round_id',
        help='A number to indicate that a pick is unkeepable',
    )

    return parser.parse_args()


def get_player_key(player, team, pos):
    return '{}/{}/{}'.format(player.upper(), team.upper(), pos.upper())


def get_team_key(team):
    return team[:12].lower().strip()


def get_manager(args, team):
    global team_owner_map
    global team_owner_map_loaded
    global unknown_owners

    if not team_owner_map_loaded:
        original_map = yaml.safe_load(args.f_owners)
        team_owner_map = {get_team_key(k): v for k, v in original_map.items()}
        team_owner_map_loaded = True

    try:
        return team_owner_map[get_team_key(team)]
    except KeyError:
        if team not in unknown_owners:
            unknown_owners.append(team)
        return None


def parse_roster(args):
    global unknown_owners

    # Keep track through loop
    roster = {}
    current_snippet = ''
    current_team = ''
    for line in args.f_roster:

        # Skip empty lines
        if line.strip() == '':
            continue

        # Append to snippet
        current_snippet += line

        # Check if this is the team name
        team_match = ROSTER_TEAM_RE.fullmatch(current_snippet)
        if team_match:
            current_team = team_match.group('team')
            current_snippet = ''

        # We have 3 lines, so we have a player
        else:
            player_match = ROSTER_PLAYER_RE.fullmatch(current_snippet)
            if player_match:
                if not player_match.group('empty'):
                    player_name = player_match.group('name')
                    nfl_team = player_match.group('team')
                    nfl_pos = player_match.group('pos')
                    player_key = get_player_key(player_name, nfl_team, nfl_pos)
                    roster[player_key] = {
                        'last_manager': get_manager(args, current_team),
                        'name': player_name,
                        'nfl_team': nfl_team,
                        'nfl_pos': nfl_pos,
                        'draft_manager': '',
                        'draft_round': None,
                        'keeper_round': None,
                    }
                current_snippet = ''

    # If we still have soem text in current snippet, our regex is failing
    if current_snippet.strip():
        print('Error! Some text not caught, started at:\n------\n{}\n------'.format('\n'.join(current_snippet.split('\n')[:3])))
        return None

    # We have some unknown owners
    if len(unknown_owners):
        print ('Error! Unknown owners:\n{}'.format('\n - ' + '\n - '.join(unknown_owners)))
        return None

    return roster


def add_keeper_data(args, roster):

    # Add drafting data
    current_snippet = ''
    current_round = None
    for line in args.f_draft:

        # Skip empty lines
        if line.strip() == '':
            continue

        # Append to snippet
        current_snippet += line

        # Change round
        round_match = DRAFT_ROUND_RE.match(current_snippet)
        if round_match:
            current_round = round_match.group('round')
            current_snippet = ''
            continue

        # Check if it's a player
        player_match = DRAFT_PLAYER_RE.match(current_snippet)
        if player_match:
            player_name = player_match.group('player')
            nfl_team = player_match.group('team')
            nfl_pos = player_match.group('pos')
            draft_manager = get_manager(args, player_match.group('owner'))
            player_key = get_player_key(player_name, nfl_team, nfl_pos)
            if player_key in roster:
                roster[player_key]['current_round'] = current_round
                roster[player_key]['draft_manager'] = draft_manager
            else:
                print('%s - Not in any team anymore (ID=%s)' % (player_name, player_key))
            current_snippet = ''

    # If we still have some text in current snippet, our regex is failing
    if current_snippet.strip():
        print('Error! Some draft text not caught, started at:\n------\n{}\n------'.format('\n'.join(current_snippet.split('\n')[:3])))
        return None

    # Add keeper data
    for player_key in roster.keys():

        # Undrafted players
        if not roster[player_key].get('draft_manager'):
            roster[player_key]['current_round'] = 'FA'
            roster[player_key]['keeper_round'] = args.fa_round
        else:
            if int(roster[player_key]['current_round']) <= args.unkeepable_rounds:
                roster[player_key]['keeper_round'] = args.unkeepable_round_id
            else:
                if roster[player_key]['draft_manager'] == roster[player_key]['last_manager']:
                    roster[player_key]['keeper_round'] = int(roster[player_key]['current_round']) - args.keeper_sub_rounds
                else:
                    roster[player_key]['keeper_round'] = min(int(roster[player_key]['current_round']) - args.keeper_sub_rounds, args.fa_round)
    return roster


if __name__ == '__main__':
    main()
