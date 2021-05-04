import json
from CosineSimilarity import *
from GoogleDrive import *

# res = {}
with open('items.json', 'r', encoding="utf8") as f:
  data = json.load(f)

docs = get_ingredients()
# print(docs[1119])
# docs = [{'name': 'Jamaican Jerked Chicken Recipe', 'ingredients': 'green onion,orange juice,ginger,pepper,lime juice,soy sauce,garlic,spice,cinnamon,clove,chicken'}]
n_docs = len(docs)
print(n_docs)
inv_idx = build_inverted_index(docs)
idf = compute_idf(inv_idx, n_docs)
doc_norms = compute_doc_norms(inv_idx, idf, n_docs)

for item in data:
  # lev = edit_distance_search(item['name'], docs)
  # if lev[0][0] < 15:
  #   print(item['name'], docs[lev[0][1]]['name'], lev[0][0])
  #   item['description'] += ', ' + docs[lev[0][1]]['ingredients']
  cos_sim = index_search(item['name'], inv_idx, idf, doc_norms)
  # print(cos_sim)
  if cos_sim and cos_sim[0][0] > 0.7:
      print(item['name'], docs[cos_sim[0][1]]['name'], cos_sim[0][0])
      item['description'] += ', ' + docs[cos_sim[0][1]]['ingredients']

#print(cos_sim)
jsonString = json.dumps(data)
jsonFile = open("new_items.json", "w")
jsonFile.write(jsonString)
jsonFile.close()
