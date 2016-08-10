Generates keeper values based on Yahoo webpage inputs and rules provided via command arguments.

For help:

    $ ./get_keeper_data.py --help

# Example
Example league has the following rules:

* Players dafted in the Nth round last year get slotted in the Nth-2 round this year
* All non-drafted players that were picked up last year are slotted in the 10th round
* Players drafted in the first 3 rounds are not keepable
* Unkeepable players will be noted with a 99 round keeper value

With that, the command will look like:

    $ ./get_keeper_data.py -o input_examples/owners.yaml -d input_examples/draft.txt -r input_examples/rosters.txt -k 2 -f 10 --unkeepable-rounds 3 --unkeepable-round-id 99

# Requirements
Using python3:

    pip3 install -r requirements.txt

# Input
There are 3 files needed:

* Final roster from previous season (`-r`)
* Draft results from previous season (`-d`)
* List of team owners (`-o`)

Eamples are provided in the [input_examples directory](input_examples).

To obtain roster and draft input files, use the following URLs by replacing:

* `$PREVIOUS_YEAR`: Last season's year
* `$LEAGUE_ID`: Yahoo league ID

URLs:

* Rosters: http://football.fantasysports.yahoo.com/f1/$LEAGUE_ID/starters
* Draft (Rounds tab): http://football.fantasysports.yahoo.com/archive/nfl/$PREVIOUS_YEAR/$LEAGUE_ID/draftresults

The owners file is a simple YAML file with a hash that maps team names to owner name. E.g.:

    ---
    City Marshalls: Belmin
    Crunk Gronks: Tito

# Outut

# Notes
* When an NFL player switches team, I cannot tell if he cleared waivers so I give him the worst (highest number) round
