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
import pprint as pp

books = pd.read_csv('D:\\Documents\\College\Degree\\8th Sem\\Project\\Book.csv', sep=';', error_bad_lines=False,warn_bad_lines=False, encoding="latin-1")

books.columns = ['ISBN', 'bookTitle', 'bookAuthor', 'yearOfPublication', 'publisher', 'imageUrlS', 'imageUrlM', 'imageUrlL']

users = pd.read_csv('D:\\Documents\\College\Degree\\8th Sem\\Project\\Book-Users1.csv', sep=',', error_bad_lines=False, warn_bad_lines=False,encoding="latin-1")

users.columns = ['userID', 'Location', 'Age']

ratings = pd.read_csv('D:\\Documents\\College\Degree\\8th Sem\\Project\\Book-Ratings1.csv', sep=',', error_bad_lines=False,warn_bad_lines=False, encoding="latin-1")

ratings.columns = ['userID', 'ISBN', 'bookRating']

# Top Books Based on ratings
def get_top_list():
    ratings_count = pd.DataFrame(ratings.groupby('ISBN')['bookRating'].sum())
    top10= ratings_count.sort_values('bookRating',ascending=False).head(10)
    return top10

top=get_top_list()
print(top)  

# Find Similar books
def get_book_recommendation(input_book):
    list_of_similar_books=[]
    
    booksRatings = ratings.pivot_table(index='userID',columns='ISBN',values='bookRating')
    average_ratings = pd.DataFrame(ratings.groupby('ISBN')['bookRating'].mean())
    average_ratings['rating-count'] = pd.DataFrame(ratings.groupby('ISBN')['bookRating'].count())
    userRating = booksRatings[input_book]
    
    similarBooks = booksRatings.corrwith(userRating)
    similarBooks = similarBooks.dropna()
    
    for i in similarBooks.index.values:
        list_of_similar_books.append(i)

    return list_of_similar_books

get_book_recommendation('0446605239')