import csv
import json
import re
import requests
from datetime import datetime
from time import sleep
from os import getcwd, path
from dateutil.relativedelta import relativedelta
from prettytable import PrettyTable

class Obj():
    def __init__(self, dict):
        self.__dict__.update(dict)
    @staticmethod
    def resp2obj(resp):
        data = resp.json()
        return json.loads(json.dumps(data), object_hook=Obj)

class Fetcher():
    def __init__(
            self, min_rating=2800, min_opponent=2800, time_controls=['180'], leaderboard_time_class='blitz',
            start_date=datetime.now().strftime('%Y/%m'), end_date=datetime.now().strftime('%Y/%m'),
            csv_directory=getcwd(), csv_name=''
        ):
        self.LB_URL = "https://www.chess.com/callback/leaderboard/live/"
        self.API_URL = "https://api.chess.com/pub/"
        self.HEADERS = {"User-Agent":"email@address.here"}
        self.GROUP_TIME_CONTROLS = ['blitz','rapid','bullet','daily','titled_tuesday']
        self.SLEEP_DELAY = 0.5
        defaults = dict(zip(self.__init__.__code__.co_varnames[1:],self.__init__.__defaults__))
        self.__min_rating = defaults['min_rating']
        self.__min_opponent = defaults['min_opponent']
        self.__time_controls = defaults['time_controls']
        self.__time_controls_specific = defaults['time_controls']
        self.__time_controls_group = []
        self.__leaderboard_time_class = defaults['leaderboard_time_class']
        self.__start_date = defaults['start_date']
        self.__end_date = defaults['end_date']
        self.__csv_directory = defaults['csv_directory']
        self.__csv_name = defaults['csv_name']
        self.__csv_default = False
        self.__csv_inhouse = False
        params = locals()
        for p in params:
            if (
                p not in defaults or
                params[p] == defaults[p]
            ):
                continue
            setattr(self, p, params[p])
        if not self.csv_name:
            self.__csv_default = True
            self.default_csv_name()
        self.__check_exclude = [
            'csv_default', 'csv_inhouse', 'check_exclude', 'LB_URL', 'API_URL',
            'HEADERS', 'GROUP_TIME_CONTROLS', 'time_controls_specific',
            'time_controls_group', 'SLEEP_DELAY' ]
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
    def leaderboard_time_class(self):
        return self.__leaderboard_time_class
    @leaderboard_time_class.setter
    def leaderboard_time_class(self, new_value):
        if not isinstance(new_value, str):
            print("ERROR: leaderboard_time_class must be a string")
            return;
        new_value = new_value.lower()
        if new_value not in ['blitz', 'bullet', 'rapid', 'daily']:
            print("ERROR: leaderboard_time_class must be 'bullet', 'blitz', 'rapid' or 'daily'")
            return;
        self.__leaderboard_time_class = new_value
        self.__csv_inhouse = True
        self.default_csv_name()
    @property
    def time_controls(self):
        return self.__time_controls
    @time_controls.setter
    def time_controls(self, new_value):
        if isinstance(new_value, str):
            new_value = new_value.replace(" ", "").split(",")
        if not isinstance(new_value, list):
            print("ERROR: time_controls must be a string or a list.")
            return;
        for control in new_value:
            if control[-2:] == "+0":
                control = control[:-2]
            if control in self.GROUP_TIME_CONTROLS:
                self.__time_controls_group.append(control)
                continue
            self.__time_controls_specific.append(control)
        print("Make sure to define time_controls in seconds, e.g. 180 for 3+0 not {0} 3".format(self.bold('NOT')))
        self.__time_controls = new_value
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
    def default_csv_name(self):
        if not self.__csv_default:
            return
        csv_name = self.start_date.replace('/','') + "_"
        if self.end_date != self.start_date:
            csv_name += self.end_date.replace('/','') + "_"
        csv_name = "chesscomgames_minrating_{0}".format(self.min_rating)
        if self.min_opponent != self.min_rating:
            csv_name += "_minopprating_{0}".format(self.min_opponent)
        csv_name += '.csv'
        self.__csv_inhouse = True
        self.csv_name = csv_name
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
        print("CSV created at: {0}".format(path.join(self.csv_directory, self.csv_name)))
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
    def fetch_players(self):
        players = []
        job_done = False
        page = 1
        url = self.LB_URL + self.leaderboard_time_class + "?page="
        while not job_done:
            resp = Obj.resp2obj(requests.get(url + str(page)))
            job_done = self.process_leaderboard(resp, players)
            page += 1
        return players
    def process_leaderboard(self, data, players):
        for player in data.leaders:
            if player.score < self.min_rating:
                return True
            players.append(player.user.username)
        return False
    def fetch_games(self, players, year, month):
        uuids={}
        games = []
        request_time = 0
        for count, player in enumerate(players, start=1):
            print("{0} {1}/{2}".format(player, count, len(players)))
            url = (self.API_URL + "player/{0}/games/{1}/{2}".format(player, year, month)).lower()
            print(url)
            if request_time + self.SLEEP_DELAY > datetime.now().timestamp():
                print("Requests too fast, sleeping now.")
                sleep(self.SLEEP_DELAY)
            request_time = datetime.now().timestamp()
            resp = Obj.resp2obj(requests.get(url, headers=self.HEADERS))
            for game in resp.games:
                self.process_game(uuids, player, games, game)
        return games
    def process_game(self, uuids, player, games, data):
        if (
            not data.rated or
            data.rules != 'chess' or
            data.uuid in uuids
        ):
            return
        if (
            data.time_control not in self.__time_controls_specific and
            data.time_class not in self.__time_controls_group and
            not ("titled_tuesday" in self.__time_controls_group and
            hasattr(data, 'tournament') and "titled-tuesday" in data.tournament)
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