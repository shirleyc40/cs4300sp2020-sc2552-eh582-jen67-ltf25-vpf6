import math
import numpy as np
import csv
# import matplotlib.pyplot as plt
import re
import json

# #getting list of all restaurants in kaggle dataset
# restaurants = {}
# with open('restaurants.csv', 'r', encoding="utf8") as f:
#     reader_restaurants = csv.reader(f, delimiter = ',')
#     for row in reader_restaurants:
#         if re.findall("austin$",row[1]):
#             if row[0] == 'BBQ at Frankie�s':
#                 row[0] = "BBQ at Frankie's"
#             restaurants[row[0]] = row[1]

# #getting list of all businesses in yelp dataset
# yelp = []
# file1 = open("yelp_academic_dataset_business.json", 'r', encoding="utf8")
# Lines = file1.readlines()
 

#     # Strips the newline character
# for line in Lines:
#     yelp.append(json.loads(line))


# #get dictionary of restaurants
# result = dict()

# for rest in yelp:
#     if rest['name'] in restaurants and rest['city'] == 'Austin':
#         name = rest['name'].lower()
#         result[name] = dict()
        
#         result[name]['stars'] = rest['stars']
#         result[name]['reviewcount'] = rest['review_count']
#         result[name]['hours'] = json.dumps(rest['hours'])
#         result[name]['categories'] = rest['categories']
#         result[name]['link'] = restaurants[rest['name']]
#         result[name]['address'] = rest['address'] + ", " + rest['city'] + ", " + rest['state'] + " " + rest['postal_code']

# with open('result.json', 'w') as fp:
#     json.dump(result, fp)


# #function to tokenize description
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

# #list of items with tokens
# items = []
# ID = 0
# with open('menu_items.csv', 'r', encoding="utf8") as f:
#     reader_menus = csv.reader(f, delimiter = ',')
#     for row in reader_menus:
#         if row[0] in result.keys():
#             if len(row[3]) > 3 and len(row[3]) < 200:
#                 item = dict()
#                 item['ID'] = ID
#                 item['restaurant'] = row[0]
#                 item['item_name'] = row[2] 
#                 item['description'] = row[2] + ' : ' + row[3]
#                 item['toks'] = tokenize(item['description'])
#                 item['price'] = row[4]
#                 items.append(item)
#                 ID += 1

# #list of items for database
# items2 = np.array([])

# with open('menu_items.csv', 'r', encoding="utf8") as f:
#     reader_menus = csv.reader(f, delimiter = ',')
#     for row in reader_menus:
#         if row[0] in result.keys():
#             if len(row[3]) > 3 and len(row[3]) < 200:
#                 item = dict()
#                 item['restaurant'] = row[0]
#                 item['name'] = row[2] 
# #                 item['description'] = row[2] + ' : ' + row[3]
#                 item['description'] = row[3]
# #                 item['toks'] = tokenize(item['description'])
#                 item['price'] = row[4]
#                 np.append(items2,item)


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
    inverted_idx = dict()

    temp = dict()

    # msgs here is the item dict 
    for item in msgs:
        temp[item['id']] = item

    for i in range(1,2908):
        if i in temp:
            item = temp[i]
            toks = tokenize(item['description'])
            counts = Counter(toks)
            for word, value in counts.items():
                if word in inverted_idx.keys():
                    inverted_idx[word].append((item['id'],value))
                else:
                    inverted_idx[word] = [(item['id'], value)]

    return inverted_idx


def boolean_search(query_word,excluded_word, inverted_index, price_range, prices):
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
    M = [] #merged list
    try:
        A = [doc_count[0] for doc_count in inverted_index[query_word.lower()]] #query
        B = [doc_count[0] for doc_count in inverted_index[excluded_word.lower()]] #excluded
    except:
        return M
    
    A_pnt = 0
    B_pnt = 0
    A_end = len(A)
    B_end = len(B)
    while A_pnt < A_end and  B_pnt < B_end:
        if A[A_pnt] == B[B_pnt]:
            A_pnt += 1
            B_pnt += 1
        else:
            if A[A_pnt] < B[B_pnt]:
                if prices[int(A[A_pnt])] < price_range:
                    M.append(int(A[A_pnt]))
                A_pnt += 1
            else:
                B_pnt += 1
    
    while A_pnt < A_end:
        if prices[int(A[A_pnt])] < price_range:
            M.append(int(A[A_pnt]))
        A_pnt += 1
    return M


