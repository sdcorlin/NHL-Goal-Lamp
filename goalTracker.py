import time
import requests
import json
import schedule
from datetime import datetime


favorite_team = "LAK"
def lightTheLamp():
    # Right now, this just prints GOAL! but it needs to control the lights
    print("GOALLLL!")

def updateScore(boxscore):
    if boxscore['clock']['inIntermission'] == True:
        print("Intermission! {} Remaining!".format(boxscore['clock']['timeRemaining']))
        print("{}: {}\n{}: {}\n".format(boxscore['awayTeam']['abbrev'], boxscore['awayTeam']['score'], boxscore['homeTeam']['abbrev'], boxscore['homeTeam']['score']))
        time.sleep(boxscore['clock']['secondsRemaining'])
    else:
        print("{}\nPeriod - {}\nTime - {}".format(boxscore['gameState'], boxscore['period'], boxscore['clock']['timeRemaining']))
        print("{}: {}\n{}: {}\n".format(boxscore['awayTeam']['abbrev'], boxscore['awayTeam']['score'], boxscore['homeTeam']['abbrev'], boxscore['homeTeam']['score']))

def live_game(game_url, home_team):
    # Game States: PRE, LIVE, FINAL
    currentGoals = 0
    while 1:
        boxscore = requests.get(game_url)
        if boxscore.status_code == 200:
            boxscore = json.loads(boxscore.text)
            if boxscore['gameState'] == "FINAL":
                updateScore(boxscore)
                break
            if boxscore[home_team]['score'] > currentGoals:
                lightTheLamp()
                currentGoals = boxscore[home_team]['score']
            elif boxscore[home_team]['score'] < currentGoals:
                print("Goal Disallowed!!!")
                currentGoals = boxscore[home_team]['score']
            updateScore(boxscore)
            time.sleep(30)

def waitToStart(startTime):
    if datetime.utcnow() < datetime.strptime(startTime, "%Y-%m-%dT%H:%M:%SZ"):
        print("Game hasn't started yet! Waiting to continue!")
    while datetime.utcnow() < datetime.strptime(startTime, "%Y-%m-%dT%H:%M:%SZ"):
        time.sleep(600)
    
def get_games():
    game_id = 0
    game_id, home_team = gamesToday()
    if game_id!=0:
        game_boxscore_url = "https://api-web.nhle.com/v1/gamecenter/{}/boxscore".format(game_id)
        live_game(game_boxscore_url, home_team)
    else:
        print("No game tonight :(")

def gamesToday():
    url = "https://api-web.nhle.com/v1/score/now"
    data = requests.get(url)
    if data.status_code != 200:
        print("API Request Failed!")
        return 0, "NA"
    todaysGames = json.loads(data.text)['games']
    for game in todaysGames:
        if game['homeTeam']['abbrev'] == favorite_team:
            gameStart = game.get("startTimeUTC")
            print("Game Tonight!! {} @ {} at {}".format(game['awayTeam']['abbrev'], game['homeTeam']['abbrev'], gameStart))
            waitToStart(gameStart)
            return game['id'], "homeTeam"
        if game['awayTeam']['abbrev'] == favorite_team:
            gameStart = game.get("startTimeUTC")
            print("Game Tonight!! {} @ {} at {}".format(game['awayTeam']['abbrev'], game['homeTeam']['abbrev'], gameStart))
            waitToStart(gameStart)
            return game['id'], "awayTeam"
    return 0, "NA"
    
schedule.every().day.at('09:00').do(get_games)

if __name__ == "__main__":
    while 1:
        schedule.run_pending()
        time.sleep(1)
        
