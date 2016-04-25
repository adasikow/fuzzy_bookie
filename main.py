from collections import OrderedDict
import fuzzy.storage.fcl.Reader


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


def team_won(match):
    return (match[0] == HOME and match[2] > match[3]) or (match[0] == AWAY and match[2] < match[3])


def team_lost(match):
    return (match[0] == HOME and match[2] < match[3]) or (match[0] == AWAY and match[2] > match[3])


def get_number_of_points(match):
    if team_won(match):
        return 3
    elif team_lost(match):
        return 0
    else:  #team drew:
        return 1


def get_number_of_points_in_last_games(results_base, number_of_games, team, side=None):
    results = results_base[team]
    result = 0
    it = 0
    i = 0
    while i < number_of_games:
        if side:
            while results[it][0] != side:
                it += 1

        result += get_number_of_points(results[it])
        it += 1
        i += 1

    return result


def get_form_rating(results_base, team):
    last_5_games_coefficient = 3.0
    last_10_games_coefficient = 2.0
    last_15_games_coefficient = 1.0
    return get_number_of_points_in_last_games(results_base, 5, team) * last_5_games_coefficient / 15.0 + \
        get_number_of_points_in_last_games(results_base, 10, team) * last_10_games_coefficient / 30.0 + \
        get_number_of_points_in_last_games(results_base, 15, team) * last_15_games_coefficient / 45.0


def get_side_rating(results_base, team, side):
    last_10_games_coefficient = 3.0
    last_20_games_coefficient = 2.0
    last_30_games_coefficient = 1.0
    return get_number_of_points_in_last_games(results_base, 10, team, side=side) * last_10_games_coefficient / 30.0 + \
        get_number_of_points_in_last_games(results_base, 20, team, side=side) * last_20_games_coefficient / 60.0 + \
        get_number_of_points_in_last_games(results_base, 30, team, side=side) * last_30_games_coefficient / 90.0


def main():
    results_base = {}
    get_results_history(results_base, '14', '15')
    get_results_history(results_base, '13', '14')
    get_results_history(results_base, '12', '13')
    get_results_history(results_base, '11', '12')
    get_results_history(results_base, '10', '11')

    recent_results = {}
    get_latest_results(recent_results, '14', '15')
    get_latest_results(recent_results, '13', '14')
    get_latest_results(recent_results, '12', '13')
    get_latest_results(recent_results, '11', '12')
    get_latest_results(recent_results, '10', '11')

    # for home in results_base.keys():
    #     for away in results_base[home].keys():
    #         for result in results_base[home][away]:
    #             print "{0} {1} : {2} {3}".format(home, result[0], result[1], away)
    #
    # for team in recent_results.keys():
    #     for result in recent_results[team]:
    #         if result[0] == HOME:
    #             print "{0} {1} : {2} {3}".format(team, result[2], result[3], result[1])
    #         else:  # if result[0] == AWAY
    #             print "{0} {1} : {2} {3}".format(result[1], result[2], result[3], team)

    team1 = 'Arsenal'
    team2 = 'ManchesterUtd'

    for result in recent_results[team1]:
        if result[0] == HOME:
            print "{0} {1} : {2} {3}".format(team1, result[2], result[3], result[1])
        else:  # if result[0] == AWAY
            print "{0} {1} : {2} {3}".format(result[1], result[2], result[3], team1)

    # for result in results_base[team1][team2]:
    #     print "{0} {1} : {2} {3}".format(team1, result[0], result[1], team2)
    #
    # for result in results_base[team2][team1]:
    #     print "{0} {1} : {2} {3}".format(team2, result[0], result[1], team1)

    print get_number_of_points_in_last_games(recent_results, 5, team1)
    print get_number_of_points_in_last_games(recent_results, 10, team1)
    print get_number_of_points_in_last_games(recent_results, 15, team1)
    print get_number_of_points_in_last_games(recent_results, 5, team1, side=HOME)
    print get_number_of_points_in_last_games(recent_results, 10, team1, side=HOME)
    print get_number_of_points_in_last_games(recent_results, 15, team1, side=HOME)
    print get_number_of_points_in_last_games(recent_results, 5, team1, side=AWAY)
    print get_number_of_points_in_last_games(recent_results, 10, team1, side=AWAY)
    print get_number_of_points_in_last_games(recent_results, 15, team1, side=AWAY)
    print team1 + ':'
    print get_form_rating(recent_results, team1)
    print get_side_rating(recent_results, team1, HOME)
    print get_side_rating(recent_results, team1, AWAY)
    print team2 + ':'
    print get_form_rating(recent_results, team2)
    print get_side_rating(recent_results, team2, HOME)
    print get_side_rating(recent_results, team2, AWAY)

    for result in recent_results[team2]:
        if result[0] == AWAY:
            print "{0} {1} : {2} {3}".format(result[1], result[2], result[3], team2)


def fuzzy_example():
    system = fuzzy.storage.fcl.Reader.Reader().load_from_file("example.fcl")

    my_input = {
        "Our_Health": 100.0,
        "Enemy_Health": 50.0
    }

    my_output = {
        "Aggressiveness": 0.0
    }

    system.calculate(my_input, my_output)

    print "Fuzzy example result: " + str(my_output["Aggressiveness"])


if __name__ == "__main__":
    main()
    fuzzy_example()

