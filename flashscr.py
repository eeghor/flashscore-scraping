import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select  # to deal with dropdown menues
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import re
import pandas as pd
from collections import defaultdict, namedtuple

from datetime import datetime

WAIT_TIME = 40 

y_from =2005
y_to = 2016

assert y_from > 2000 and y_to < 2017, ("We've got a problem: you requested years {}-{} but there's only data for 2001-2016...".format(y_from, y_to))
assert y_from <= y_to, ("Please, make sure that the earliest year you pick is not after the last year...")

comps = "WD MD MS WS"

abbr_dict = {"MS" : "Men's Singles", 
				"WS" : "Women's Singles", 
					"MD" : "Men's Doubles", 
						"WD" : "Women's Doubles"}

extra_link_cm = {"WS": "wta-singles", 
					"MS": "atp-singles", 
						"MD": "atp-doubles", 
							"WD": "wta-doubles"}

# example: http://www.flashscore.com/tennis/atp-doubles/australian-open-2001/results/
list_matches = []
TennisMatch = namedtuple("TennisMatch", "round date time p1 p2 score")

driver = webdriver.Chrome('/Users/ik/Codes/flashscore-scraping/chromedriver')
print("-------> scraping flashscore.com")

for competition in comps.split():

	print("scraping " + abbr_dict[competition] + "...")

	for year in range(y_from, y_to + 1):
		# print("year=",year)
		print("downloading data for",year, "...", end="")
	
		driver.get("http://www.flashscore.com/tennis/" + extra_link_cm[competition] + "/australian-open-" + str(year) + "/results/")

		rtabl = WebDriverWait(driver, WAIT_TIME).until(EC.visibility_of_element_located((By.XPATH, "//table[@class='tennis']")))

		for row in rtabl.find_elements_by_xpath(".//tr"):
			clls = row.find_elements_by_xpath(".//td")
			if len(clls) == 1:  # has to be a header row
				current_round = clls[0].text.strip()
			elif len(clls) == 6:  # result row
				# date and time are as 21.01. 10:00
				day_month, tm = row.find_element_by_xpath(".//td[contains(@class, 'time')]").text.strip().split()

				full_datetime = datetime.strptime(day_month + str(year), "%d.%m.%Y").strftime("%Y-%m-%d")
				# print("date=", full_datetime)
				# print("time=", tm)
				# get the players
				p1 = row.find_element_by_xpath(".//td[contains(@class, 'team') and contains(@class, 'home')]").text.strip()
				
				if "(" in p1:
					p1 = p1.split("(")[0].strip()
				# print("player1=",p1)
				p2 = row.find_element_by_xpath(".//td[contains(@class, 'team') and contains(@class, 'away')]").text.strip()
				
				if "(" in p2:
					p2 = p2.split("(")[0].strip()
				# print("player2=",p2)
				score = row.find_element_by_xpath(".//td[contains(@class, 'score')]").text.replace(" ","").strip()
				# print("score=",score)

				list_matches.append(TennisMatch(round=current_round, date=full_datetime, time=tm, 
					p1=p1, p2=p2, score=score))
		print("ok")

driver.quit()

print("done. retrieved {} match results".format(len(list_matches)))

df = pd.DataFrame(columns="round date time player1 player2 score".split())

for i, row in enumerate(list_matches):
	df.loc[i] = row
	
csv_fl = "scraped_flashscore_data_" + "_".join(comps.split()) + "_" + str(y_from) + "_" + str(y_to) + ".csv"

df.to_csv(csv_fl, index=False, sep="\t")

print("saved everything in the file called {} in your local directory".format(csv_fl))


	# now find all rows