from collections import Counter
import math
import numpy as np
from nltk.tokenize import TreebankWordTokenizer
import re

treebank_tokenizer = TreebankWordTokenizer()

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

def build_inverted_index(msgs, tokenizer=tokenize):
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
    inverted_index = {}
    for ind, msg in enumerate(msgs):
        toks = tokenizer(msg['name']+msg['ingredients'].lower())
        if 'recipe' in toks:
            toks.remove('recipe')
            # print(toks)
        counts = Counter(toks)
        for term, count in counts.items():
            if term in inverted_index:
                inverted_index[term].append((ind, count))
            else:
                inverted_index[term] = [(ind, count)]
    return inverted_index

def compute_idf(inv_idx, n_docs, min_df=5, max_df_ratio=0.9):
    """ Compute term IDF values from the inverted index.
    Words that are too frequent or too infrequent get pruned.
    
    Hint: Make sure to use log base 2.
    
    Arguments
    =========
    
    inv_idx: an inverted index as above
    
    n_docs: int,
        The number of documents.
        
    min_df: int,
        Minimum number of documents a term must occur in.
        Less frequent words get ignored. 
        Documents that appear min_df number of times should be included.
    
    max_df_ratio: float,
        Maximum ratio of documents a term can occur in.
        More frequent words get ignored.
    
    Returns
    =======
    
    idf: dict
        For each term, the dict contains the idf value.
        
    """
    
    # YOUR CODE HERE
    idf = {}
    for term, value in inv_idx.items():
        df = len(value)
        # print(df/n_docs)
        if df >= min_df and df/n_docs <= max_df_ratio:
            idf[term] = math.log2(n_docs/(1+df))
    return idf

def compute_doc_norms(index, idf, n_docs):
    """ Precompute the euclidean norm of each document.
    
    Arguments
    =========
    
    index: the inverted index as above
    
    idf: dict,
        Precomputed idf values for the terms.
    
    n_docs: int,
        The total number of documents.
    
    Returns
    =======
    
    norms: np.array, size: n_docs
        norms[i] = the norm of document i.
    """
    
    # YOUR CODE HERE
    norms = np.zeros(n_docs)
    for term, value in idf.items():
        for doc in index[term]:
            norms[doc[0]] += (doc[1]*value)**2
    return np.sqrt(norms)

def index_search(query, index, idf, doc_norms, tokenizer=tokenize):
    """ Search the collection of documents for the given query
    
    Arguments
    =========
    
    query: string,
        The query we are looking for.
    
    index: an inverted index as above
    
    idf: idf values precomputed as above
    
    doc_norms: document norms as computed above
    
    tokenizer: a TreebankWordTokenizer
    
    Returns
    =======
    
    results, list of tuples (score, doc_id)
        Sorted list of results such that the first element has
        the highest score (descending order), but if there is 
        a tie for the score, sort by the second element, that is
        the `doc_id` with ascending order. 
        An example is as follows:
        
        score       doc_id
       [(0.9,       1000),
        (0.9,       1001),
        (0.8,       2000),
        (0.8,       2001),
        (0.8,       2002),
        ...]

        
    """
    
    # YOUR CODE HERE
    num = [0] * len(doc_norms)
    query_toks = tokenizer(query.lower())
    query_counts = Counter(query_toks)
    #calculate the query norm the same way the doc norms were calculated
    query_norm = 0
    
    # calculate the numerator by looking at each term in the query
    # and for each of those terms (if it is in idf), look in index to see which docs contain that term
    # add to the numerator for that doc the tf-idf of the query times tf-idf of the doc
    for term, q_tf in query_counts.items():
        if term in idf:
            query_norm += (q_tf*idf[term])**2
            for doc, d_tf in index[term]:
                num[doc] += (q_tf*idf[term])*(d_tf*idf[term])
                
    query_norm = math.sqrt(query_norm)
    den = query_norm * doc_norms
    
    # since started with 0s in num and have 0s in doc_norms,
    # go through and make sure not to add those to the cossim
    # when dividing the num by the den
    ret = []
    for i in range(len(num)):
        if num[i] != 0 and den[i] != 0:
            ret.append((num[i], i,))
    ret.sort(key = lambda x:(-x[0],x[1]))
    return ret 


def insertion_cost(message, j):
    return 1

def deletion_cost(query, i):
    return 1

def substitution_cost(query, message, i, j):
    if query[i-1] == message[j-1]:
        return 0
    else:
        return 2
    
