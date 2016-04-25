from collections import OrderedDict


HOME = 'h'
AWAY = 'a'


def get_file_path(season_start, season_end):
    league_prefix = 'premierleague'
    extension = '.txt'
    filename = league_prefix + season_start + season_end
    return league_prefix + '\\' + filename + extension


def get_latest_results(result_base, season_start, season_end):
    f = open(get_file_path(season_start, season_end))
    for line in f:
        match_info = line.split()
        if len(match_info) == 5:
            home = match_info[0]
            away = match_info[1]
            home_goals = int(match_info[2])
            away_goals = int(match_info[4])

            if home not in result_base:
                result_base[home] = []

            if away not in result_base:
                result_base[away] = []

            result_base[home].append((HOME, away, home_goals, away_goals))
            result_base[away].append((AWAY, home, home_goals, away_goals))

    f.close()


def get_results_history(results_base, season_start, season_end):
    f = open(get_file_path(season_start, season_end))
    for line in f:
        match_info = line.split()
        if len(match_info) == 5:
            home = match_info[0]
            away = match_info[1]
            home_goals = int(match_info[2])
            away_goals = int(match_info[4])

            if home not in results_base:
                results_base[home] = OrderedDict()

            if away not in results_base[home]:
                results_base[home][away] = []

            results_base[home][away].append((home_goals, away_goals))

    f.close()


def main():
    results_base = {}
    get_results_history(results_base, '14', '15')
    get_results_history(results_base, '13', '14')
    get_results_history(results_base, '12', '13')
    get_results_history(results_base, '11', '12')
    get_results_history(results_base, '10', '11')

    recent_form = {}
    get_latest_results(recent_form, '14', '15')
    get_latest_results(recent_form, '13', '14')
    get_latest_results(recent_form, '12', '13')
    get_latest_results(recent_form, '11', '12')
    get_latest_results(recent_form, '10', '11')

    for home in results_base.keys():
        for away in results_base[home].keys():
            for result in results_base[home][away]:
                print "{0} {1} : {2} {3}".format(home, result[0], result[1], away)

    for team in recent_form.keys():
        for result in recent_form[team]:
            if result[0] == HOME:
                print "{0} {1} : {2} {3}".format(team, result[2], result[3], result[1])
            else:  # if result[0] == AWAY
                print "{0} {1} : {2} {3}".format(result[1], result[2], result[3], team)

    team1 = 'Arsenal'
    team2 = 'ManchesterUtd'

    for result in recent_form[team1]:
        if result[0] == HOME:
            print "{0} {1} : {2} {3}".format(team1, result[2], result[3], result[1])
        else:  # if result[0] == AWAY
            print "{0} {1} : {2} {3}".format(result[1], result[2], result[3], team1)

    for result in results_base[team1][team2]:
        print "{0} {1} : {2} {3}".format(team1, result[0], result[1], team2)

    for result in results_base[team2][team1]:
        print "{0} {1} : {2} {3}".format(team2, result[0], result[1], team1)


if __name__ == "__main__":
    main()
