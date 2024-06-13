import csv
import re
import requests
from datetime import datetime
from os import getcwd, path
from chessdotcom import Client, get_player_games_by_month
from dateutil.relativedelta import relativedelta
from prettytable import PrettyTable

class Fetcher():
    def __init__(
            self, min_rating=2800, min_opponent=2800, time_control='180', time_class='blitz',
            start_date=datetime.now().strftime('%Y/%m'), end_date=datetime.now().strftime('%Y/%m'),
            csv_directory=getcwd(), csv_name=''
        ):
        self.LB_URL = "https://www.chess.com/callback/leaderboard/live/"
        self.__min_rating = min_rating
        self.__min_opponent = min_opponent
        self.__time_control = time_control
        self.__time_class = time_class
        self.__start_date = start_date
        self.__end_date = end_date
        self.__csv_directory = csv_directory
        self.__csv_name = csv_name
        self.__csv_default = False
        self.__csv_inhouse = False
        if not self.csv_name:
            self.__csv_default = True
            self.default_csv_name()
        self.__check_exclude = ['csv_default', 'csv_inhouse', 'check_exclude', 'LB_URL']
        self.set_client()
    def __str__(self):
        return self.csv_name
    @property
    def start_date(self):
        return self.__start_date
    @start_date.setter
    def start_date(self, new_value):
        if not self.validate_date_format(new_value):
            return
        self.__start_date = new_value
        self.__csv_inhouse = True
        self.default_csv_name()
    @property
    def end_date(self):
        return self.__end_date
    @end_date.setter
    def end_date(self, new_value):
        if not self.validate_date_format(new_value):
            return
        self.__end_date = new_value
        self.__csv_inhouse = True
        self.default_csv_name()
    @property
    def time_class(self):
        return self.__time_class
    @time_class.setter
    def time_class(self, new_value):
        if not isinstance(new_value, str):
            print("ERROR: time_class must be a string")
            return;
        new_value = new_value.lower()
        if new_value not in ['blitz', 'bullet', 'rapid', 'daily']:
            print("ERROR: time_class must be 'bullet', 'blitz', 'rapid' or 'daily'")
            return;
        self.__time_class = new_value
        self.__csv_inhouse = True
        self.default_csv_name()
    @property
    def time_control(self):
        return self.__time_control
    @time_control.setter
    def time_control(self, new_value):
        if not isinstance(new_value, str):
            print("ERROR: time_control must be a string.")
            return;
        if new_value[-2:] == "+0":
            new_value = new_value[:-2]
        print("Make sure to define time_control in seconds, e.g. 180 {0} 3".format(self.bold('NOT')))
        self.__time_control = new_value
        self.__csv_inhouse = True
        self.default_csv_name()
    @property
    def min_rating(self):
        return self.__min_rating
    @min_rating.setter
    def min_rating(self, new_value):
        if not isinstance(new_value, int):
            print("ERROR: min_rating must be an integer.")
            return;
        if new_value < 2500:
            print("WARNING: this will take a very long time to run.")
        self.__min_rating = new_value
        self.__csv_inhouse = True
        self.default_csv_name()
    @property
    def min_opponent(self):
        return self.__min_opponent
    @min_opponent.setter
    def min_opponent(self, new_value):
        if not isinstance(new_value, int):
            print("ERROR: min_opponent must be an integer.")
            return;
        self.__min_opponent = new_value
        self.__csv_inhouse = True
        self.default_csv_name()
    @property
    def csv_directory(self):
        return self.__csv_directory
    @csv_directory.setter
    def csv_directory(self, new_value):
        if not isinstance(new_value, str):
            print("ERROR: csv_directory must be a string.")
            return;
        self.__csv_directory = new_value
    @property
    def csv_name(self):
        return self.__csv_name
    @csv_name.setter
    def csv_name(self, new_value):
        if not isinstance(new_value, str):
            print("ERROR: csv_name must be a string.")
            return;
        self.__csv_name = new_value
        if not self.csv_name:
            self.__csv_default = True
            self.default_csv_name()
            return
        if not self.__csv_inhouse:
            self.__csv_default = False
        self.__csv_inhouse = False
    def bold(self, text):
        return "\033[1m" + text + "\033[0m"
    def validate_date_format(self, date):
        if not isinstance(date, str):
            print('ERROR: date must be a string.')
            return False
        pattern = re.compile(r"\d\d\d\d/\d\d$")
        if not pattern.match(date):
            print('ERROR: date must be in a "YYYY/MM" format.')
            return False
        if int(date[-2:]) > 12:
            print('ERROR: month can not be greater than 12.')
            return False
        return True
    def set_client(self, user_agent="CC Fetcher", tries=2, tts=4):
        Client.request_config["headers"]["User-Agent"] = (user_agent)
        Client.rate_limit_handler.tries = tries
        Client.rate_limit_handler.tts = tts
    def default_csv_name(self):
        if not self.__csv_default:
            return
        csv_name = "{0}_min{1}_".format(self.time_class, self.min_rating)
        if self.min_opponent != self.min_rating:
            csv_name += "minopp{0}_".format(self.min_opponent)
        csv_name += self.start_date.replace('/','-')
        if self.end_date != self.start_date:
            csv_name += "_" + self.end_date.replace('/','-')
        csv_name += '.csv'
        self.__csv_inhouse = True
        self.csv_name = csv_name
        print("Current CSV File Name: " + self.csv_name)
    @property
    def check(self):
        table = PrettyTable()
        table.field_names = ["Attribute", "Value", "Type"]
        for attr in list(self.__dict__):
            readable_attr = attr.replace('_Fetcher__','')
            if readable_attr in self.__check_exclude:
                continue
            table.add_row([readable_attr, getattr(self, attr), type(getattr(self, attr))])
        print(table)
        print("When you are ready to start pulling games call fetch()")
    def generate_csv(self, games):
        if not len(games):
            print("No games found")
            return
        keys = games[0].keys()
        if self.csv_name[-4:] != '.csv':
            self.csv_name += '.csv'
        with open(path.join(self.csv_directory, self.csv_name), "w", newline="") as f:
            w = csv.DictWriter(f, keys)
            w.writeheader()
            w.writerows(games)
    def fetch(self):
        players = self.fetch_players()
        start_date = self.start_date.split('/')
        start_date = datetime(int(start_date[0]), int(start_date[1]), 1)
        end_date = self.end_date.split('/')
        end_date = datetime(int(end_date[0]), int(end_date[1]), 1)
        games = []
        while start_date.year != end_date.year or start_date.month <= end_date.month:
            games += self.fetch_games(players, start_date.year, start_date.strftime('%m'))
            start_date += relativedelta(months=+1)
        self.generate_csv(games)
        print("CSV created at: {0}".format(path.join(self.csv_directory, self.csv_name)))
    def fetch_players(self):
        players = []
        job_done = False
        page = 1
        url = self.LB_URL + self.time_class + "?page="
        while not job_done:
            resp = requests.get(url + str(page))
            job_done = self.process_leaderboard(resp.json(), players)
            page += 1
        return players
    def process_leaderboard(self, data, players):
        for player in data['leaders']:
            if player['score'] < self.min_rating:
                return True
            players.append(player['user']['username'])
        return False
    def fetch_games(self, players, year, month):
        uuids={}
        games = []
        for count, player in enumerate(players, start=1):
            print("{0} {1}/{2}".format(player, count, len(players)))
            resp = get_player_games_by_month(player, year, month)
            for game in resp.games:
                self.process_game(uuids, player, games, game)
        return games
    def process_game(self, uuids, player, games, data):
        if (
            not data.rated or
            data.rules != 'chess' or
            data.time_control != self.time_control or
            data.uuid in uuids
        ):
            return
        uuids[data.uuid] = None
        opponent = data.white if data.white.username != player else data.black
        if opponent.rating < self.min_opponent:
            return
        game_result = 'draw'
        if data.white.result == 'win':
            game_result = 'white win'
        elif data.black.result == 'win':
            game_result = 'black win'
        game = {
            "date_endtime" : datetime.fromtimestamp(data.end_time).strftime("%m/%d/%Y %H:%M"),
            "time_class"   : data.time_class,
            "time_control" : data.time_control,
            "game_result"  : game_result,
            "rating_diff"  : data.white.rating - data.black.rating,
            "white_user"   : data.white.username,
            "white_rating" : data.white.rating,
            "white_result" : data.white.result,
            "black_user"   : data.black.username,
            "black_rating" : data.black.rating,
            "black_result" : data.black.result
        }
        games.append(game)