# Automated Sports Hedging System

## Description
This program continually identifies profitable hedging opportunities among most Australian sports in a variety of big bookmakers and notifies the user of big wins. A guaranteed profit of up to 5% of the initial stake was consistently seen throughout the development of this program.

Please note that betting limits and partially accepted bets imposed by bookies severely reduce the practical application of this program. This program is strictly shown for entertainment purposes.

## Prerequisites
1. Acquire an API key from [OddsAPI](https://the-odds-api.com/) and assign it to the 'API_KEY' variable in analysis.py and pre_game_analysis.py.
2. Setup an account on [Twilio](https://www.twilio.com/en-us) and assign your account id to the 'account_sid' variable and authentication token to the 'auth_token' variables in analysis.py and pre_game_analysis.py.
3. Assign an appropriate virtual/mobile number and your receiving mobile number to the 'from_' and 'to' parameters in the message object in analysis.py and pre_game_analysis.py.

## Usage
### python analysis.py
This gets the current aus sports and finds all hedging opportunities for head-to-head bets. Third party APIs may act as a bottleneck. Data is writted to 'potentials.json' in order of decreasing profits, and a user-friendly response is recorded in message.txt.

The program is also able to calculate proportional stake distributions.

### Different configurations for hedging identifier
Ensure the following parameters in the analysis.py file for the corresponding change to take effect:
1. 'upcoming_only=True' in 'sport_keys' object
    Looks at live games and upcoming 8 games. This is speedy and outcome of match is decided within hours usally.

2. 'upcoming_only=False' in 'sport_keys' object
    Program will look at all games over the next couple weeks. More potential opportunities at the cost of slower processing time.

3. 'upcoming_only=False' and 'commenceTimeTo= current+2 days' in 'odds_response' object.
    This combination allows for faster processing, but you can only see in 2 days time. 27 usage api points per script execution

Current configuration is set at option 3.
