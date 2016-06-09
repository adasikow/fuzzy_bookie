import sys

from collections import OrderedDict

import fuzzy.storage.fcl.Reader


TEST_TEAM = 'Arsenal'
TEST_FCL = 'bookie_b.fcl'

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


def get_n_last_matches(team, season_start, season_end, n):
    result = []
    f = open(get_file_path(season_start, season_end))
    counter = 0
    for line in f:
        match_info = line.split()
        if len(match_info) == 5:
            home = match_info[0]
            away = match_info[1]
            if home == team:
                result.append((HOME, away))
                counter += 1
            elif away == team:
                result.append((AWAY, home))
                counter += 1

            if counter == n:
                break

    f.close()
    return result


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


def get_number_of_points_in_last_games(results_base, number_of_games, team, start, side=None):
    results = results_base[team]
    result = 0
    it = start
    i = 0
    while i < number_of_games:
        if side:
            try:
                while results[it][0] != side:
                    it += 1
            except IndexError:
                return result

        result += get_number_of_points(results[it])
        it += 1
        i += 1

    return result


def get_form_rating(results_base, team, start=0):
    last_5_games_coefficient = 3.0
    last_10_games_coefficient = 2.0
    last_15_games_coefficient = 1.0
    return get_number_of_points_in_last_games(results_base, 5, team, start) * last_5_games_coefficient / 15.0 + \
        get_number_of_points_in_last_games(results_base, 10, team, start) * last_10_games_coefficient / 30.0 + \
        get_number_of_points_in_last_games(results_base, 15, team, start) * last_15_games_coefficient / 45.0


def get_side_rating(results_base, team, side, start=0):
    last_10_games_coefficient = 3.0
    last_20_games_coefficient = 2.0
    last_30_games_coefficient = 1.0
    return get_number_of_points_in_last_games(results_base, 10, team, start, side=side) * last_10_games_coefficient / 30.0 + \
        get_number_of_points_in_last_games(results_base, 20, team, start, side=side) * last_20_games_coefficient / 60.0 + \
        get_number_of_points_in_last_games(results_base, 30, team, start, side=side) * last_30_games_coefficient / 90.0


def compare_teams(results_base, home, away, start=0):
    home_side_result_coefficient = 2.0
    away_side_result_coefficient = 1.0
    home_side_results = results_base[home][away][start:]
    away_side_results = results_base[away][home][start:]
    n = len(home_side_results)

    if n == 0: # no match history for these teams, so prob is unknown
        return 0.5

    home_team_points = 0.0
    away_team_points = 0.0
    for i in range(n):
        time_coefficient = float(n - i) / n

        if home_side_results[i][0] > home_side_results[i][1]:
            home_team_points += home_side_result_coefficient * 3.0 * time_coefficient
        elif home_side_results[i][0] < home_side_results[i][1]:
            away_team_points += home_side_result_coefficient * 3.0 * time_coefficient
        else:  # home_side_results[i][0] == home_side_results[i][1]
            home_team_points += home_side_result_coefficient * 1.0 * time_coefficient
            away_team_points += home_side_result_coefficient * 1.0 * time_coefficient

        if away_side_results[i][0] > away_side_results[i][1]:
            away_team_points += away_side_result_coefficient * 3.0 * time_coefficient
        elif away_side_results[i][0] < away_side_results[i][1]:
            home_team_points += away_side_result_coefficient * 3.0 * time_coefficient
        else:  # away_side_results[i][0] == away_side_results[i][1]
            home_team_points += away_side_result_coefficient * 1.0 * time_coefficient
            away_team_points += away_side_result_coefficient * 1.0 * time_coefficient

    return home_team_points / (home_team_points + away_team_points)


def fuzzy_bookie(home_team_form, away_team_form, home_side_advantage, away_side_advantage, home_team_win_probability):
    system = fuzzy.storage.fcl.Reader.Reader().load_from_file(TEST_FCL)

    my_input = {
        "Home_Team_Form": home_team_form,
        "Away_Team_Form": away_team_form,
        "Home_Side_Advantage": home_side_advantage,
        "Away_Side_Advantage": away_side_advantage,
        "Home_Team_Win_Probability": home_team_win_probability
    }

    my_output = {
        "Result": 1.0
    }

    system.calculate(my_input, my_output)

    return my_output["Result"]


def predict(results_base, recent_results, home_team, away_team, start_form=0, start_comp=0):
    fuzzy_result = fuzzy_bookie(
        get_form_rating(recent_results, home_team, start_form),
        get_form_rating(recent_results, away_team, start_form),
        get_side_rating(recent_results, home_team, HOME, start_form),
        get_side_rating(recent_results, away_team, AWAY, start_form),
        compare_teams(results_base, home_team, away_team, start_comp)
    )

    if fuzzy_result == 1.0:
        return 'home'
    elif fuzzy_result == 2.0:
        return 'away'
    elif fuzzy_result == 3.0:
        return 'draw'
    else:
        return 'fail'


