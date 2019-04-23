# #collaborative

# reader = Reader()
# ratings = pd.read_csv('movies_ratings_small.csv')
# ratings.head()
# data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)
# data.split(n_folds=5)
# svd = SVD()
# #evaluate(svd, data, measures=['RMSE', 'MAE'])
# trainset = data.build_full_trainset()
# svd.train(trainset)

# ratings[ratings['userId'] == 1]
# svd.predict(1, 302, 3)

# #Hybrid

# def convert_int(x):
#     try:
#         return int(x)
#     except:
#         return np.nan

# id_map = pd.read_csv('movies_links_small.csv')[['movieId', 'tmdbId']]
# id_map['tmdbId'] = id_map['tmdbId'].apply(convert_int)
# id_map.columns = ['movieId', 'id']
# id_map = id_map.merge(smd[['title', 'id']], on='id').set_index('title')
# #id_map = id_map.set_index('tmdbId')

# indices_map = id_map.set_index('id')

# def hybrid(userId, title):
#     idx = indices[title]
#     tmdbId = id_map.loc[title]['id']
#     #print(idx)
#     movie_id = id_map.loc[title]['movieId']
    
#     sim_scores = list(enumerate(cosine_sim[int(idx)]))
#     sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
#     sim_scores = sim_scores[1:26]
#     movie_indices = [i[0] for i in sim_scores]
    
#     movies = smd.iloc[movie_indices][['title', 'vote_count', 'vote_average', 'year', 'id']]
#     movies['est'] = movies['id'].apply(lambda x: svd.predict(userId, indices_map.loc[x]['movieId']).est)
#     movies = movies.sort_values('est', ascending=False)
#     return movies['title'].head(10)


# uid = sys.argv[1]
# moviename = sys.argv[2]
# print(hybrid(uid, moviename))