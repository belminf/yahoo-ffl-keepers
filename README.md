Using python3.

# Requirements
    pip3 install -r requirements.txt

# Data sources
Use the following URLs by replacing:

* `$PREVIOUS_YEAR`: Last season's year
* `$LEAGUE_ID`: Yahoo league ID

URLs:

* Rosters: http://football.fantasysports.yahoo.com/f1/$LEAGUE_ID/starters
* Draft (Rounds tab): http://football.fantasysports.yahoo.com/archive/nfl/$PREVIOUS_YEAR/$LEAGUE_ID/draftresults
'''

# Notes
* When an NFL player switches team, I cannot tell if he cleared waivers so I give him the worst (highest number) round