def print_results(results, team):
    for result in results:
        if result[0] == HOME:
            print "{0} {1} : {2} {3}".format(team, result[2], result[3], result[1])
        else:  # if result[0] == AWAY
            print "{0} {1} : {2} {3}".format(result[1], result[2], result[3], team)


def match_result_to_str(match):
    if match[0] > match[1]:
        return 'home'
    elif match[0] < match[1]:
        return 'away'
    else:
        return 'draw'


def is_prediction_correct(results_base, home, away, prediction, i=0):
    if prediction == 'fail':
        print "Prediction failed, match: {0} - {1}".format(home, away)
        return 0

    result = match_result_to_str(results_base[home][away][i])
    if result == prediction:
        print "Prediction correct - {0}, match: {1} - {2}".format(prediction, home, away)
        return 1
    else:
        print "Prediction incorrect - {0}, result - {1},  match: {2} - {3}".format(prediction, result, home, away)
        return -1


def evaluate(results_base, recent_results, team, match_list):
    prediction_correct = 0
    prediction_incorrect = 0
    prediction_failure = 0

    while len(match_list) > 0:
        start = len(match_list)
        match = match_list.pop()
        side = match[0]
        opp = match[1]
        if side == HOME:
            home = team
            away = opp
        else:  # side == AWAY
            home = opp
            away = team

        prediction = predict(results_base, recent_results, home, away, start, 1)
        prediction_eval = is_prediction_correct(results_base, home, away, prediction)
        if prediction_eval == 1:
            prediction_correct += 1
        elif prediction_eval == -1:
            prediction_incorrect += 1
        else:  # if prediction_eval == 0
            prediction_failure += 1

    return prediction_correct, prediction_incorrect, prediction_failure


def percent(part, total):
    return 100.0 * (float(part) / float(total))


def test():

    if len(sys.argv) == 3:
        global TEST_TEAM
        TEST_TEAM = sys.argv[1]
        global TEST_FCL
        TEST_FCL = sys.argv[2]

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

    season_start = '14'
    season_end = '15'
    number_of_matches = 19

    team = TEST_TEAM
    match_list = get_n_last_matches(team, season_start, season_end, number_of_matches)

    test_result = evaluate(results_base, recent_results, team, match_list)

    print "Correct: {0} , Incorrect : {1}, Failure : {2}, Correctness: {3:.2f}%".\
        format(test_result[0], test_result[1], test_result[2], percent(test_result[0], number_of_matches))
    # print predict(results_base, recent_results, 'Arsenal', 'Chelsea')


# TEST POPRAWIONY - PRZEWIDYWANIE WYNIKOW SPOTKAN 2. POLOWY SEZONU 13/14 NA PODSTAWIE DANYCH Z SEZONOW 09-10 - 13-14
def test_fixed_after_presentation():

    if len(sys.argv) == 3:
        global TEST_TEAM
        TEST_TEAM = sys.argv[1]
        global TEST_FCL
        TEST_FCL = sys.argv[2]

    results_base = {}
    get_results_history(results_base, '13', '14')
    get_results_history(results_base, '12', '13')
    get_results_history(results_base, '11', '12')
    get_results_history(results_base, '10', '11')
    get_results_history(results_base, '09', '10')

    recent_results = {}
    get_latest_results(recent_results, '13', '14')
    get_latest_results(recent_results, '12', '13')
    get_latest_results(recent_results, '11', '12')
    get_latest_results(recent_results, '10', '11')
    get_latest_results(recent_results, '09', '10')

    season_start = '13'
    season_end = '14'
    number_of_matches = 19

    team = TEST_TEAM
    match_list = get_n_last_matches(team, season_start, season_end, number_of_matches)

    test_result = evaluate(results_base, recent_results, team, match_list)

    print "Correct: {0} , Incorrect : {1}, Failure : {2}, Correctness: {3:.2f}%".\
        format(test_result[0], test_result[1], test_result[2], percent(test_result[0], number_of_matches))
    # print predict(results_base, recent_results, 'Arsenal', 'Chelsea')


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

    if len(sys.argv) == 2:
        global TEST_FCL
        TEST_FCL = sys.argv[1]

    home = raw_input("Podaj druzyne gManospodarzy: ")
    away = raw_input("Podaj druzyne gosci: ")

    result = predict(results_base, recent_results, home, away)

    if result == 'home':
        print "Wygra druzyna gospodarzy"
    elif result == 'away':
        print "Wygra druzyna gosci"
    elif result == 'draw':
        print "Mecz zakonczy sie remisem"
    else:
        print "Nie udalo sie przewidziec wyniku"


if __name__ == "__main__":
    #main()
    test_fixed_after_presentation()
