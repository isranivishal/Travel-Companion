import sys
import pandas as pd
import matplotlib.pyplot as plt
import sklearn.metrics as metrics
import numpy as np
from sklearn.neighbors import NearestNeighbors
from scipy.spatial.distance import correlation
from sklearn.metrics.pairwise import pairwise_distances
import ipywidgets as widgets
from IPython.display import display, clear_output
from contextlib import contextmanager
import warnings
import numpy as np
import os, sys
import re
import seaborn as sns

books = pd.read_csv('Book.csv', sep=',', error_bad_lines=False,warn_bad_lines=False, encoding="latin-1")

users = pd.read_csv('Book-User1.csv', sep=',', error_bad_lines=False, warn_bad_lines=False,encoding="latin-1")

ratings = pd.read_csv('Book-Rating1.csv', sep=',', error_bad_lines=False,warn_bad_lines=False, encoding="latin-1")

# Top Books Based on ratings
def get_top_list():
    ratings_count = pd.DataFrame(ratings.groupby('ISBN')['Book-Rating'].sum())
    top10 = ratings_count.sort_values('Book-Rating',ascending=False).head(7)
    return top10.index.tolist()

# Find Similar books
def get_book_recommendation(input_book):
    list_of_similar_books=[]
    
    booksRatings = ratings.pivot_table(index='User-ID',columns='ISBN',values='Book-Rating')
    average_ratings = pd.DataFrame(ratings.groupby('ISBN')['Book-Rating'].mean())
    average_ratings['rating-count'] = pd.DataFrame(ratings.groupby('ISBN')['Book-Rating'].count())
    userRating = booksRatings[input_book]
    
    similarBooks = booksRatings.corrwith(userRating)
    similarBooks = similarBooks.dropna()
    
    for i in similarBooks.index.values:
        list_of_similar_books.append(i)

    return list_of_similar_books

    