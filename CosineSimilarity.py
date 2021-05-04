from collections import Counter
import math
import numpy as np
from nltk.tokenize import TreebankWordTokenizer

def compute_idf(inv_idx, n_docs, min_df=15, max_df_ratio=0.90):
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

def index_search(query, index, idf, doc_norms, tokenizer=treebank_tokenizer):
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
    query_toks = tokenizer.tokenize(query.lower())
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
            ret.append((num[i]/den[i], i))
    ret.sort(key = lambda x:(-x[0],x[1]))
    return ret 