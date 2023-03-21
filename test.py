from scan import current_moment,get_link,handling
from parsing import check_link
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from datetime import datetime
from send import errormsg,make_mistake,startmsg

options = webdriver.ChromeOptions()
options.add_argument('--mute-audio')
browser = webdriver.Chrome(options=options)

browser.get("https://www.icehockey24.com/")

switch_to_live = browser.find_element(By.CSS_SELECTOR,
                                      "div.filters__tab:nth-child(2) > div:nth-child(2)")
switch_to_live.click()
period1_list = set()
period2_list = set()
period3_list = set()

refresher = 0

try:
    startmsg()
    while True:
            try:


                sleep(1)
                matches = browser.find_elements(By.CSS_SELECTOR,"[id^='g_4']")
                for i in matches:
                        time,score_one,score_two,scoreline = handling(i) # scoreline only for 2 and 3 periods???
                        period,minute = current_moment(time)

                        print("SECOND PERIOD::", scoreline[0],':',scoreline[1])
                        if period == 4:
                            continue

                        if period == 1 and minute >=9 and score_one + score_two == 0:
                            print("...........1st period is checking...........")
                            checker = 1
                            link = get_link(i)
                            if link in period1_list:
                                print("<<<<<1st period of match was already scanned...>>>>>")
                                continue
                            period1_list.add(link)
                            check_link(link,time,score_one,score_two,period,minute,checker)

                        if period == 2 and minute >=9 and scoreline[0]== 0 and scoreline[1] == 0:
                            print("...........2nd period is checking...........")
                            checker = 2
                            link = get_link(i)
                            if link in period2_list:
                                print("<<<<<2nd period of match was already scanned...>>>>>")
                                continue
                            period2_list.add(link)
                            check_link(link,time,score_one,score_two,period,minute,checker)

                print(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                sleep(10)
                refresher +=1
                print("REFRESHER:: ", refresher)
                if refresher % 100 == 0:
                    #browser.refresh()
                    #sleep(10)
                    #switch_to_live.click()
                    sleep(2)
            except Exception as ex:
                print(ex)
                make_mistake()
                sleep(2)
                continue
finally:
    errormsg()
