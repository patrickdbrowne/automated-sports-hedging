import requests
import json
import sys
import smtplib
from email.mime.text import MIMEText
from datetime import date, datetime
import time

class SportsArb:
    def __init__(self, API_KEY, SPORT=None, REGIONS=None, MARKETS=None, ODDS_FORMAT=None, DATE_FORMAT=None):
        self.API_KEY = API_KEY
        self.SPORT = SPORT
        self.REGIONS = REGIONS
        self.MARKETS = MARKETS
        self.ODDS_FORMAT = ODDS_FORMAT
        self.DATE_FORMAT = DATE_FORMAT
        self.struct = {
            "sports_title": None,
            "home_team": None,
            "ht_bookmaker": None,
            "ht_type": "h2h",
            "highest_ht_odds": 0,
            "away_team": None,
            "at_bookmaker": None,
            "at_type": "h2h",
            "highest_at_odds": 0,
            "opportunity": False,
            "sum_implied": 0,
            "ht_stake": 0,
            "at_stake": 0,  
            "profit": 0,   
            "commencement": None,

            "draw": False,
            "highest_draw_odds": 0,
            "draw_bookmaker": None,
            "draw_stake": 0,       
        }

        self.all_matches = []
        self.potentials = []

    def getAvailableSports(self, write_to_file=False, upcoming_only=False):
        """GET ALL KEY SPORT TYPES - AFL, NFL, NBA etc. TO ITERATE THROUGH (ERROR!)"""

        if not(upcoming_only):
            sports_response = requests.get(
                'https://api.the-odds-api.com/v4/sports', 
                params={
                    'api_key': self.API_KEY
                }
            ).json()

            if write_to_file:
                with open("sports_data.json", "w") as f:
                    json.dump(sports_response, f, indent=4)
            
            ls_sports = []

            # list of sport keys to send to API later
            for sport in sports_response:
                ls_sports.append(sport["key"])
            return ls_sports

        else: 
            # Returns live games and upcoming 8 sport games
            return ["upcoming"]

    def retrieveOdds(self, file=None):
        """For a given sports key, compare the highest odds for teams across all australian markets
        Input:
            If you want to READ FROM A FILE:
                - file = path to .json file
                - SELF.sport = the sport you want analysed (constructor)
            
            If you want to GET A REQUEST:
                - name = name of the file you want to dump the request into for keeping records
                - SELF.sport = the sport you want analysed (constructor)
        
        """

        if file == None:
            # /v4/sports/{sport}/odds/?apiKey={apiKey}&regions={regions}&markets={markets}
            odds_response = requests.get(f'https://api.the-odds-api.com/v4/sports/{self.SPORT}/odds', params={
                'api_key': self.API_KEY,
                'regions': self.REGIONS,
                'markets': self.MARKETS,
                'oddsFormat': self.ODDS_FORMAT,
                'dateFormat': self.DATE_FORMAT,
            }).json()

            with open(f"sports_data/{self.SPORT}.json", "w") as f:
                json.dump(odds_response, f, indent=4)

            path = f"sports_data/{self.SPORT}.json"
        else:
            path = file

        with open(path) as f:
            odds_response = json.load(f)


        # Go through each dictionary in JSON from API to find:
            # Highest odds for the home team in any market
            # Highest odds for the away team in any market
        
        if not("message" in odds_response):
            # Indicates error with combination of parameters in url
            for match in odds_response:
                self.struct["sports_title"] = match["sport_title"]
                self.struct["home_team"] = match["home_team"]
                self.struct["away_team"] = match["away_team"]
                highest_home_odds = 0
                ht_booky = ""
                highest_away_odds = 0
                at_booky = ""
                ht_type = "h2h"
                at_type = "h2h"
                highest_draw = 0
                draw_booky = ""
                draw_status = False
                
                for i in match["bookmakers"]:
                    # the "market" is an array and first element is 'h2h'
                    # for now, consider only two odds (i.e., no draws)
                    if len(i["markets"][0]["outcomes"]) <= 3:
                        # Which position in the list home,away,and draw teams are
                        key_home = -1
                        key_away = -1
                        key_draw = -1

                        ##### If there are three options
                        if len(i["markets"][0]["outcomes"]) == 3:
                            draw_status = True
                            
                            # home
                            if self.struct["home_team"] == i["markets"][0]["outcomes"][0]["name"]: 
                                key_home = 0
                            if self.struct["home_team"] == i["markets"][0]["outcomes"][1]["name"]:
                                key_home = 1
                            if self.struct["home_team"] == i["markets"][0]["outcomes"][2]["name"]:
                                key_home = 2
                            
                            # away
                            if self.struct["away_team"] == i["markets"][0]["outcomes"][0]["name"]: 
                                key_away = 0
                            if self.struct["away_team"] == i["markets"][0]["outcomes"][1]["name"]:
                                key_away = 1
                            if self.struct["away_team"] == i["markets"][0]["outcomes"][2]["name"]:
                                key_away = 2
                            
                            # draw
                            if "Draw" == i["markets"][0]["outcomes"][0]["name"]: 
                                key_draw = 0
                            if "Draw" == i["markets"][0]["outcomes"][1]["name"]:
                                key_draw = 1
                            if "Draw" == i["markets"][0]["outcomes"][2]["name"]:
                                key_draw = 2 

                        ## If there are two options
                        elif len(i["markets"][0]["outcomes"]) == 2:
                            
                            # home
                            if self.struct["home_team"] == i["markets"][0]["outcomes"][0]["name"]: 
                                key_home = 0
                                key_away = 1
                            if self.struct["home_team"] == i["markets"][0]["outcomes"][1]["name"]:
                                key_home = 1
                                key_away = 0

                        # If there's a draw
                        if draw_status:
                            
                            if i["markets"][0]["outcomes"][key_draw]["price"] > highest_draw:
                                highest_draw = i["markets"][0]["outcomes"][key_draw]["price"]
                                draw_booky = i["title"]

                            if i["markets"][0]["outcomes"][key_home]["price"] > highest_home_odds:
                                highest_home_odds = i["markets"][0]["outcomes"][key_home]["price"]
                                ht_booky = i["title"]
                                ht_type = i["markets"][0]["key"]
                            
                            if i["markets"][0]["outcomes"][key_away]["price"] > highest_away_odds:
                                highest_away_odds = i["markets"][0]["outcomes"][key_away]["price"]
                                at_booky = i["title"]
                                at_type = i["markets"][0]["key"]

                        
                        # If there is no draw - two outcomes
                        elif not(draw_status):
                            if i["markets"][0]["outcomes"][key_home]["price"] > highest_home_odds:
                                highest_home_odds = i["markets"][0]["outcomes"][key_home]["price"]
                                ht_booky = i["title"]
                                ht_type = i["markets"][0]["key"]
                            
                            if i["markets"][0]["outcomes"][key_away]["price"] > highest_away_odds:
                                highest_away_odds = i["markets"][0]["outcomes"][key_away]["price"]
                                at_booky = i["title"]
                                at_type = i["markets"][0]["key"]
    

                    else: 
                        continue
                        
                self.struct["highest_ht_odds"] = highest_home_odds
                self.struct["ht_bookmaker"] = ht_booky
                self.struct["highest_at_odds"] = highest_away_odds
                self.struct["at_bookmaker"] = at_booky
                self.struct["ht_type"] = ht_type
                self.struct["at_type"] = at_type
                self.struct["commencement"] = match["commence_time"]
                self.struct["draw"] = draw_status
                self.struct["highest_draw_odds"] = highest_draw
                self.struct["draw_bookmaker"] = draw_booky

                self.all_matches.append(self.struct)
                self.struct = {
                    "sports_title": None,
                    "home_team": None,
                    "ht_bookmaker": None,
                    "ht_type": "h2h",
                    "highest_ht_odds": 0,
                    "away_team": None,
                    "at_bookmaker": None,
                    "at_type": "h2h",
                    "highest_at_odds": 0,
                    "opportunity": False,
                    "sum_implied": 0,
                    "ht_stake": 0,
                    "at_stake": 0,   
                    "profit": 0, 
                    "commencement": None,

                    "draw": False,
                    "highest_draw_odds": 0,
                    "draw_bookmaker": None,
                    "draw_stake": 0,  
                }

        return self.all_matches
    
    def checkOppos(self):
        """After running retrieveOdds, compare the odds in each hashmap in self.all_matches
        using implied probabilities"""

        potentials = []
        # If the sum of the implied probabilities of a match < 1 --> there is an opportunity to exploit the market
        for i in self.all_matches:
            # prevent division by zero error
            try:
                if i["highest_draw_odds"] == 0:
                    sum_implied = 1/(i["highest_ht_odds"]) + 1/(i["highest_at_odds"])

                else:
                    # If there are three outcomes including a draw
                    sum_implied = 1/(i["highest_ht_odds"]) + 1/(i["highest_at_odds"]) + 1/(i["highest_draw_odds"])
                
                i["sum_implied"] = sum_implied

                if sum_implied < 1:
                    i["opportunity"] = True
                    potentials.append(i)

            except:
                continue

        # Write matches with arbitrage opportunities to file
        with open("potentials.json", "w") as f:
            json.dump(potentials, f, indent=4)
        self.potentials = potentials

        return self.potentials
    
    def getData(self):
        return self.all_matches

    def calculateStakes(self, stake):
        """Given an arb opportunity, calculate how much to distribute the stake"""
        profit = 0
        for match in range(len(self.potentials)):
            ##### Check if there's a draw outcome
            if self.potentials[match]["draw"] == False:
                # Rearrange odd1 * partial = odd2 *(stake - partial)
                odd_home = self.potentials[match]["highest_ht_odds"]
                odd_away = self.potentials[match]["highest_at_odds"]
                partial = (odd_away * stake)/(odd_home + odd_away)

                # How much to bet for the home team given stake and odds
                self.potentials[match]["ht_stake"] = partial
                self.potentials[match]["at_stake"] = stake - partial
                self.potentials[match]["profit"] = partial * odd_home - stake
            
            elif self.potentials[match]["draw"] == True:
                sum_implied = self.potentials[match]["sum_implied"]
                odd_home = self.potentials[match]["highest_ht_odds"]
                odd_away = self.potentials[match]["highest_at_odds"]
                odd_draw = self.potentials[match]["highest_draw_odds"]

                self.potentials[match]["ht_stake"] = stake * (1/odd_home)/(sum_implied)
                self.potentials[match]["at_stake"] = stake * (1/odd_away)/(sum_implied)
                self.potentials[match]["draw_stake"] = stake * (1/odd_draw)/(sum_implied)

                # For safety, consider minumum return for profit (worst-case sceneraio) but they should all be equal
                min_revenue = min([self.potentials[match]["ht_stake"] * odd_home, self.potentials[match]["at_stake"] * odd_away, self.potentials[match]["draw_stake"] * odd_draw])
                self.potentials[match]["profit"] = min_revenue - stake
        return self.potentials

