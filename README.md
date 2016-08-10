Using some sources from Yahoo FFL webpages, this generates keeper data based on rules provided in the arguments.

View `get_keeper_data.py --help`

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
