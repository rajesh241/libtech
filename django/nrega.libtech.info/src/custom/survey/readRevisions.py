import json
from pprint import pprint

with open('revision_list.txt') as data_file:    
    data = json.load(data_file)

#pprint(data)
pprint(len(data["revisions"]))
pprint(data["revisions"][0])
