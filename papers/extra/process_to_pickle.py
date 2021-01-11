import csv
fobj = open("journalList_dots.csv", mode = "r")
reader = csv.reader(fobj, delimiter=";")
abbrev = {rows[0]:rows[1] for rows in reader}
import pickle
pickle.dump(abbrev, open("journalList_dots.p", "wb"))

