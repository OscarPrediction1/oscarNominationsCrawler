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
	else:
		director = {}
		director["boxOfficeId"] = None

	if name == "":
		name = None

	return name, director["boxOfficeId"]

# open saved results file from a search via http://awardsdatabase.oscars.org/
with open ("results2.html", "r") as results:
    data = results.read().replace('\n', '')

# parse html file
soup = BeautifulSoup(data, "html.parser")

nominees = {}
data = []

# find data entry point
dl = soup.find("dl")

if dl:

	for child in dl.children:

		# start new year
		if "awardYearHeader" in str(child):

			year = int(child.get_text()[0:4])
			print year
			nominees[year] = {}

		# find category
		if "BSCategoryExact" in str(child):

			cat = child.get_text().split("(")[0].strip()
			nominees[year][cat] = []

		# nomination name
		if "BSNominationID" in str(child):

			nominee = child.get_text().split("--")[0].strip()
			won = False

			item = {
				"year": year,
				"category": cat,
				"film": None,
				"boxOfficeId": None,
				"actor": None,
				"director": None,
				"won": False
			}

			if nominee.startswith("*"):
				item["won"] = True
				nominee = nominee[1:]

			if cat == "ACTOR IN A LEADING ROLE" or cat == "ACTOR IN A SUPPORTING ROLE" or cat == "ACTRESS IN A LEADING ROLE" or cat == "ACTRESS IN A SUPPORTING ROLE":

				item["actor"] = nominee

				film = child.get_text().split("--")[1].strip()
				if "{" in film:
					film = film.split("{")[0].strip()

				item["film"] = film
				item["director"], item["boxOfficeId"] = getDirectors(film)

				# bla
			elif cat == "DIRECTING":

				director = ""

				item["film"] = nominee
				item["director"] = child.get_text().split("--")[1].strip()
				director, item["boxOfficeId"] = getDirectors(nominee)

			elif cat == "ART DIRECTION" or cat == "CINEMATOGRAPHY" or cat == "COSTUME DESIGN" or cat == "FILM EDITING" or cat == "FOREIGN LANGUAGE FILM" or cat == "MAKEUP" or cat == "MUSIC (Original Score)" or cat == "BEST PICTURE" or cat == "SOUND" or cat == "SOUND EDITING" or cat == "VISUAL EFFECTS" or cat.startswith("WRITING"):

				item["film"] = nominee
				item["director"], item["boxOfficeId"] = getDirectors(nominee)

			data.append(item)


# remove all elements from collection
db.oscar_nominations_extended.delete_many({})

for d in data:
	db.oscar_nominations_extended.insert_one(d)

print "done"