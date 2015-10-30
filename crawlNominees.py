from bs4 import BeautifulSoup
from pymongo import MongoClient
import db

client = MongoClient(db.conn_string)
db = client.oscar

# GET DIRECTORS
def getDirectors(nominee):
	director = db.boxoffice_movies.find_one({"name": nominee})	
	name = ""

	if director:
		if len(director["directors"]) == 1:
			name = director["directors"][0]
		else:
			for n in director["directors"]:
				name += n + ", "

			if name:
				name = name[:-2]

	if name == "":
		name = None

	return name

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

				name = nominee[1:]

				if cat == "DIRECTING":
					name = getDirectors(name)

				nominees[year][cat].append({
					"name": name,
					"won": True
				})
			else:

				name = nominee

				if cat == "DIRECTING":
					name = getDirectors(name)

				nominees[year][cat].append({
					"name": name,
					"won": False
				})

# remove all elements from collection
db.oscar_nominations.delete_many({})

for year, data in nominees.iteritems():

	data["_id"] = year
	db.oscar_nominations.insert_one(data)

print "done"