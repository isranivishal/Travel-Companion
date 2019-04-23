from flask import Flask, redirect, url_for, request, render_template
import os
import pandas
from sklearn.model_selection import train_test_split
from urllib.request import *
from urllib.error import *
import numpy as np

app = Flask(__name__)

@app.route('/')
def CategoryPage():
   return render_template('CategoryPage.html')

@app.route('/PaginationMaps.html')
def PaginationFuncion():
	return render_template('PaginationMaps.html')

@app.route('/GenericSongRecommender.html')
def GenericSongRecommender():
	triplets_file = 'C:\\Users\\Mansi\\Desktop\\SongRecommenderSystem\\MillionSongs.txt'
	songs_metadata_file = 'C:\\Users\\Mansi\\Desktop\\SongRecommenderSystem\\song_data.csv'

	song_df_1 = pandas.read_table(triplets_file,header=None)
	song_df_1.columns = ['user_id', 'song_id', 'listen_count']

	song_df_2 =  pandas.read_csv(songs_metadata_file)
	song_df = pandas.merge(song_df_1, song_df_2.drop_duplicates(['song_id']), on="song_id", how="left")

	song_df['song'] = song_df["artist_name"] + ' - ' + song_df["title"]

	song_grouped = song_df.groupby(['song']).agg({'listen_count': 'count'}).reset_index()#Finding the listen count
	grouped_sum = song_grouped['listen_count'].sum()#Adding all the listen counts of all the songs
	song_grouped['percentage']  = song_grouped['listen_count'].div(grouped_sum)*100 #Finding the percentage column
	song_grouped.sort_values(['listen_count', 'song'], ascending = [0,1])#Scaling the value between 0 and 1

	users = song_df['user_id'].unique()

	songs = song_df['song'].unique()

	train_data, test_data = train_test_split(song_df, test_size = 0.20, random_state=0)

	#Class for Popularity based Recommender System modelclass 
	class popularity_recommender_py():  
	    def __init__(self):        
	        self.train_data = None        
	        self.user_id = None        
	        self.item_id = None        
	        self.popularity_recommendations = None            
	    #Create the popularity based recommender system model    
	    def create(self, train_data, user_id, item_id): 
	        self.train_data = train_data
	        self.user_id = user_id        
	        self.item_id = item_id         
	        
	        #Get a count of user_ids for each unique song as recommendation score
	        train_data_grouped = train_data.groupby([self.item_id]).agg({self.user_id: 'count'}).reset_index()        
	        train_data_grouped.rename(columns = {'user_id': 'score'},inplace=True)            
	        #Sort the songs based upon recommendation score
	        train_data_sort = train_data_grouped.sort_values(['score', self.item_id], ascending = [0,1])            
	        #Generate a recommendation rank based upon score
	        train_data_sort['Rank'] = train_data_sort['score'].rank(ascending=0, method='first')
	        #Get the top 10 recommendations
	        self.popularity_recommendations = train_data_sort.head(10)     
	        #Use the popularity based recommender system model to    
	        #make recommendations    
	    def recommend(self, user_id):            
	        user_recommendations = self.popularity_recommendations                 
	        #Add user_id column for which the recommendations are being generated        
	        user_recommendations['user_id'] = user_id            
	        #Bring user_id column to the front        
	        cols = user_recommendations.columns.tolist()        
	        cols = cols[-1:] + cols[:-1]        
	        user_recommendations = user_recommendations[cols]
	        return user_recommendations

	pm =popularity_recommender_py()
	pm.create(train_data, 'user_id', 'song')
	#user the popularity model to make some prediction
	user_id = users[5]
	recommendlist=[]
	recommendlist=pm.recommend(user_id)
	# print (type(recommendlist))
	# print(recommendlist)
	songlist=recommendlist["song"].tolist()
	userlist=recommendlist["user_id"].tolist()
	# print (songlist)
	# print(userlist)
	return render_template('GenericSongRecommender.html',songlist=songlist,userlist=userlist)

@app.route('/SongRecommender.html',methods=['GET','POST'])
def SongRecommender():
	artist_name=request.args.get('artist_name')
	release=request.args.get('release')
	title=request.args.get('title')
	artist_name=artist_name[:len(artist_name)].replace(" ","%20")
	release=release[:len(release)].replace(" ","%20")
	title=title[:len(title)].replace(" ","%20")
	# *************************************************************
	Solrquery="http://localhost:8983/solr/SongData/select?q=(artist_name:%22"+artist_name+"%22%20AND%20release:%22"+release+"%22"+"%20AND%20title:%22"+title+"%22)&mlt=true&mlt.fl=title,release,artist_name&mlt.mindf=1&mlt.mintf=1&mlt.boost=true&mlt.count=10&mlt.match.include=false"+"&wt=python"
	# **********************************************************
	connection=urlopen(Solrquery)
	response = eval(connection.read())
	songresultlist=[]
	for document in response['response']['docs']:
		song_id=document['id']
		i=0
		for similarsongs in response['moreLikeThis'][song_id]['docs']:
			songresultlist.append(similarsongs['title'][0])
	return 	render_template('SongRecommender.html',response=songresultlist)
