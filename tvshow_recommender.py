import numpy as np
import pandas as pd

df=pd.read_csv('tvshow_metadata.csv', delimiter = ',')

df=df[['Title','Year','imdbRating','imdbVotes','totalSeasons']]

df['Title'].head(20)
# Most Trending Shows

df[df.Title=="The Haunting of Hill House"]
# Searching for show details

df[df.Year=='2018-'].head(3)
# Top New releases of 2018

df.sort_values(by = ['imdbRating'],ascending = False).head(20)
# Sorted according to the IMdB rating

df.sort_values(by = ['imdbRating','Year'],ascending = False).head(20)
# Most Popular Shows

df.sort_values(by = ['imdbVotes'],ascending = False).head(10)
# Sorted by IMdB Votes

df.sort_values(by = ['Title']).head(20)
# A - Z Sorting

df.sort_values(by = ['Title'],ascending=False).head(20)
# Z-A Sorting

df['Title'].nunique()

df1=pd.read_csv('TV_Show_Dataset.csv', delimiter = ',')

df1.loc[df1['Genre'] == 'Comedy'].sort_values(by = ['imdbRating'],ascending= False)
# Top Rated Comedy Shows

df1.loc[df1['Country'] == 'India'].sort_values(by = ['imdbRating'],ascending= False)
#Indian Shows

df1.loc[df1['Rated'] == 'TV-14']
# TV-14 Rated

df1.loc[df1['Rated'] == 'TV-MA']
# MA Rated

df1.loc[df1['Rated'] == 'TV-PG']
# PG Rated

df1[(df1.Runtime > 30) & (df1.Runtime <60)].sort_values(by = ['imdbRating'],ascending= False)
# TV Shows whose average run time is greater than 30 mins

df1[(df1.Runtime > 0) & (df1.Runtime <30)].sort_values(by = ['imdbRating'],ascending= False)
# TV Shows whose average run time is less than 30 mins

df1[df1["Genre"].str.contains('Horror',na=False)].sort_values(by = ['imdbRating','imdbVotes'],ascending= False)
# Horror Genres Sorting

df1[df1["Genre"].str.contains('Thriller',na=False)].sort_values(by = ['imdbRating','imdbVotes'],ascending= False)
# Thriller

df1[df1["Genre"].str.contains('Romance',na=False)].sort_values(by = ['imdbRating','imdbVotes'],ascending= False)
# Romance

df1[df1["Genre"].str.contains('Mystery',na=False)].sort_values(by = ['imdbRating','imdbVotes'],ascending= False)
# Mystery

df1[df1["Genre"].str.contains('Comedy',na=False)].sort_values(by =['imdbRating','imdbVotes'],ascending= False)
# Comedy

df1[df1["Genre"].str.contains('Drama',na=False)].sort_values(by = ['imdbRating','imdbVotes'],ascending= False)
# Drama

df1[df1["Genre"].str.contains('Adventure',na=False)].sort_values(by =['imdbRating','imdbVotes'],ascending= False)
# Adventure

df1[df1["Genre"].str.contains('History',na=False)].sort_values(by = ['imdbRating','imdbVotes'],ascending= False)
# History

df1[df1["Genre"].str.contains('Biography',na=False)].sort_values(by =['imdbRating','imdbVotes'],ascending= False)
# Biography

df1[df1["Genre"].str.contains('Crime',na=False)].sort_values(by = ['imdbRating','imdbVotes'],ascending= False)
# Crime

df1[df1["Genre"].str.contains('Sci-Fi',na=False)].sort_values(by = ['imdbRating','imdbVotes'],ascending= False)
# Scifi

df1[df1["Genre"].str.contains('Action',na=False)].sort_values(by =['imdbRating','imdbVotes'],ascending= False)
# Action

df1[df1["Genre"].str.contains('Animation',na=False)].sort_values(by = ['imdbRating','imdbVotes'],ascending= False)
# Animation

df1[df1["Genre"].str.contains('Fantasy',na=False)].sort_values(by = ['imdbRating','imdbVotes'],ascending= False)
# Fantasy