#example of query:

# query_want = 'noodle'
# query_dont_want = 'hot'

# search = boolean_search(query_want,query_dont_want,inv_idx)
# print(search)
# print(items[search[0]])

def new_inv_ind(doc_inds, documents, inv_ind_func):
    """ Create a new inverted index that only contains terms in the list of documents
    returned from a boolean search
    
    Arguments
    =========
    
    doc_inds: list of ints,
        The indices of items in the items list. Result of the previous Boolean search
        
    documents: np.array,
        list of dictionaries representing each document. NEEDS TO BE NUMPY
    
    inv_ind_func: function,
        The function to create a inverted index. build_inverted_index(msgs)
        
    
    Returns
    =======
    
    inverted_index: dict
        For each term, the index contains 
        a sorted list of tuples (doc_id, count_of_term_in_doc)
        such that tuples with smaller doc_ids appear first:
        inverted_index[term] = [(d1, tf1), (d2, tf2), ...]
        
    """
    temp = dict()

    # msgs here is the item dict 
    for item in documents:
        # print(item)
        temp[item['id']] = item

    new_docs = np.array([])
    for i in doc_inds:
        new_docs = np.append(new_docs, temp[i])

    new_inv_ind = inv_ind_func(new_docs)
    return new_inv_ind


def term_sort(want_query,not_query,inv_ind):
    """ Create two sorted lists of terms from the query, by the number of docs that use the term
    
    Arguments
    =========
    
    want_query: list,
        The query of wanted terms.
        
    not_query: list,
        The query of terms not wanted
    
    inv_ind: inverted index,
    
    tokenize_func: tokenize function,
        
    
    Returns
    =======
    
    wants: 
        List of (wanted terms,term freq) sorted by term frequency
        
    nots:
        List of (not wanted terms,term) sorted by term frequency
        
    """
    
#     want_toks = tokenize_func(want_query)
#     not_toks = tokenize_func(not_query)
    
    wants = []
    for tok in want_query:
        if tok in inv_ind:
            l = len(inv_ind[tok])
            wants.append((tok,l))
    wants.sort(key = lambda x: x[1]) 
    
    nots = []
    for tok in not_query:
        if tok in inv_ind:
            l = len(inv_ind[tok])
            nots.append((tok,l))
    nots.sort(key = lambda x: x[1])
    
    return wants,nots
    


def main(want_query,not_query,price_range,item_list, inv_idx, prices):
    """
    BIG ASSUMPTION FOR RIGHT NOW: the wants and exclude lists are same length
    
    returns:
        documents: list,
            A list of documents that match the query terms
    """
    #get inverted index
    # inv_ind = build_inverted_index(item_list) 
    
    #get sorted lists of query terms
    want_words,not_want_words = term_sort(want_query,not_query,inv_idx)
        
    #loop through boolean searches
    documents = item_list
    for i in range(len(want_words)):
        for j in range(len(not_want_words)):
            doc_list = boolean_search(want_words[i][0],not_want_words[j][0],inv_idx,price_range, prices)
            # print(doc_list)
            # doc list is a list of item ids
            temp = dict()

            # msgs here is the item dict 
            for item in documents:
                # print(item)
                temp[item['id']] = item
            
            documents = np.array([])
            for x in doc_list:
                if x in temp:
                    documents = np.append(documents, temp[x])

            inv_ind = new_inv_ind(doc_list, item_list, build_inverted_index)
    # print("hey: ", documents)   
    return documents
    
    

#example:
# qw = ['noodle','noodle']
# qn = ['crispy','egg']

# r = main(qw,qn,100,items2)
# print(r)