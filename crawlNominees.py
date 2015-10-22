from bs4 import BeautifulSoup
from pymongo import MongoClient
import db

client = MongoClient(db.conn_string)
db = client.oscar

# open saved results file from a search via http://awardsdatabase.oscars.org/
with open ("results.html", "r") as results:
    data = results.read().replace('\n', '')

# parse html file
soup = BeautifulSoup(data, "html.parser")

nominees = {}

# find data entry point
dl = soup.find("dl")

if dl:

	for child in dl.children:

		# start new year
		if "awardYearHeader" in str(child):

			year = int(child.get_text()[0:4])
			nominees[year] = {}

		# find category
		if "BSCategoryExact" in str(child):

			cat = child.get_text().split("(")[0].strip()
			nominees[year][cat] = []

		# nomination name
		if "BSNominationID" in str(child):

			nominee = child.get_text().split("--")[0].strip()

			if nominee.startswith("*"):
				nominees[year][cat].append({
					"name": nominee[1:],
					"won": True
				})
			else:
				nominees[year][cat].append({
					"name": nominee,
					"won": False
				})

# remove all elements from collection
db.oscar_nominations.delete_many({})

for year, data in nominees.iteritems():

	data["_id"] = year
	db.oscar_nominations.insert_one(data)

print "done"