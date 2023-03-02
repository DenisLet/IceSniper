from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from functools import reduce
from time import sleep

from send import bet_siska




def check_link(url,time,score_one,score_two,period,minute,checker):
    try:
        print("STARTING")
        caps = DesiredCapabilities().CHROME
        caps["pageLoadStrategy"] = "eager"
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        browser = webdriver.Chrome(desired_capabilities=caps,options=options)
        browser.get(url)
        browser.implicitly_wait(1)
        sleep(2)
        team_home = browser.find_elements(By.CSS_SELECTOR, "a.participant__participantName")[0].get_attribute(
            "href") + "/results/"
        team_away = browser.find_elements(By.CSS_SELECTOR, "a.participant__participantName")[1].get_attribute(
            "href") + "/results/"
        title = browser.find_element(By.CSS_SELECTOR, ".tournamentHeader__country").text
        print("WORKING")
        try:
            first_period_data = browser.find_element(By.CSS_SELECTOR, "div.smv__incidentsHeader:nth-child(1)").text
            total_1period = sum(int(i) for i in first_period_data[2:] if i.isdigit())
            goal_time = browser.find_elements(By.CSS_SELECTOR, "div.smv__verticalSections.section")
            for kino in goal_time:
                stroka = kino.text.split()
                if "2ND" in stroka:
                    period2 = stroka.index("2ND")
                    total_2period = sum(int(i) for i in stroka[period2 + 2:period2 + 5] if i.isdigit())
                else:
                    total_2period = 0
        except Exception:
                print("Problems in period scoring calculation...")
                first_period_data = "No"
                total_1period = "No"
                total_2period =0

        def separator(matches):
            match_list = list()
            for i in matches:
                line = i.text
                #  print(line)
                if "(" in line or "Awrd" in line or "Abn" in line:
                    continue
                if len([i for i in line.split() if i.isdigit()]) < 6:
                    continue
                match_list.append(line.split())
            return match_list

        def forming(browser, link1, link2):  # NEED ADD TYPE SPORT AND FIXABLE CSS SELECTOR
            browser.get(link1)
            # browser.execute_script("arguments[0].click();", WebDriverWait(browser, 20).until(
            #     EC.element_to_be_clickable((By.CSS_SELECTOR, "a.event__more.event__more--static"))))
            # time.sleep(3)
            team1 = browser.find_element(By.CSS_SELECTOR, "div.heading__name").get_attribute("innerHTML")
            matches = browser.find_elements(By.CSS_SELECTOR, "[id^='g_4']")
            match_list_home = separator(matches)
            browser.get(link2)
            # browser.execute_script("arguments[0].click();", WebDriverWait(browser, 20).until(
            #     EC.element_to_be_clickable((By.CSS_SELECTOR, "a.event__more.event__more--static"))))
            # time.sleep(3)
            team2 = browser.find_element(By.CSS_SELECTOR, "div.heading__name").get_attribute("innerHTML")
            matches = browser.find_elements(By.CSS_SELECTOR, "[id^='g_4']")
            match_list_away = separator(matches)
            return match_list_home, match_list_away, team1, team2

        games = forming(browser, team_home, team_away)

        home_team_name, away_team_name = games[2].split(), games[3].split()

        print(home_team_name, away_team_name)

        def separation_home_away(team_, all_matches):
            home_matches = list()
            away_matches = list()
            waste = ["W", "U18", "U20", "U21", "U23"]  # WASTE - U20 and another juniors and woman champs//
            for i in waste:
                if i in team_:
                    team_ = [j for j in team_ if j not in waste]

            for k in all_matches:
                i = [j for j in k[:len(k) - 1] if j not in waste] + k[-1:]

                x = i.index(team_[len(team_) - 1])
                # print(team_[len(team_)-1])
                # print(x)
                if i[x + 1].isdigit():
                    away_matches.append(i)
                elif "(" in i[x + 1] and i[x + 2].isdigit():
                    away_matches.append(i)
                else:
                    home_matches.append(i)
            return home_matches, away_matches

        team1_home, team1_away = separation_home_away(home_team_name, games[0])  # 1 team home / away matches
        team2_home, team2_away = separation_home_away(away_team_name, games[1])  # 2 team home / away matches
        team1_nosep = games[0]
        team2_nosep = games[1]

        def filth_count(matches, period):
            if period == "first":
                x, y = 2, 3
            if period == "second":
                x, y = 4, 5
            if period == "third":
                x, y = 6, 7
            goals_scored = []
            for i in matches:
                if 'Pen' in i:
                    scores = i[-13:-1]
                elif "AOT" in i:
                    scores = i[-11:-1]
                else:
                    scores = i[-9:-1]
                goals_scored.append(int(scores[x]) + int(scores[y]))
            return goals_scored

        res1_t1 = filth_count(team1_nosep, period='first')
        res2_t1 = filth_count(team1_nosep, period='second')
        res3_t1 = filth_count(team1_nosep, period="third")
        res1_t2 = filth_count(team2_nosep, period='first')
        res2_t2 = filth_count(team2_nosep, period='second')
        res3_t2 = filth_count(team2_nosep, period="third")
        dataset = [j for i in zip(res1_t1, res2_t1, res3_t1) for j in reversed(i)]  # home team data
        dataset2 = [j for i in zip(res1_t2, res2_t2, res3_t2) for j in reversed(i)]
        print(dataset)
        print(len(dataset))
        print(len(dataset2))
        gg = dataset[::-1]
        gg2 = dataset2[::-1]
        last_3p_t1 = gg[-1]
        last_3p_t2 = gg2[-1]
        last_2p_t1 = gg[-2]
        last_2p_t2 = gg2[-2]

        def count_zero(games):
            contrlist = []
            for i, j in enumerate(games):
                if j == 0:
                    contrlist.append(i)
            afters = 0
            for i in contrlist:
                if i == len(games) - 1:
                    msg = "LAST PLAYED PERIOD IS NULL"
                    break
                if games[i + 1] == 0:
                    afters += 1
            percent = round((1 - afters / len(contrlist)) * 100, 1)
            return afters, percent, len(contrlist)

        a, p, l = count_zero(gg)
        a1, p1, l1 = count_zero(gg2)
        print(a, p, l, sep="---")
        print(a1, p1, l1, sep="---")

        last9_t1 = dataset[:9].count(0)
        last9_t2 = dataset2[:9].count(0)
        print(dataset[:9])
        print(dataset2[:9])
        print(last9_t1)
        print(last9_t2)
        last0_t1 = dataset[3:12].count(0)
        last0_t2 = dataset2[3:12].count(0)
        print(dataset[3:12])
        print(dataset2[3:12])
        print("ZERO IN LAST 3 GAMES:: ", last0_t1)
        print("ZERO IN LAST 3 GAMES:: ", last0_t2)

        all_seq_team1 = round((1 - l / len(dataset)) * 100, 1)
        all_seq_team2 = round((1 - l1 / len(dataset2)) * 100, 1)
        print("AVE PERIOD 1T:: ", all_seq_team1, f'{l}/{len(dataset)}')
        print("AVE PERIOD 2T:: ", all_seq_team2, f'{l1}/{len(dataset2)}')







        info = f"{a}/{l} ({p}%) *{len(dataset)}* <-> {a1}/{l1} ({p1}%) *{len(dataset2)}*"

        def results(matches, loc, period):
            if period == "first":
                x, y = 2, 3
            if period == "second":
                x, y = 4, 5
            if period == "third":
                x, y = 6, 7
            team_scored = []
            team_conceded = []
            if loc == "home":
                scored, conceded = x, y
            else:
                scored, conceded = y, x
            for i in matches:

                if 'Pen' in i:
                    scores = i[-13:-1]
                elif "AOT" in i:
                    scores = i[-11:-1]
                else:
                    scores = i[-9:-1]
                # print(scores)
                team_scored.append(int(scores[scored]))
                team_conceded.append(int(scores[conceded]))
            return team_scored, team_conceded

        try:
            ''' 1st period results individual '''

            team1_scored_1p_home, team1_conceded_1p_home = results(team1_home, loc="home", period="first")
            team1_scored_1p_away, team1_conceded_1p_away = results(team1_away, loc="away", period="first")
            team2_scored_1p_home, team2_conceded_1p_home = results(team2_home, loc="home", period="first")
            team2_scored_1p_away, team2_conceded_1p_away = results(team2_away, loc="away", period="first")

            '''2nd period results individual'''

            team1_scored_2p_home, team1_conceded_2p_home = results(team1_home, loc="home", period="second")
            team1_scored_2p_away, team1_conceded_2p_away = results(team1_away, loc="away", period="second")
            team2_scored_2p_home, team2_conceded_2p_home = results(team2_home, loc="home", period="second")
            team2_scored_2p_away, team2_conceded_2p_away = results(team2_away, loc="away", period="second")

            '''3rd period results individual'''

            team1_scored_3p_home, team1_conceded_3p_home = results(team1_home, loc="home", period="third")
            team1_scored_3p_away, team1_conceded_3p_away = results(team1_away, loc="away", period="third")
            team2_scored_3p_home, team2_conceded_3p_home = results(team2_home, loc="home", period="third")
            team2_scored_3p_away, team2_conceded_3p_away = results(team2_away, loc="away", period="third")

            '''Fulltime results individual'''

            def fulltime(period1, period2, period3):
                return [int(x) + int(y) + int(z) for x, y, z in zip(period1, period2, period3)]

            team1_scored_ft_home = fulltime(team1_scored_1p_home, team1_scored_2p_home, team1_scored_3p_home)
            team1_scored_ft_away = fulltime(team1_scored_1p_away, team1_scored_2p_away, team1_scored_3p_away)
            team1_conceded_ft_home = fulltime(team1_conceded_1p_home, team1_conceded_2p_home, team1_conceded_3p_home)
            team1_conceded_ft_away = fulltime(team1_conceded_1p_away, team1_conceded_2p_away, team1_conceded_3p_away)
            team2_scored_ft_home = fulltime(team2_scored_1p_home, team2_scored_2p_home, team2_scored_3p_home)
            team2_scored_ft_away = fulltime(team2_scored_1p_away, team2_scored_2p_away, team2_scored_3p_away)
            team2_conceded_ft_home = fulltime(team2_conceded_1p_home, team2_conceded_2p_home, team2_conceded_3p_home)
            team2_conceded_ft_away = fulltime(team2_conceded_1p_away, team2_conceded_2p_away, team2_conceded_3p_away)

            '''Fulltime results common'''

            team1_common_ft_home = [x + y for x, y in zip(team1_scored_ft_home, team1_conceded_ft_home)]
            team1_common_ft_away = [x + y for x, y in zip(team1_scored_ft_away, team1_conceded_ft_away)]
            team2_common_ft_home = [x + y for x, y in zip(team2_scored_ft_home, team2_conceded_ft_home)]
            team2_common_ft_away = [x + y for x, y in zip(team2_scored_ft_away, team2_conceded_ft_away)]

            '''1st period common result'''

            team1_common_1p_home = [x + y for x, y in zip(team1_scored_1p_home, team1_conceded_1p_home)]
            team1_common_1p_away = [x + y for x, y in zip(team1_scored_1p_away, team1_conceded_1p_away)]
            team2_common_1p_home = [x + y for x, y in zip(team2_scored_1p_home, team2_conceded_1p_home)]
            team2_common_1p_away = [x + y for x, y in zip(team2_scored_1p_away, team2_conceded_1p_away)]

            '''2nd period common result'''

            team1_common_2p_home = [x + y for x, y in zip(team1_scored_2p_home, team1_conceded_2p_home)]
            team1_common_2p_away = [x + y for x, y in zip(team1_scored_2p_away, team1_conceded_2p_away)]
            team2_common_2p_home = [x + y for x, y in zip(team2_scored_2p_home, team2_conceded_2p_home)]
            team2_common_2p_away = [x + y for x, y in zip(team2_scored_2p_away, team2_conceded_2p_away)]

            '''3rd period common result'''

            team1_common_3p_home = [x + y for x, y in zip(team1_scored_3p_home, team1_conceded_3p_home)]
            team1_common_3p_away = [x + y for x, y in zip(team1_scored_3p_away, team1_conceded_3p_away)]
            team2_common_3p_home = [x + y for x, y in zip(team2_scored_3p_home, team2_conceded_3p_home)]
            team2_common_3p_away = [x + y for x, y in zip(team2_scored_3p_away, team2_conceded_3p_away)]

            """1-2 peroidos indiv calc"""

            team1_scored_12_home = [x + y for x, y in zip(team1_scored_1p_home, team1_scored_2p_home)]
            team1_scored_12_away = [x + y for x, y in zip(team1_scored_1p_away, team1_scored_2p_away)]
            team1_conceded_12_home = [x + y for x, y in zip(team1_conceded_1p_home, team1_conceded_2p_home)]
            team1_conceded_12_away = [x + y for x, y in zip(team1_conceded_1p_away, team1_conceded_2p_away)]
            team2_scored_12_home = [x + y for x, y in zip(team2_scored_1p_home, team2_scored_2p_home)]
            team2_scored_12_away = [x + y for x, y in zip(team2_scored_1p_away, team2_scored_2p_away)]
            team2_conceded_12_home = [x + y for x, y in zip(team2_conceded_1p_home, team2_conceded_2p_home)]
            team2_conceded_12_away = [x + y for x, y in zip(team2_conceded_1p_away, team2_conceded_2p_away)]

            '''1-2 periods common results'''

            team1_common_12_home = [x + y for x, y in zip(team1_scored_12_home, team1_conceded_12_home)]
            team1_common_12_away = [x + y for x, y in zip(team1_scored_12_away, team1_conceded_12_away)]
            team2_common_12_home = [x + y for x, y in zip(team2_scored_12_home, team2_conceded_12_home)]
            team2_common_12_away = [x + y for x, y in zip(team2_scored_12_away, team2_conceded_12_away)]

            '''Total calculation'''






            def calc(list):
                matches = 0
                zero, one, two, three, four, more = 0, 0, 0, 0, 0, 0
                for i in list:
                    matches += 1
                    if int(i) == 0:
                        zero += 1
                    elif int(i) == 1:
                        one += 1
                    elif int(i) == 2:
                        two += 1
                    elif int(i) == 3:
                        three += 1
                    elif int(i) == 4:
                        four += 1
                    else:
                        more += 1
                return zero, one, two, three, four, more, matches


            score1, score2 = calc(team1_common_1p_home)[0], calc(team1_common_1p_away)[0]
            score3, score4 = calc(team2_common_1p_home)[0], calc(team2_common_1p_away)[0]

            score5, score6 = calc(team1_common_2p_home)[0], calc(team1_common_2p_away)[0]
            score7, score8 = calc(team2_common_2p_home)[0], calc(team2_common_2p_away)[0]

            score9 ,score10 = calc(team1_common_3p_home)[0], calc(team1_common_3p_away)[0]
            score11,score12 = calc(team2_common_3p_home)[0], calc(team2_common_3p_away)[0]

            nice = [0, 1]

            '''Printer'''


            print("<<<<<    FULLTIME   >>>>>")
            print("SCORED   FULLTIME  HOME: ", team1_scored_ft_home, calc(team1_scored_ft_home))
            if calc(team1_scored_ft_home)[0] == 0:
                print("$$$")
            print("CONCEDED FULLTIME  HOME: ", team1_conceded_ft_home, calc(team1_conceded_ft_home))
            if calc(team1_conceded_ft_home)[0] == 0:
                print("$$$")
            print("SCORED   FULLTIME  AWAY: ", team1_scored_ft_away, calc(team1_scored_ft_away))
            if calc(team1_scored_ft_away)[0] == 0:
                print("$$$")
            print("CONCEDED FULLTIME  AWAY: ", team1_conceded_ft_away, calc(team1_conceded_ft_away))
            if calc(team1_conceded_ft_away)[0] == 0:
                print("$$$")
            print("SCORED    COMMON   HOME: ", team1_common_ft_home, calc(team1_common_ft_home))
            if calc(team1_common_ft_home)[0] == 0:
                print("$$$")
            print("SCORED    COMMON   AWAY: ", team1_common_ft_away, calc(team1_common_ft_away))
            if calc(team1_common_ft_away)[0] == 0:
                print("$$$")
            print("*" * 40)
            print("<<<<<AWAY TEAM RESULTS>>>>>", away_team_name)

            print("<<<<<    FULLTIME   >>>>>")
            print("SCORED   FULLTIME  HOME: ", team2_scored_ft_home, calc(team2_scored_ft_home))
            if calc(team2_scored_ft_home)[0] == 0:
                print("$$$")
            print("CONCEDED FULLTIME  HOME: ", team2_conceded_ft_home, calc(team2_conceded_ft_home))
            if calc(team2_conceded_ft_home)[0] == 0:
                print("$$$")
            print("SCORED   FULLTIME  AWAY: ", team2_scored_ft_away, calc(team2_scored_ft_away))
            if calc(team2_scored_ft_away)[0] == 0:
                print("$$$")
            print("CONCEDED FULLTIME  AWAY: ", team2_conceded_ft_away, calc(team2_conceded_ft_away))
            if calc(team2_conceded_ft_away)[0] == 0:
                print("$$$")
            print("SCORED    COMMON   HOME: ", team2_common_ft_home, calc(team2_common_ft_home))
            if calc(team2_common_ft_home)[0] == 0:
                print("$$$")
            print("SCORED    COMMON   AWAY: ", team2_common_ft_away, calc(team2_common_ft_away))
            if calc(team2_common_ft_away)[0] == 0:
                print("$$$")


            """    FORMING TO SEND MESSAGE   """
            current_score = f"{score_one}:{score_two}"


            if period == 1 and checker == 1:
                print("FIRST PERIOD WILL BE SCANNED")
                print("<<<<<HOME TEAM RESULTS>>>>>", home_team_name)
                print("<<<<<    1ST PERIOD   >>>>>")
                print("1ST PERIOD SCORED  HOME: ",team1_scored_1p_home,calc(team1_scored_1p_home))
                print("1ST PERIOD CONCED. HOME: ",team1_conceded_1p_home,calc(team1_conceded_1p_home))
                print("1ST PERIOD SCORED  AWAY: ",team1_scored_1p_away,calc(team1_scored_1p_away))
                print("1ST PERIOD CONCED. AWAY: ",team1_conceded_1p_away,calc(team1_conceded_1p_away))
                print("1ST PERIOD COMMON HOME : ",team1_common_1p_home,calc(team1_common_1p_home))
                print("1ST PERIOD COMMON AWAY : ",team1_common_1p_away,calc(team1_common_1p_away))
                print()
                print("<<<<<AWAY TEAM RESULTS>>>>>")
                print("<<<<<    1ST PERIOD   >>>>>")
                print("1ST PERIOD SCORED  HOME: ", team2_scored_1p_home,calc(team2_scored_1p_home))
                print("1ST PERIOD CONCED. HOME: ", team2_conceded_1p_home,calc(team2_conceded_1p_home))
                print("1ST PERIOD SCORED  AWAY: ", team2_scored_1p_away,calc(team2_scored_1p_away))
                print("1ST PERIOD CONCED. AWAY: ", team2_conceded_1p_away,calc(team2_conceded_1p_away))
                print("1ST PERIOD COMMON HOME : ", team2_common_1p_home,calc(team2_common_1p_home))
                print("1ST PERIOD COMMON AWAY : ", team2_common_1p_away,calc(team2_common_1p_away))

                scorage1 = round((1 - (calc(team1_common_1p_home)[0] + calc(team1_common_1p_away)[0])/(calc(team1_common_1p_home)[6] + calc(team1_common_1p_away)[6])) * 100,1)
                scorage2 = round((1 - (calc(team2_common_1p_home)[0] + calc(team2_common_1p_away)[0])/(calc(team2_common_1p_home)[6] + calc(team2_common_1p_away)[6])) * 100,1)
                print("OK -1")
                mark = f'{scorage1}% + {scorage2}%'
                # depth = f'Depth::{len(score1+score2)}+{len(score3+score4)}'
                print("OK -2")

                team1_scored_1 = round((1 - (calc(team1_scored_1p_home)[0] + calc(team1_scored_1p_away)[0])/(calc(team1_scored_1p_home)[6] + calc(team1_scored_1p_away)[6])) * 100,1)
                team1_conceded_1 = round((1 - (calc(team1_conceded_1p_home)[0] + calc(team1_conceded_1p_away)[0]) / (
                            calc(team1_conceded_1p_home)[6] + calc(team1_conceded_1p_away)[6])) * 100, 1)
                team2_scored_1 = round((1 - (calc(team2_scored_1p_home)[0] + calc(team2_scored_1p_away)[0])/(calc(team2_scored_1p_home)[6] + calc(team2_scored_1p_away)[6])) * 100,1)
                team2_conceded_1 = round((1 - (calc(team2_conceded_1p_home)[0] + calc(team2_conceded_1p_away)[0]) / (
                            calc(team2_conceded_1p_home)[6] + calc(team2_conceded_1p_away)[6])) * 100, 1)
                print("OK -3")
                mark_team1 = f"{team1_scored_1}% to {team1_conceded_1}%"
                mark_team2 = f"{team2_scored_1}% to {team2_conceded_1}%"
                last = f'{last_2p_t1}-{last_2p_t2}@@@{last_3p_t1}-{last_3p_t2}'

                if (scorage1>=87 and scorage2>=87) or scorage1 > 96 or scorage2 > 96:
                    data = (title, current_score, *home_team_name,mark_team1, *away_team_name,mark_team2, "1ST PERIOD GOAL",mark,info,"Last::",last)
                    bet_siska(data)
                    print("FIRST PERIOD SCANNED")
                    if (last_3p_t1 == 0 or last_3p_t2 == 0) and p + p1 > 150:
                        data = (title, current_score, *home_team_name,mark_team1, *away_team_name,mark_team2, "1ST PERIOD GOAL",mark,info,"LAST 3 PERIODS WAS 0")
                        bet_siska(data)
                        print("FIRST PERIOD SCANNED according last 3 periods")

                    if last_3p_t1+last_2p_t1 == 0 or last_3p_t2+last_2p_t2 ==0 :
                        data = (title, current_score, *home_team_name, mark_team1, *away_team_name, mark_team2,
                                    "1ST PERIOD GOAL", mark, info, "LAST 3 and 2 PERIODS WAS 0")
                        bet_siska(data)
                        print("FIRST PERIOD SCANNED according last 3 and 2 periods")


                else:
                    print("1st period insufficient percentage")

            if all_seq_team1 + all_seq_team2 > 182:
                if last0_t1+last0_t2 >=1:
                    scorage1 = round((1 - (calc(team1_common_1p_home)[0] + calc(team1_common_1p_away)[0]) / (
                                calc(team1_common_1p_home)[6] + calc(team1_common_1p_away)[6])) * 100, 1)
                    scorage2 = round((1 - (calc(team2_common_1p_home)[0] + calc(team2_common_1p_away)[0]) / (
                                calc(team2_common_1p_home)[6] + calc(team2_common_1p_away)[6])) * 100, 1)
                    mark = f'{scorage1}% + {scorage2}%'
                    msg1 = f'AVE::  {all_seq_team1} >>> {all_seq_team2}'
                    msg2 = f'LAST 3 GAMES:: {last0_t1} >>> {last0_t2}'
                    msg3 = f'{l}/{len(dataset)} >>> {l1}/{len(dataset2)}'
                    data = ("<AVEREAGE>",title,*home_team_name,*away_team_name,msg1,msg2,msg3,mark)
                    bet_siska(data)




            if period == 2 and checker == 2 :
                print("CONDITION 1 FOR SECOND PERIOD IS OK")
                if score_one + score_two - total_1period == 0:
                    print("CONDITION 2 FOR SECOND PERIOD IS OK ")
                    print("<<<<<    2ND PERIOD   >>>>>")
                    print("2ND PERIOD SCORED  HOME: ",team1_scored_2p_home,calc(team1_scored_2p_home))
                    print("2ND PERIOD CONCED. HOME: ",team1_conceded_2p_home,calc(team1_conceded_2p_home))
                    print("2ND PERIOD SCORED  AWAY: ",team1_scored_2p_away,calc(team1_scored_2p_away))
                    print("2ND PERIOD CONCED. AWAY: ",team1_conceded_2p_away,calc(team1_conceded_2p_away))
                    print("2ND PERIOD COMMON HOME : ",team1_common_2p_home,calc(team1_common_2p_home))
                    print("2ND PERIOD COMMON AWAY : ",team1_common_2p_away,calc(team1_common_2p_away))
                    print()
                    print("2ND PERIOD SCORED  HOME: ", team2_scored_2p_home,calc(team2_scored_2p_home))
                    print("2ND PERIOD CONCED. HOME: ", team2_conceded_2p_home,calc(team2_conceded_2p_home))
                    print("2ND PERIOD SCORED  AWAY: ", team2_scored_2p_away,calc(team2_scored_2p_away))
                    print("2ND PERIOD CONCED. AWAY: ", team2_conceded_2p_away,calc(team2_conceded_2p_away))
                    print("2ND PERIOD COMMON HOME : ", team2_common_2p_home,calc(team2_common_2p_home))
                    print("2ND PERIOD COMMON AWAY : ", team2_common_2p_away,calc(team2_common_2p_away))

                    scorage1 = round((1 - (calc(team1_common_2p_home)[0] + calc(team1_common_2p_away)[0]) / (
                                calc(team1_common_2p_home)[6] + calc(team1_common_2p_away)[6])) * 100, 1)
                    scorage2 = round((1 - (calc(team2_common_2p_home)[0] + calc(team2_common_2p_away)[0]) / (
                                calc(team2_common_2p_home)[6] + calc(team2_common_2p_away)[6])) * 100, 1)

                    team1_scored_2 = round((1 - (calc(team1_scored_2p_home)[0] + calc(team1_scored_2p_away)[0]) / (
                                calc(team1_scored_2p_home)[6] + calc(team1_scored_2p_away)[6])) * 100, 1)
                    team1_conceded_2 = round(
                        (1 - (calc(team1_conceded_2p_home)[0] + calc(team1_conceded_2p_away)[0]) / (
                                calc(team1_conceded_2p_home)[6] + calc(team1_conceded_2p_away)[6])) * 100, 1)
                    team2_scored_2 = round((1 - (calc(team2_scored_2p_home)[0] + calc(team2_scored_2p_away)[0]) / (
                                calc(team2_scored_2p_home)[6] + calc(team2_scored_2p_away)[6])) * 100, 1)
                    team2_conceded_2 = round(
                        (1 - (calc(team2_conceded_2p_home)[0] + calc(team2_conceded_2p_away)[0]) / (
                                calc(team2_conceded_2p_home)[6] + calc(team2_conceded_2p_away)[6])) * 100, 1)

                    mark_team1 = f"{team1_scored_2}% to {team1_conceded_2}%"
                    mark_team2 = f"{team2_scored_2}% to {team2_conceded_2}%"


                    mark = f'{scorage1}% + {scorage2}%'
                    if (score5<=2 and score8<=2) or score5 == 0 or score8 == 0:
                        data = (title, current_score, *home_team_name,mark_team1, *away_team_name,mark_team2, "2ND PERIOD GOAL", mark)
                        bet_siska(data)
                        print("SECOND  PERIOD SCANNED")
                    else:
                        print("2nd period insufficient percantage")
                else:
                    print("Score was changed during 2nd period ")

        except Exception:
            print(Exception)
    finally:

       print("SCANNED")
       sleep(2)
       browser.quit()

















