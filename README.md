# chesscom game fetcher

This module will fetch all the games played at a specified time control for a specified period from all players rated above a defined rating and then compile them into a CSV file. This is quite a specialised use case. If you wish to instead download the games of an specific player you can, but you may be better served by my online tool for this use case, [Let's Do The Procedure](https://letsdotheprocedure.com/).

## Getting Started

### Installation
`pip install chesscom-game-fetcher`

### Basic Usage
The module relies upon the `Fetcher` class, which uses its attributes to determine which games to fetch when its `fetch()` method is called.
```
from chesscom_game_fetcher import Fetcher
fetcher = Fetcher()
fetcher.fetch()
## Default settings will fetch all 3+0 games from the current
## month played between those rated 2800 and above.
```
Attributes can be set both during `Fetcher` initialisation on the instance itself. Check which settings your `Fetcher` instance will be using at any time by calling the `check` attribute.
```
from chesscom_game_fetcher import Fetcher
fetcher = Fetcher(min_rating=3000, min_opponent=3000)
fetcher.time_control = '180+1'

## This will print a table of the instance's fetch settings.
fetcher.check

## This will now fetch all 3+1 games from the current month
## played between those rated 3000 and above.
fetcher.fetch()
```
### Specialised Usage
The individual methods `Fetcher.fetch()` calls can, if you wish, be used manually.
This is how you fetch games from specific players.
#### Fetch Players
`Fetcher.fetch_players()`
returns a list of all those rated above `Fetcher.min_rating`
#### Fetch Games
`Fetcher.fetch_games(player_list, year, 'month')`
- `player_list` : a list of player names.
- `year`        : year to search for games in. `YYYY` format.
- `month`       : two digit string for the month to search for games in. `'MM'` format.

```
fetcher = Fetcher(min_rating=3000, min_opponent=3000)
player_list = fetcher.fetch_players()
games_list = fetcher.fetch_games(player_list, 2024, '04')
## games_list will contain all games played between
## those rated 3000 minimum in april 2024
```
#### Create CSV
`Fetcher.generate_csv(games_list)`
Outputs a CSV file using a games_list created by `Fetcher.fetch_games`.

`Fetcher.csv_directory` and `Fetcher.csv_name` are used to create the file.

### Attribute Reference Table
| Attribute     | Default                                                  | Type | Description                                                                                                                                                                                                               |
|---------------|----------------------------------------------------------|------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| min_rating    | 2800                                                     | int  | Players will be pulled from the leaderboard for this `time_class` until a player with a rating below `min_rating` is found.                                                                                               |
| min_opponent  | 2800                                                     | int  | Any games with an opponent rated below `min_opponent` will be discarded.                                                                                                                                                  |
| time_control  | '180'                                                    | str  | Games without this time control will be discarded. `time_control` is set by total seconds for each player (+ increment in seconds if used). For example `180` will select 3+0 games whilst `180+1` will select 3+1 games. |
| time_class    | 'blitz'                                                  | str  | Must be one of: `daily`, `rapid`, `blitz` or `bullet`                                                                                                                                                                     |
| start_date    | '{ current year (4 digit) }/{ current month (2 digit) }' | str  | Games will be pulled starting from this month. Format: `YYYY/MM`.                                                                                                                                                         |
| end_date      | '{ current year (4 digit) }/{ current month (2 digit) }' | str  | Games will stop being pulled *after* this month. Format: `YYYY/MM`.                                                                                                                                                       |
| csv_directory | '{ current terminal directory }'          | str  | Directory for the CSV file. By default it will be placed in the directory your terminal is using.                                                                                                                         |
| csv_name      | auto-generated if not provided                      | str  | Name for the CSV file. Default format is: `'{ time_class }_min{ min_rating }_minopp{ min_opponent }_{ start_date }_{ end_date }.csv'`    

### CSV File Output
By default this will go wherever your terminal was pointing when python was started with a file name automatically generated by the `Fetcher` instance itself. Change these with the `csv_directory` and `csv_name` attributes respectively.

The field names given to the CSV are:
`date_endtime, time_class, time_control, game_result, rating_diff, white_user, white_rating,	white_result,	black_user,	black_rating,	black_result`

### Author
Package developed by Scott Oxtoby. Emails to: `pypi@oxtoby.uk`.