from bs4 import BeautifulSoup
from time import sleep


def current_moment(time):
    if "1st" in time[0]:
        period = 1
    elif "2nd" in time[0]:
        period = 2
    elif "3rd" in time[0]:
        period = 3
    elif "Break" in time[0]:
        period = "BT"
    elif "Fin" in time[0]:
        period = 4
    else:
        period = "error"
    if period == "BT":
        minute = 0
    elif period ==  4:
        minute = 99
    else:
        minute = int(time[2])
    print("PERIOD:: ",period,"MINUTE:: ",minute)
    return period,minute

def get_link(match):
    link = match.get_attribute("id")
    url = f"https://www.icehockey24.com/match/{link[4:]}"
    return url

def handling(game):
    match = game.get_attribute("innerHTML")
    soup = BeautifulSoup(match, "html.parser")
    time = soup.select_one("div.event__stage--block").text.strip().split()
    if soup.select_one("div.event__score.event__score--home").text.strip().isdigit() and \
        soup.select_one("div.event__score.event__score--away").text.strip().isdigit():
        score_one = int(soup.select_one("div.event__score.event__score--home").text.strip())
        score_two = int(soup.select_one("div.event__score.event__score--away").text.strip())

        e1_2 = soup.select_one("div.event__part--home.event__part--2")
        e2_2 = soup.select_one("div.event__part--away.event__part--2")
        e1_3 = soup.select_one("div.event__part--home.event__part--3")
        e2_3 = soup.select_one("div.event__part--away.event__part--3")

        def ex(data): # existance
            if isinstance(data,type(None)):
                return 0
            if data.text.strip().isdigit():
                return int(data.text.strip())
            else:
                return  777

        score1_2, score2_2, score1_3, score2_3 = ex(e1_2),ex(e2_2),ex(e1_3), ex(e2_3)

    else:
        score_one = 99
        score_two = 99

    scoreline2_3 = (score1_2, score2_2, score1_3, score2_3)
    print("CURRENT SCORE:: ",score_one,"-",score_two)
    if "Finished" in time or "Overtime" in time or "Penalties" in time or "Postponed" in time \
            or "Interrupted" in time  or "Awaitingupdates" in time or "Awarded" in time or 'After Penalties' in time:
        time = ["Fin","Fin"]
    return time,score_one,score_two,scoreline2_3