if __name__ == "__main__":  
    while True:

        redistribute = False
        if len(sys.argv) > 1:
            # Indicates recalculate current distribution with new stake
            redistribute = True

        if not(redistribute):
            API_KEY = "YOUR API KEY HERE" # $25 USD for 20k rq/month. 

            # uk | us | us2 | eu | au. Multiple can be specified if comma delimited.
            REGIONS = "au"

            # h2h | spreads | totals. Multiple can be specified if comma delimited
            # h2h (head-to-head) is the win-or-lose betting type
            MARKETS = "h2h"

            # decimal | american
            ODDS_FORMAT = "decimal"

            # iso | unix. iso is yyyy-mm-dd and unix is number of seconds after 1970 jan 1
            DATE_FORMAT = "iso"

            # upcoming only -> true for LIVE GAMES ONLY (less API usage points)
            # upcoming only -> false for PRE-GAME HEDGES (LOWER RISK/REWARD)
            sport_keys = SportsArb(API_KEY).getAvailableSports(write_to_file=True, upcoming_only=False)

            total_oppos = []

            for sport_key in sport_keys:
                # Get odds for all selected sports
                query = SportsArb(API_KEY, sport_key, REGIONS, MARKETS, ODDS_FORMAT, DATE_FORMAT)
                query.retrieveOdds()
                query.checkOppos()
                total_oppos.append(query.calculateStakes(1000))

            filtered_oppos_uns = [element for element in total_oppos if len(element) > 0]
            filtered_oppos_uns2 = []

            # Formatting
            for arr in filtered_oppos_uns:
                for data in arr:
                    filtered_oppos_uns2.append(data)

            filtered_oppos = sorted(filtered_oppos_uns2, key=lambda x: x["profit"], reverse=True)

        else:
            # Redistribute current bets with a new stake
            new_stake = float(sys.argv[1])
            filtered_oppos = None
            with open("potentials.json") as f:
                filtered_oppos = json.load(f)
            
                # Iterate through each match and update values
                for match in filtered_oppos:
                    if match["draw"] == False:
                        odd_home = match["highest_ht_odds"]
                        odd_away = match["highest_at_odds"]
                        partial = (odd_away * new_stake)/(odd_home + odd_away)

                        # How much to bet for the home team given stake and odds
                        match["ht_stake"] = partial
                        match["at_stake"] = new_stake - partial
                        match["profit"] = partial * odd_home - new_stake  

                    elif match["draw"] == True:
                        sum_implied = match["sum_implied"]
                        odd_home = match["highest_ht_odds"]
                        odd_away = match["highest_at_odds"]
                        odd_draw = match["highest_draw_odds"]

                        match["ht_stake"] = new_stake * (1/odd_home)/(sum_implied)
                        match["at_stake"] = new_stake * (1/odd_away)/(sum_implied)
                        match["draw_stake"] = new_stake * (1/odd_draw)/(sum_implied)

                        # For safety, consider minumum return for profit (worst-case sceneraio) but they should all be equal
                        min_revenue = min([match["ht_stake"] * odd_home, match["at_stake"] * odd_away, match["draw_stake"] * odd_draw])
                        match["profit"] = min_revenue - new_stake

        with open("message_pregame.txt", "wb") as f:
            f.write(f"""Here are your hedging opportunities! ({datetime.now().strftime("%Y-%m-%d %H:%M:%S")})""".encode('utf-8'))
            f.write(f"Google what's in the square brackets for pre-game\n\n".encode('utf-8'))

            for i in filtered_oppos:
                f.write(f"{i['sports_title']}\n".encode('utf-8'))
                f.write(f"{i['home_team']} vs. {i['away_team']}\nCommence time: {i['commencement']}\n\n".encode('utf-8'))
                if i["draw"] == False:
                    f.write(f"With ${int(i['ht_stake']+i['at_stake'])}, distribute your stake by:\n".encode('utf-8'))
                if i["draw"] == True:
                    f.write(f"With ${int(i['ht_stake']+i['at_stake']+i['draw_stake'])}, distribute your stake by:\n".encode('utf-8'))
                f.write(f"{i['ht_bookmaker']} - ${i['ht_stake']:.2f} on {i['highest_ht_odds']} odds for {i['home_team']} [{i['ht_bookmaker']} {i['sports_title']} {i['home_team']} vs. {i['away_team']}]\n".encode('utf-8'))
                f.write(f"{i['at_bookmaker']} - ${i['at_stake']:.2f} on {i['highest_at_odds']} odds for {i['away_team']} [{i['at_bookmaker']} {i['sports_title']} {i['home_team']} vs. {i['away_team']}]\n".encode('utf-8'))
                if i["draw"] == True:
                    f.write(f"{i['draw_bookmaker']} - ${i['draw_stake']:.2f} on {i['highest_draw_odds']} odds for a draw. [{i['draw_bookmaker']} {i['sports_title']} {i['home_team']} vs. {i['away_team']}]\n".encode('utf-8'))
                f.write(f"\nThis should give ${i['profit']:.2f} of profit!\n\n\n\n".encode('utf-8')) 

        with open("potentials.json", "w") as f:
            json.dump(filtered_oppos, f, indent=4)

        with open("message_pregame.txt", "r") as f:
            for line in f.readlines():
                print(line, end="")
        
        # SMS ON UR PHONE IF THERE'S A POTENTIAL BIG WIN
        sendSMS = False
        if filtered_oppos != []:
            if filtered_oppos[0]["profit"] > 50:
                sendSMS = True
        
        if sendSMS:

            from twilio.rest import Client
            account_sid = 'ACCOUNT ID'
            auth_token = 'AUTHENTICATION TOKEN'
            client = Client(account_sid, auth_token)

            message = client.messages.create(
            from_='FROM PHONE NUMBER',
            body="Opportunity to make $50+! Check message_pregame.txt on your laptop.",
            to='RECEIVING MOBILE NUMBER')
        
        
        # Execute script every 'interval' seconds
        if len(sys.argv) > 1:
            break

        interval = 300
        time.sleep(interval)
            