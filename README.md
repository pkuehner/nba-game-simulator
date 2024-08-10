# Text-Based NBA Simulator
This Simulator that can Simulate a game based on real play by play data and outputs at as Text to the Command Line

## Data
It parses official NBA Data (from 2019 season but technically others are possible) and accumulates stats for each possible lineup a team ran. From this data it creates probabilities for possession outcomes depending on the lineup both for defense and offense.

## Simulation
During simulation it just runs through 225 possessions and randomly simulates the outcome of the possesion.

## Usage
Install requirements
Download and parse the data -> `./download.sh`
Simulate a game -> `python -m analyze.re_simulate_game <HOME_TEAM_ABBREVIATION> <AWAY_TEAM_ABBREVIATIOn>`

## Example:
python -m analyze.re_simulate_game BOS PHI

```
....
2pta by: away
Shot made
{'home': 97, 'away': 109}
home exchanged to Lineup: 40
{'id': 1629057, 'full_name': 'Robert Williams III', 'first_name': 'Robert', 'last_name': 'Williams III', 'is_active': True}
{'id': 202689, 'full_name': 'Kemba Walker', 'first_name': 'Kemba', 'last_name': 'Walker', 'is_active': False}
{'id': 203935, 'full_name': 'Marcus Smart', 'first_name': 'Marcus', 'last_name': 'Smart', 'is_active': True}
{'id': 202330, 'full_name': 'Gordon Hayward', 'first_name': 'Gordon', 'last_name': 'Hayward', 'is_active': True}
{'id': 1628369, 'full_name': 'Jayson Tatum', 'first_name': 'Jayson', 'last_name': 'Tatum', 'is_active': True}
3pta by: home
Defensive Rebound by: away
2pta by: away
Shot made
{'home': 97, 'away': 111}
3pta by: home
Offensive Rebound by: home
2pta by: home
Shot made
{'home': 99, 'away': 111}
fta by: away
Shot made
{'home': 99, 'away': 112}
home exchanged to Lineup: 28
{'id': 202330, 'full_name': 'Gordon Hayward', 'first_name': 'Gordon', 'last_name': 'Hayward', 'is_active': True}
{'id': 202689, 'full_name': 'Kemba Walker', 'first_name': 'Kemba', 'last_name': 'Walker', 'is_active': False}
{'id': 203935, 'full_name': 'Marcus Smart', 'first_name': 'Marcus', 'last_name': 'Smart', 'is_active': True}
{'id': 1628369, 'full_name': 'Jayson Tatum', 'first_name': 'Jayson', 'last_name': 'Tatum', 'is_active': True}
{'id': 1628464, 'full_name': 'Daniel Theis', 'first_name': 'Daniel', 'last_name': 'Theis', 'is_active': True}
3pta by: home
Shot made
{'home': 102, 'away': 112}
2pta by: away
Shot made
{'home': 102, 'away': 114}
3pta by: home
Offensive Rebound by: home
Turnover by home
-----
Q4 End {'home': 102, 'away': 114}
-----
```