curr_insertion_function = insertion_cost
curr_deletion_function = deletion_cost
curr_substitution_function = substitution_cost

def edit_matrix(query, message):
    """ calculates the edit matrix
    
    Arguments
    =========
    
    query: query string,
        
    message: message string,
    
    m: length of query + 1,
    
    n: length of message + 1,
    
    Returns:
        edit matrix {(i,j): int}
    """
    
    m = len(query) + 1
    n = len(message) + 1
    
    matrix = np.zeros((m, n))
    for i in range(1, m):
        matrix[i, 0] = matrix[i-1, 0] + curr_deletion_function(query, i)
    
    for j in range(1, n):
        matrix[0, j] = matrix[0, j-1] + curr_insertion_function(message, j)
    
    for i in range(1, m):
        for j in range(1, n):
            matrix[i, j] = min(
                matrix[i-1, j] + curr_deletion_function(query, i), # "down" or delete op
                matrix[i, j-1] + curr_insertion_function(message, j), # "right" or insert op
                matrix[i-1, j-1] + curr_substitution_function(query, message, i, j) # "diagnol" or sub op
            )
    
    return matrix

def edit_distance(query, message):
    """ Edit distance calculator
    
    Arguments
    =========
    
    query: query string,
        
    message: message string,
    
    Returns:
        edit cost (int)
    """
        
    query = query.lower()
    message = message.lower()
    
    # YOUR CODE HERE
    matrix = edit_matrix(query, message)
    return matrix[-1, -1]

def edit_distance_search(query, msgs):
    """ Edit distance search
    
    Arguments
    =========
    
    query: string,
        The query we are looking for.
        
    msgs: list of dicts,
        Each message in this list has a 'text' field with
        the raw document.
    
    Returns
    =======
    
    result: list of (score, message) tuples.
        The result list is sorted by score such that the closest match
        is the top result in the list.
    
    """
    # YOUR CODE HERE
    ret = []
    for i, msg in enumerate(msgs):
        score = edit_distance(query, msg['name'])
        ret.append((score, i))
    ret.sort(key=lambda x:x[0])
    return ret

def build_name_sims_jac(n_docs, menu_items, ingredients, n_items=9046):
    """Returns a matrix of size num_movies x num_movies where entry [i,j]
       should be the Jaccard similarity between the category sets for movies i and j. 
        
    Notes: 
        - Movies sometimes contain *duplicate* categories! You should only count a category once.
        - A movie should have a Jaccard similarity of 1.0 with itself.
        - If a movie has no categories, then its Jaccard similarity with other movies is 0.
    
    Params: {num_movies: Integer,
             input_data: List<Dictionary>}
    Returns: np.ndarray 
    """
    # YOUR CODE HERE
    name_sim_jac = np.zeros((n_items, n_docs))
    for i, item in enumerate(menu_items):
        set_categories1 = set(tokenize(item['name']))
        for j, recipe in enumerate(ingredients):
            set_categories2 = set(tokenize(recipe['name']))
            if "recipe" in set_categories2:
                set_categories2.remove("recipe")
            if len(set_categories1) == 0 or len(set_categories2) == 0:
                name_sim_jac[i, j] = 0
            else:
                num = len(set_categories1.intersection(set_categories2))
                den = len(set_categories1.union(set_categories2))
                name_sim_jac[i, j] = num/den
    return name_sim_jac

# movie_name_to_index = {name:movie_id_to_index[movie_name_to_id[name]] for name in [d['movie_name'] for d in data]}
# movie_index_to_name = {v:k for k,v in movie_name_to_index.items()}

def get_ranked_movies(item_id, docs, sim_matrix):
    """
    Return sorted rankings (most to least similar) of movies as 
    a list of two-element tuples, where the first element is the 
    movie name and the second element is the similarity score
    
    This function will sort movies with the same score
    according to how these movies were ordered in the original data.
    
    Params: {mov: String,
             sim_matrix: np.ndarray}
    Returns: List<Tuple>
    """
    
    # Get movie index from movie name
    item_idx = item_id
    
    # Get list of similarity scores for movie
    score_lst = sim_matrix[item_idx]
    mov_score_lst = [(docs[i], s) for i,s in enumerate(score_lst)]
    
    # Do not account for movie itself in ranking
    mov_score_lst = mov_score_lst[:item_idx] + mov_score_lst[item_idx+1:]
    
    # Sort rankings by score
    mov_score_lst = sorted(mov_score_lst, key=lambda x: -x[1])
    
    return mov_score_lst