@app.route('/PersonalisedSongRecommender.html')
def PersonalisedSongRecommender():
	triplets_file = 'C:\\Users\\Mansi\\Desktop\\SongRecommenderSystem\\MillionSongs.txt'
	songs_metadata_file = 'C:\\Users\\Mansi\\Desktop\\SongRecommenderSystem\\song_data.csv'
	song_df_1 = pandas.read_table(triplets_file,header=None)
	song_df_1.columns = ['user_id', 'song_id', 'listen_count']
	song_df_2 =  pandas.read_csv(songs_metadata_file)
	song_df = pandas.merge(song_df_1, song_df_2.drop_duplicates(['song_id']), on="song_id", how="left")
	song_df['song'] = song_df["artist_name"] + ' - ' + song_df["title"]	
	song_grouped = song_df.groupby(['song']).agg({'listen_count': 'count'}).reset_index()#Finding the listen count
	grouped_sum = song_grouped['listen_count'].sum()#Adding all the listen counts of all the songs
	song_grouped['percentage']  = song_grouped['listen_count'].div(grouped_sum)*100 #Finding the percentage column
	song_grouped.sort_values(['listen_count', 'song'], ascending = [0,1])#Scaling the value between 0 and 1
	users = song_df['user_id'].unique()
	songs = song_df['song'].unique()
	train_data, test_data = train_test_split(song_df, test_size = 0.10, random_state=0)
	class item_similarity_recommender_py():
	    def __init__(self):
	        self.train_data = None
	        self.user_id = None
	        self.item_id = None
	        self.cooccurence_matrix = None
	        self.songs_dict = None
	        self.rev_songs_dict = None
	        self.item_similarity_recommendations = None
	    def get_user_items(self, user):
	        user_data = self.train_data[self.train_data[self.user_id] == user]
	        user_items = list(user_data[self.item_id].unique())
	        return user_items
	    def get_item_users(self, item):
	        item_data = self.train_data[self.train_data[self.item_id] == item]
	        item_users = set(item_data[self.user_id].unique())
	        return item_users
	    def get_all_items_train_data(self):
	        all_items = list(self.train_data[self.item_id].unique())
	        return all_items
	    def construct_cooccurence_matrix(self, user_songs, all_songs):
	        user_songs_users = []        
	        for i in range(0, len(user_songs)):
	            user_songs_users.append(self.get_item_users(user_songs[i]))
	        cooccurence_matrix = np.matrix(np.zeros(shape=(len(user_songs), len(all_songs))), float)
	        for i in range(0,len(all_songs)):
	            songs_i_data = self.train_data[self.train_data[self.item_id] == all_songs[i]]
	            users_i = set(songs_i_data[self.user_id].unique())
	            for j in range(0,len(user_songs)):       
	                users_j = user_songs_users[j]
	                users_intersection = users_i.intersection(users_j)
	                if len(users_intersection) != 0:
	                    users_union = users_i.union(users_j)                    
	                    cooccurence_matrix[j,i] = float(len(users_intersection))/float(len(users_union))
	                else:
	                    cooccurence_matrix[j,i] = 0
	        return cooccurence_matrix
	    def generate_top_recommendations(self, user, cooccurence_matrix, all_songs, user_songs):
	        print("Non zero values in cooccurence_matrix :%d" % np.count_nonzero(cooccurence_matrix))
	        user_sim_scores = cooccurence_matrix.sum(axis=0)/float(cooccurence_matrix.shape[0])
	        user_sim_scores = np.array(user_sim_scores)[0].tolist()
	        sort_index = sorted(((e,i) for i,e in enumerate(list(user_sim_scores))), reverse=True)
	        columns = ['user_id', 'song', 'score', 'rank']
	        df = pandas.DataFrame(columns=columns)
	        rank = 1 
	        for i in range(0,len(sort_index)):
	            if ~np.isnan(sort_index[i][0]) and all_songs[sort_index[i][1]] not in user_songs and rank <= 10:
	                df.loc[len(df)]=[user,all_songs[sort_index[i][1]],sort_index[i][0],rank]
	                rank = rank+1
	        if df.shape[0] == 0:
	            print("The current user has no songs for training the item similarity based recommendation model.")
	            return -1
	        else:
	            return df
	    def create(self, train_data, user_id, item_id):
	        self.train_data = train_data
	        self.user_id = user_id
	        self.item_id = item_id
	    def recommend(self, user):
	        user_songs = self.get_user_items(user)    
	        print("No. of unique songs for the user: %d" % len(user_songs))
	        all_songs = self.get_all_items_train_data()
	        print("no. of unique songs in the training set: %d" % len(all_songs))
	        cooccurence_matrix = self.construct_cooccurence_matrix(user_songs, all_songs)
	        df_recommendations = self.generate_top_recommendations(user, cooccurence_matrix, all_songs, user_songs)
	        return df_recommendations
	    def get_similar_items(self, item_list):
	        user_songs = item_list
	        all_songs = self.get_all_items_train_data()        
	        print("no. of unique songs in the training set: %d" % len(all_songs))
	        cooccurence_matrix = self.construct_cooccurence_matrix(user_songs, all_songs)
	        user = ""
	        df_recommendations = self.generate_top_recommendations(user, cooccurence_matrix, all_songs, user_songs)
	        return df_recommendations
	is_model = item_similarity_recommender_py()
	is_model.create(train_data, 'user_id', 'song')
	user_id = users[4]
	user_items = is_model.get_user_items(user_id)

	answer=is_model.recommend(user_id)
	# print(answer)
	# print(type(answer))
	return render_template('PersonalisedSongRecommender.html',answer=answer)
if __name__ == '__main__':
   app.run()