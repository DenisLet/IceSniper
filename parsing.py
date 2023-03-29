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
            "href") + "results/"
        team_away = browser.find_elements(By.CSS_SELECTOR, "a.participant__participantName")[1].get_attribute(
            "href") + "results/"
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
        # print(a, p, l, sep="---")
        # print(a1, p1, l1, sep="---")

        last9_t1 = dataset[:9].count(0)
        last9_t2 = dataset2[:9].count(0)
        # print(dataset[:9])
        # print(dataset2[:9])
        # print(last9_t1)
        # print(last9_t2)
        last0_t1 = dataset[3:12].count(0)
        last0_t2 = dataset2[3:12].count(0)
        # print(dataset[3:12])
        # print(dataset2[3:12])
        # print("ZERO IN LAST 3 GAMES:: ", last0_t1)
        # print("ZERO IN LAST 3 GAMES:: ", last0_t2)

        all_seq_team1 = round((1 - l / len(dataset)) * 100, 1)
        all_seq_team2 = round((1 - l1 / len(dataset2)) * 100, 1)
        # print("AVE PERIOD 1T:: ", all_seq_team1, f'{l}/{len(dataset)}')
        # print("AVE PERIOD 2T:: ", all_seq_team2, f'{l1}/{len(dataset2)}')







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

        match_matrix = [team1_scored_1p_home,
                        team1_conceded_1p_home,
                        team1_scored_2p_home,
                        team1_conceded_2p_home]

        cases_home_t1 = len(team1_scored_1p_home)
        cases_away_t1 = len(team1_scored_1p_away)
        cases_home_t2 = len(team2_scored_1p_home)
        cases_away_t2 = len(team2_scored_1p_away)

        def catcher00(a, b, c, d, long):
            collector = []
            for i in range(long):
                if a[i] + b[i] == 0:
                    collector.append(c[i] + d[i])
            #         print('2nd period after 0-0::', c[i], ':', d[i])
            # print()
            return collector

        '''1st period ended with 0-0'''

        t1_home00 = catcher00(team1_scored_1p_home,
                              team1_conceded_1p_home,
                              team1_scored_2p_home,
                              team1_conceded_2p_home, cases_home_t1)

        t1_away00 = catcher00(team1_scored_1p_away,
                              team1_conceded_1p_away,
                              team1_scored_2p_away,
                              team1_conceded_2p_away, cases_away_t1)

        t2_home00 = catcher00(team2_scored_1p_home,
                              team2_conceded_1p_home,
                              team2_scored_2p_home,
                              team2_conceded_2p_home, cases_home_t2)

        t2_away00 = catcher00(team2_scored_1p_away,
                              team2_conceded_1p_away,
                              team2_scored_2p_away,
                              team2_conceded_2p_away, cases_away_t2)

        def catcher10(a, b, c, d, long):
            collector = []
            for i in range(long):
                if a[i] == 1 and b[i] == 0:
                    collector.append(c[i] + d[i])
            #         print('2nd period after 1-0::',c[i],':',d[i])
            # print()

            return collector

        def catcher01(a, b, c, d, long):
            collector = []
            for i in range(long):
                if a[i] == 0 and b[i] == 1:
                    collector.append(c[i] + d[i])
            #         print('2nd period after 0-1::', c[i], ':', d[i])
            # print()
            return collector

        '''home team win in persent match 1 period with 1-0 scores'''

        t1_win10 = catcher10(team1_scored_1p_home,
                             team1_conceded_1p_home,
                             team1_scored_2p_home,
                             team1_conceded_2p_home, cases_home_t1)

        t1_win01 = catcher01(team1_scored_1p_away,
                             team1_conceded_1p_away,
                             team1_scored_2p_away,
                             team1_conceded_2p_away, cases_away_t1)

        t2_lose10 = catcher01(team2_scored_1p_home,
                              team2_conceded_1p_home,
                              team2_scored_2p_home,
                              team2_conceded_2p_home, cases_home_t2)

        t2_lose01 = catcher10(team2_scored_1p_away,
                              team2_conceded_1p_away,
                              team2_scored_2p_away,
                              team2_conceded_2p_away, cases_away_t2)

        '''away team win in persent match 1 period with 0-1 scores'''

        t2_win10 = catcher10(team2_scored_1p_home,
                             team2_conceded_1p_home,
                             team2_scored_2p_home,
                             team2_conceded_2p_home, cases_home_t2)

        t2_win01 = catcher01(team2_scored_1p_away,
                             team2_conceded_1p_away,
                             team2_scored_2p_away,
                             team2_conceded_2p_away, cases_away_t2)

        t1_lose10 = catcher01(team1_scored_1p_home,
                              team1_conceded_1p_home,
                              team1_scored_2p_home,
                              team1_conceded_2p_home, cases_home_t1)

        t1_lose01 = catcher10(team1_scored_1p_away,
                              team1_conceded_1p_away,
                              team1_scored_2p_away,
                              team1_conceded_2p_away, cases_away_t1)

        '''1st period ended with 1-1'''

        def catcher11(a, b, c, d, long):
            collector = []
            for i in range(long):
                if a[i] == 1 and b[i] == 1:
                    collector.append(c[i] + d[i])
            #         print('2nd period after 1-1::', c[i], ':', d[i])
            # print()
            return collector

        t1_home11 = catcher11(team1_scored_1p_home,
                              team1_conceded_1p_home,
                              team1_scored_2p_home,
                              team1_conceded_2p_home, cases_home_t1)

        t1_away11 = catcher11(team1_scored_1p_away,
                              team1_conceded_1p_away,
                              team1_scored_2p_away,
                              team1_conceded_2p_away, cases_away_t1)

        t2_home11 = catcher11(team2_scored_1p_home,
                              team2_conceded_1p_home,
                              team2_scored_2p_home,
                              team2_conceded_2p_home, cases_home_t2)

        t2_away11 = catcher11(team2_scored_1p_away,
                              team2_conceded_1p_away,
                              team2_scored_2p_away,
                              team2_conceded_2p_away, cases_away_t2)

        ''' first period scored 2-0 or 0-2'''

        def catcher20(a, b, c, d, long):
            collector = []
            for i in range(long):
                if a[i] == 2 and b[i] == 0:
                    collector.append(c[i] + d[i])
            #         print('2nd period after 2-0::',c[i],':',d[i])
            # print()

            return collector

        def catcher02(a, b, c, d, long):
            collector = []
            for i in range(long):
                if a[i] == 0 and b[i] == 2:
                    collector.append(c[i] + d[i])
            #         print('2nd period after 0-2::', c[i], ':', d[i])
            # print()

            return collector

        '''home team win in persent match 1 period with 2-0 scores'''

        t1_win20 = catcher20(team1_scored_1p_home,
                             team1_conceded_1p_home,
                             team1_scored_2p_home,
                             team1_conceded_2p_home, cases_home_t1)

        t1_win02 = catcher02(team1_scored_1p_away,
                             team1_conceded_1p_away,
                             team1_scored_2p_away,
                             team1_conceded_2p_away, cases_away_t1)

        t2_lose20 = catcher02(team2_scored_1p_home,
                              team2_conceded_1p_home,
                              team2_scored_2p_home,
                              team2_conceded_2p_home, cases_home_t2)

        t2_lose02 = catcher20(team2_scored_1p_away,
                              team2_conceded_1p_away,
                              team2_scored_2p_away,
                              team2_conceded_2p_away, cases_away_t2)

        '''away team win in persent match 1 period with 0-2 scores'''

        t2_win20 = catcher20(team2_scored_1p_home,
                             team2_conceded_1p_home,
                             team2_scored_2p_home,
                             team2_conceded_2p_home, cases_home_t2)

        t2_win02 = catcher02(team2_scored_1p_away,
                             team2_conceded_1p_away,
                             team2_scored_2p_away,
                             team2_conceded_2p_away, cases_away_t2)

        t1_lose20 = catcher02(team1_scored_1p_home,
                              team1_conceded_1p_home,
                              team1_scored_2p_home,
                              team1_conceded_2p_home, cases_home_t1)

        t1_lose02 = catcher20(team1_scored_1p_away,
                              team1_conceded_1p_away,
                              team1_scored_2p_away,
                              team1_conceded_2p_away, cases_away_t1)

        ''' first period scored 2-1 or 1-2'''

        def catcher21(a, b, c, d, long):
            collector = []
            for i in range(long):
                if a[i] == 2 and b[i] == 1:
                    collector.append(c[i] + d[i])
            #         print('2nd period after 2-1::',c[i],':',d[i])
            # print()

            return collector

        def catcher12(a, b, c, d, long):
            collector = []
            for i in range(long):
                if a[i] == 1 and b[i] == 2:
                    collector.append(c[i] + d[i])
            #         print('2nd period after 1-2::', c[i], ':', d[i])
            # print()

            return collector

        '''home team win in persent match 1 period with 2-1 scores'''

        t1_win21 = catcher21(team1_scored_1p_home,
                             team1_conceded_1p_home,
                             team1_scored_2p_home,
                             team1_conceded_2p_home, cases_home_t1)

        t1_win12 = catcher12(team1_scored_1p_away,
                             team1_conceded_1p_away,
                             team1_scored_2p_away,
                             team1_conceded_2p_away, cases_away_t1)

        t2_lose21 = catcher12(team2_scored_1p_home,
                              team2_conceded_1p_home,
                              team2_scored_2p_home,
                              team2_conceded_2p_home, cases_home_t2)

        t2_lose12 = catcher21(team2_scored_1p_away,
                              team2_conceded_1p_away,
                              team2_scored_2p_away,
                              team2_conceded_2p_away, cases_away_t2)

        '''away team win in persent match 1 period with 1-2 scores'''

        t2_win21 = catcher21(team2_scored_1p_home,
                             team2_conceded_1p_home,
                             team2_scored_2p_home,
                             team2_conceded_2p_home, cases_home_t2)

        t2_win12 = catcher12(team2_scored_1p_away,
                             team2_conceded_1p_away,
                             team2_scored_2p_away,
                             team2_conceded_2p_away, cases_away_t2)

        t1_lose21 = catcher12(team1_scored_1p_home,
                              team1_conceded_1p_home,
                              team1_scored_2p_home,
                              team1_conceded_2p_home, cases_home_t1)

        t1_lose12 = catcher21(team1_scored_1p_away,
                              team1_conceded_1p_away,
                              team1_scored_2p_away,
                              team1_conceded_2p_away, cases_away_t1)

        ''' first period scored 3-0 or 0-3'''

        def catcher30(a, b, c, d, long):
            collector = []
            for i in range(long):
                if a[i] == 3 and b[i] == 0:
                    collector.append(c[i] + d[i])
            #         print('2nd period after 3-0::',c[i],':',d[i])
            # print()

            return collector

        def catcher03(a, b, c, d, long):
            collector = []
            for i in range(long):
                if a[i] == 0 and b[i] == 3:
                    collector.append(c[i] + d[i])
            #         print('2nd period after 0-3::', c[i], ':', d[i])
            # print()

            return collector

        '''home team win in persent match 1 period with 3-0 scores'''

        t1_win30 = catcher30(team1_scored_1p_home,
                             team1_conceded_1p_home,
                             team1_scored_2p_home,
                             team1_conceded_2p_home, cases_home_t1)

        t1_win03 = catcher03(team1_scored_1p_away,
                             team1_conceded_1p_away,
                             team1_scored_2p_away,
                             team1_conceded_2p_away, cases_away_t1)

        t2_lose30 = catcher03(team2_scored_1p_home,
                              team2_conceded_1p_home,
                              team2_scored_2p_home,
                              team2_conceded_2p_home, cases_home_t2)

        t2_lose03 = catcher30(team2_scored_1p_away,
                              team2_conceded_1p_away,
                              team2_scored_2p_away,
                              team2_conceded_2p_away, cases_away_t2)

        '''away team win in persent match 1 period with 0-3 scores'''

        t2_win30 = catcher30(team2_scored_1p_home,
                             team2_conceded_1p_home,
                             team2_scored_2p_home,
                             team2_conceded_2p_home, cases_home_t2)

        t2_win03 = catcher03(team2_scored_1p_away,
                             team2_conceded_1p_away,
                             team2_scored_2p_away,
                             team2_conceded_2p_away, cases_away_t2)

        t1_lose30 = catcher03(team1_scored_1p_home,
                              team1_conceded_1p_home,
                              team1_scored_2p_home,
                              team1_conceded_2p_home, cases_home_t1)

        t1_lose03 = catcher30(team1_scored_1p_away,
                              team1_conceded_1p_away,
                              team1_scored_2p_away,
                              team1_conceded_2p_away, cases_away_t1)

        '''first period scored more then 3'''

        def catcher_more(a, b, c, d, long):
            collector = []
            for i in range(long):
                if a[i] + b[i] > 3:
                    collector.append(c[i] + d[i])
            #         print('2nd period after 3++++::', c[i], ':', d[i])
            # print()
            return collector

        t1_homeMo = catcher_more(team1_scored_1p_home,
                                 team1_conceded_1p_home,
                                 team1_scored_2p_home,
                                 team1_conceded_2p_home, cases_home_t1)

        t1_awayMo = catcher_more(team1_scored_1p_away,
                                 team1_conceded_1p_away,
                                 team1_scored_2p_away,
                                 team1_conceded_2p_away, cases_away_t1)

        t2_homeMo = catcher_more(team2_scored_1p_home,
                                 team2_conceded_1p_home,
                                 team2_scored_2p_home,
                                 team2_conceded_2p_home, cases_home_t2)

        t2_awayMo = catcher_more(team2_scored_1p_away,
                                 team2_conceded_1p_away,
                                 team2_scored_2p_away,
                                 team2_conceded_2p_away, cases_away_t2)

        def counter(data):
            count = 0
            null, one, two, more = 0, 0, 0, 0
            for i in data:
                count += 1
                if i == 0:
                    null += 1
                if i == 1:
                    one += 1
                if i == 2:
                    two += 1
                if i > 2:
                    more += 1
            return null, one, two, more, count

        per2_00 = counter(t1_home00 + t1_away00 + t2_home00 + t2_away00)
        per2_10 = counter(t1_win10 + t1_win01 + t2_lose01 + t2_lose10)
        per2_01 = counter(t2_win01 + t2_win10 + t1_lose10 + t1_lose01)
        per2_11 = counter(t1_home11 + t1_away11 + t2_home11 + t2_away11)
        per2_20 = counter(t1_win20 + t1_win02 + t2_lose02 + t2_lose20)
        per2_02 = counter(t2_win02 + t2_win20 + t1_lose20 + t1_lose02)
        per2_21 = counter(t1_win21 + t1_win12 + t2_lose12 + t2_lose21)
        per2_12 = counter(t2_win12 + t2_win21 + t1_lose21 + t1_lose12)
        per2_30 = counter(t1_win30 + t1_win03 + t2_lose03 + t2_lose30)
        per2_03 = counter(t2_win03 + t2_win30 + t1_lose30 + t1_lose03)
        per2_Mo = counter(t1_homeMo + t1_awayMo + t2_homeMo + t2_awayMo)

        def try_it_over(data, value):
            long = data[4]

            if data[0] == 0 and long >= value:
                return 1
            if data[0] != 0 and long / data[0] >= 12:
                return 1
            if long >= 8 and data[0] == 0 and data[1] <= 1:
                return 2


        def alternative_attempt(data1,data2,data3,data4,data5):
            reason1 = data1[0]+data2[0]+data3[0]+data4[0]+data5[0]
            reason2 = data1[4]+data2[4]+data3[4]+data4[4]+data5[4]
            if reason1<=1:
                if reason2>=15:
                    return True, reason1, reason2
            return False

        print('TRY IT OVER 0-0', try_it_over(per2_00,10), per2_00)
        print('TRY IT OVER 1-0', try_it_over(per2_10, 10), per2_10)
        print('TRY IT OVER 0-1', try_it_over(per2_01, 10), per2_01)
        print('TRY IT OVER 1-1', try_it_over(per2_11, 10), per2_11)
        print('TRY IT OVER 2-0', try_it_over(per2_20, 10), per2_11)
        print('TRY IT OVER 0-2', try_it_over(per2_02, 10), per2_11)
        print('TRY IT OVER 2-1', try_it_over(per2_21, 10), per2_21)
        print('TRY IT OVER 1-2', try_it_over(per2_12, 10), per2_12)
        print('TRY IT OVER 3-0', try_it_over(per2_30, 10), per2_30)
        print('TRY IT OVER 0-3', try_it_over(per2_03, 10), per2_03)
        print('TRY IT OVER 3++', try_it_over(per2_Mo, 10), per2_Mo)
        print(score_one, score_two)





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

        """    FORMING TO SEND MESSAGE   """
        current_score = f"{score_one}:{score_two}"


        if period == 1 and checker == 1:
            # print("FIRST PERIOD WILL BE SCANNED")
            # print("<<<<<HOME TEAM RESULTS>>>>>", home_team_name)
            # print("<<<<<    1ST PERIOD   >>>>>")
            # print("1ST PERIOD SCORED  HOME: ",team1_scored_1p_home,calc(team1_scored_1p_home))
            # print("1ST PERIOD CONCED. HOME: ",team1_conceded_1p_home,calc(team1_conceded_1p_home))
            # print("1ST PERIOD SCORED  AWAY: ",team1_scored_1p_away,calc(team1_scored_1p_away))
            # print("1ST PERIOD CONCED. AWAY: ",team1_conceded_1p_away,calc(team1_conceded_1p_away))
            # print("1ST PERIOD COMMON HOME : ",team1_common_1p_home,calc(team1_common_1p_home))
            # print("1ST PERIOD COMMON AWAY : ",team1_common_1p_away,calc(team1_common_1p_away))
            # print()
            # print("<<<<<AWAY TEAM RESULTS>>>>>")
            # print("<<<<<    1ST PERIOD   >>>>>")
            # print("1ST PERIOD SCORED  HOME: ", team2_scored_1p_home,calc(team2_scored_1p_home))
            # print("1ST PERIOD CONCED. HOME: ", team2_conceded_1p_home,calc(team2_conceded_1p_home))
            # print("1ST PERIOD SCORED  AWAY: ", team2_scored_1p_away,calc(team2_scored_1p_away))
            # print("1ST PERIOD CONCED. AWAY: ", team2_conceded_1p_away,calc(team2_conceded_1p_away))
            # print("1ST PERIOD COMMON HOME : ", team2_common_1p_home,calc(team2_common_1p_home))
            # print("1ST PERIOD COMMON AWAY : ", team2_common_1p_away,calc(team2_common_1p_away))

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

        if all_seq_team1 + all_seq_team2 > 182 and checker == 1:
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



        mark2 = f'AVE::  {all_seq_team1} >>> {all_seq_team2}'
        if checker == 2 :
            if score_one == 0 and score_two == 0:
                if try_it_over(per2_00,8) == 1:
                    data = ( title, *home_team_name, *away_team_name,current_score,'AVERAGE 2' ,mark2, f'{per2_00}' )
                    bet_siska(data)

            if score_one == 1 and score_two == 0:
                if try_it_over(per2_10,8) == 1:
                    data = ( title, *home_team_name, *away_team_name,current_score,'AVERAGE 2' ,mark2, f'{per2_10}' )
                    bet_siska(data)

            if score_one == 0 and score_two == 1:
                if try_it_over(per2_01,8) == 1:
                    data = ( title, *home_team_name, *away_team_name,current_score,'AVERAGE 2' ,mark2, f'{per2_01}' )
                    bet_siska(data)


            if score_one == 2 and score_two == 0:
                if try_it_over(per2_20,8) == 1:
                    data = ( title, *home_team_name, *away_team_name,current_score,'AVERAGE 2' ,mark2, f'{per2_20}' )
                    bet_siska(data)

            if score_one == 0 and score_two == 2:
                if try_it_over(per2_02,8) == 1:
                    data = ( title, *home_team_name, *away_team_name,current_score,'AVERAGE 2' ,mark2, f'{per2_02}' )
                    bet_siska(data)

            if score_one == 1 and score_two == 1:
                if try_it_over(per2_11,8) == 1:
                    data = ( title, *home_team_name, *away_team_name,current_score,'AVERAGE 2' ,mark2, f'{per2_11}' )
                    bet_siska(data)

            if score_one == 2 and score_two == 1:
                if try_it_over(per2_21,8) == 1:
                    data = ( title, *home_team_name, *away_team_name,current_score,'AVERAGE 2' ,mark2, f'{per2_21}' )
                    bet_siska(data)

            if score_one == 1 and score_two == 2:
                if try_it_over(per2_12,8) == 1 :
                    data = ( title, *home_team_name, *away_team_name,current_score,'AVERAGE 2 ' ,mark2, f'{per2_12}' )
                    bet_siska(data)

            if score_one == 3 and score_two == 0:
                if try_it_over(per2_30,8) == 1:
                    data = ( title, *home_team_name, *away_team_name,current_score,'AVERAGE 2' ,mark2, f'{per2_30}' )
                    bet_siska(data)

            if score_one == 0 and score_two == 3:
                if try_it_over(per2_03,8) == 1:
                    data = (title, *home_team_name, *away_team_name,current_score, 'AVERAGE 2', mark2, f'{per2_03}')
                    bet_siska(data)


            if score_one + score_two > 3:
                if try_it_over(per2_Mo,8) == 1:
                    data = (title, *home_team_name, *away_team_name,current_score,'AVERAGE 2', mark2, f'{per2_Mo}')
                    bet_siska(data)



            if  (score_one == 1 and score_two == 2) or\
                (score_one == 2 and score_two == 1) or \
                (score_one == 0 and score_two == 3) or  \
                (score_one == 3 and score_two == 0):
                if alternative_attempt(per2_12,per2_21,per2_30,per2_03,per2_Mo)[0] == True:
                    x1, x2 = alternative_attempt(per2_12, per2_21, per2_30, per2_03, per2_Mo)[1:]
                    data = (title, *home_team_name, *away_team_name, current_score, 'ALTERNATIVE', mark2, f'{x1}>>{x2}')
                    bet_siska(data)



    finally:

       print("SCANNED")
       sleep(2)
       browser.quit()

















