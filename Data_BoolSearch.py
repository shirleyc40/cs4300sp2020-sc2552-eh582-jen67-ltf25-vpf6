import math
import numpy as np
import csv
import matplotlib.pyplot as plt
import re
import json

#getting list of all restaurants in kaggle dataset
restaurants = []
with open('restaurants.csv', 'r', encoding="utf8") as f:
    reader_restaurants = csv.reader(f, delimiter = ',')
    for row in reader_restaurants:
        if re.findall("austin$",row[1]):
            if row[0] == 'BBQ at Frankie�s':
                row[0] = "BBQ at Frankie's"
            restaurants.append(row[0])

#getting list of all businesses in yelp dataset
yelp = []
file1 = open("yelp_academic_dataset_business.json", 'r', encoding="utf8")
Lines = file1.readlines()
 

    # Strips the newline character
for line in Lines:
    yelp.append(json.loads(line))


#get dictionary of restaurants
result = dict()

for rest in yelp:
    if rest['name'] in restaurants and rest['city'] == 'Austin':
        name = rest['name'].lower()
        result[name] = dict()
        
        result[name]['stars'] = rest['stars']
        result[name]['reviewcount'] = rest['review_count']
        result[name]['hours'] = rest['hours']
        result[name]['categories'] = rest['categories']


#function to tokenize description
def tokenize(text):
    """Returns a list of words that make up the text.
    
    Note: for simplicity, lowercase everything.
    Requirement: Use regular expressions to satisfy this function
    
    Params: {text: String}
    Returns: List
    """
    # YOUR CODE HERE
    t = text.lower()
    words = re.findall(r'[a-z]+',t)
    return words

#list of items with tokens
items = []
ID = 0
with open('menu_items.csv', 'r', encoding="utf8") as f:
    reader_menus = csv.reader(f, delimiter = ',')
    for row in reader_menus:
        if row[0] in result.keys():
            if len(row[3]) > 3 and len(row[3]) < 200:
                item = dict()
                item['ID'] = ID
                item['restaurant'] = row[0]
                item['item_name'] = row[2] 
                item['description'] = row[2] + ' : ' + row[3]
                item['toks'] = tokenize(item['description'])
                item['price'] = row[4]
                items.append(item)
                ID += 1

#list of items for database
items2 = []

with open('menu_items.csv', 'r', encoding="utf8") as f:
    reader_menus = csv.reader(f, delimiter = ',')
    for row in reader_menus:
        if row[0] in result.keys():
            if len(row[3]) > 3 and len(row[3]) < 200:
                item = dict()
                item['restaurant'] = row[0]
                item['name'] = row[2] 
                item['description'] = row[2] + ' : ' + row[3]
#                 item['toks'] = tokenize(item['description'])
                item['price'] = row[4]
                items.append(item)


#creating json of items

# with open('items.json', 'w') as fp:
#     json.dump(items2, fp)

from collections import Counter

#inverted index
def build_inverted_index(msgs):
    """ Builds an inverted index from the messages.
    
    Arguments
    =========
    
    msgs: list of dicts.
        Each message in this list already has a 'toks'
        field that contains the tokenized message.
    
    Returns
    =======
    
    inverted_index: dict
        For each term, the index contains 
        a sorted list of tuples (doc_id, count_of_term_in_doc)
        such that tuples with smaller doc_ids appear first:
        inverted_index[term] = [(d1, tf1), (d2, tf2), ...]
        
    Example
    =======
    
    >> test_idx = build_inverted_index([
    ...    {'toks': ['to', 'be', 'or', 'not', 'to', 'be']},
    ...    {'toks': ['do', 'be', 'do', 'be', 'do']}])
    
    >> test_idx['be']
    [(0, 2), (1, 2)]
    
    >> test_idx['not']
    [(0, 1)]
    
    Note that doc_id refers to the index of the document/message in msgs.
    """
    # YOUR CODE HERE
    inverted_indx = dict()

    for doc_id,msg in enumerate(msgs):
        counts = Counter(msg['toks'])
        for word, value in counts.items():
            if word in inverted_indx.keys():
                inverted_indx[word].append((doc_id,value))
            else:
                inverted_indx[word] = [(doc_id,value)]

    return inverted_indx


def boolean_search(query_word,excluded_word, inverted_index):
    """ Search the collection of documents for the given query_word 
        provided that the documents do not include the excluded_word
    
    Arguments
    =========
    
    query_word: string,
        The word we are searching for in our documents.
    
    excluded_word: string,
        The word excluded from our documents.
    
    inverted_index: an inverted index as above
    
    
    Returns
    =======
    
    results: list of ints
        Sorted List of results (in increasing order) such that every element is a `doc_id`
        that points to a document that satisfies the boolean
        expression of the query.
        
    """
    # YOUR CODE HERE
    M = [] #merdged list
    A = [doc_count[0] for doc_count in inverted_index[query_word.lower()]] #query
    B = [doc_count[0] for doc_count in inverted_index[excluded_word.lower()]] #excluded
    
    
    at_end = False
    A_pnt = 0
    B_pnt = 0
    A_end = len(A)
    B_end = len(B)
    while at_end == False:
        if A[A_pnt] == B[B_pnt]:
            A_pnt += 1
            B_pnt += 1
        else:
            if A[A_pnt] < B[B_pnt]:
                M.append(A[A_pnt])
                A_pnt += 1
            else:
                B_pnt += 1
        if A_pnt >= A_end or B_pnt >= B_end:
            at_end = True
    
    if A_pnt < A_end:
        M.append(A[A_pnt:])
    return M


#example of query:

# query_want = 'noodle'
# query_dont_want = 'hot'

# search = boolean_search(query_want,query_dont_want,inv_idx)
# print(search)
# print(items[search[0]])