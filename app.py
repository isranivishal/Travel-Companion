from flask import Flask, render_template,request,redirect,url_for,logging,session
from pymongo import MongoClient
from bson.json_util import dumps
import json
from flask_bcrypt import Bcrypt
import numpy as np
import pandas as pd
import random,requests
# import pysolr
# from urllib.request import *
# from urllib.error import *
# from flask_web3 import current_web3, FlaskWeb3
import os

# from .movies_recommender import get_top_movies_list,get_movie_recommendation,get_genre_list
from .books_recommender import get_top_list,get_book_recommendation

client = MongoClient('127.0.0.1:27017')
db = client.travel_companion

app = Flask(__name__)

# app.config.update({'ETHEREUM_PROVIDER': 'http', 'ETHEREUM_ENDPOINT_URI': 'http://localhost:7545'})
# web3 = FlaskWeb3(app=app)

app.secret_key='mysecret'
bcrypt = Bcrypt(app)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

def if_logged_in():
    if session['set']==1:
        return True
    else:
        return False     


# User Register
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        users=db.users
        existing_user = users.find_one({'email_id' : request.form['email_id'] })

        if existing_user is None:
            hashpass= bcrypt.generate_password_hash(request.form['password']).decode('utf-8')          
            id=users.count() + 1
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email_id = request.form['email_id']
            my_list={}
            my_list["books"]=[]
            my_list["movies"]=[]
            my_list["tv_shows"]=[]
            my_list["songs"]=[]
            purchases={}
            purchases["books"]=[]
            purchases["movies"]=[]
            purchases["tv_shows"]=[]
            purchases["songs"]=[]
            history={}
            history["books"]=[]
            history["movies"]=[]
            history["tv_shows"]=[]
            history["songs"]=[]

            users.insert_one({
                    "id" : id,
                    "first_name" : first_name,
                    "last_name" : last_name,
                    "email_id" : email_id,
                    "password" : hashpass,
                    "my_list" : my_list,
                    "purchases" : purchases,
                    "history" : history
            })
            session['id']=id
            session['set']=1
            return redirect(url_for('user_personalise'))
        return 'The user already exists!'
    return render_template('Home.html')

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    users=db.users
    login_user = users.find_one({'email_id' : request.form['email_id'] })
    if login_user:
        if bcrypt.check_password_hash(login_user['password'],request.form['password']):
            session['id']=login_user['id']
            session['set']=1
            return redirect(url_for('home')) 
    return 'Invalid Username/Password Combination'

@app.route('/home')
def home():
    names= db.users.find({'id' : session['id']},{'_id':0,'first_name' : 1 })
    for doc in names:
        for i in doc:
            name=doc[i]
    if(if_logged_in()):
        return render_template('home.html',name=name)
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear
    session['set']=0
    return redirect(url_for('index'))      

# get user related info
@app.route('/user_personalise')
def user_personalise():
    names= db.users.find({'id' : session['id']},{'_id':0,'first_name' : 1 })
    for doc in names:
        for i in doc:
            name=doc[i]
    return render_template('user-personalise.html',name=name)  

@app.route('/get_user_data', methods=['GET', 'POST'])
def get_user_data():
    
    books=[]
    movies=[]
    tvshows=[]
    songs=[]

    books.append(request.form['book1'])
    books.append(request.form['book2'])
    books.append(request.form['book3'])

    movies.append(request.form['movie1'])
    movies.append(request.form['movie2'])
    movies.append(request.form['movie3'])

    tvshows.append(request.form['tvshow1'])
    tvshows.append(request.form['tvshow2'])
    tvshows.append(request.form['tvshow3'])

    songs.append(request.form['songs1'])
    songs.append(request.form['songs2'])
    songs.append(request.form['songs3'])

    
    db.users.update_one(
            {"id": session['id']},
            {
                "$set": {
                    "history":{
                        "books" : books,
                        "movies" : movies,
                        "tv_shows" : tvshows,
                        "songs" : songs
                    }
                }
        }
    )
    return redirect(url_for('user_loading'))

@app.route('/user_loading')
def user_loading():
    names= db.users.find({'id' : session['id']},{'_id':0,'first_name' : 1 })
    for doc in names:
        for i in doc:
            name=doc[i]
    return render_template('user-loading.html',name=name)  

# user related 
@app.route('/my_list', methods = ['GET'])
def my_list():
    try:
        user_details = db.users.find({'id' : session['id']},{'_id':0,'my_list' : 1 })  
    except Exception as e:
        return dumps({'error' : str(e)})
    return render_template('user-my-list.html', user_details=user_details)    

@app.route('/my_account', methods = ['GET'])
def my_account():
    try:
        user_details = db.users.find({'id' : session['id']},{'_id':0,'first_name' : 1,'last_name' : 1,'email_id' : 1,'history' : 1 })  
    except Exception as e:
        return dumps({'error' : str(e)})
    return render_template('user-my-account.html', user_details=user_details)   

@app.route('/my_purchases', methods = ['GET'])
def my_purchases():
    try:
        user_details = db.users.find({'id' : session['id']},{'_id':0,'first_name' : 1,'last_name' : 1,'email_id' : 1,'purchases' : 1 })   
    except Exception as e:
        return dumps({'error' : str(e)})
    return render_template('user-my-purchases.html', user_details=user_details)   

#modules routing

@app.route("/books_home")
def books_home():

    topbooks=[]
    top=get_top_list()
    for i in range(len(top)):
        topbooks.append(db.books.find({'ISBN' : top[i]},{'_id':0,'Book-Title' : 1 }))

    recommend=""
    recommended=[]
    user_history = db.users.find({'id' : session['id']},{'_id':0,'history' : 1 })
    for doc in user_history:
        for books in doc['history']['books']:
            title=books
            isbn=db.books.find({'Book-Title' : title},{'_id':0,'ISBN' : 1 })
            break
    recommend=get_book_recommendation(isbn[0]['ISBN'])
    for i in recommend:
        recommended.append(db.books.find({'ISBN' : i},{'_id':0,'Book-Title' : 1 }))

    return render_template('books-home.html',recommended=recommended,topbooks=topbooks)

@app.route("/books_details/<name>")
def books_details(name):
    books_name=db.books.find({'Book-Title' : name})
    return render_template('books-details.html',books_name=books_name[0]) 

@app.route("/tvshow-home")
def tvshow_home():
    df=pd.read_csv('tvshow_metadata.csv', delimiter = ',')
    
    toplist=df['Title'].head(6).tolist()
    tv_show_details=[]
    for title in toplist:
        tv_show_details.append(db.tv_shows.find({'Title' : title},{'_id':0,'Title' : 1,'imdbRating' : 1 ,'Genre' : 1,'Plot' : 1 ,'Poster' : 1}))
    
    most_popular_list=df.sort_values(by = ['imdbRating','Year'],ascending = False).head(6)
    tv_show_details1=[]
    for title in most_popular_list['Title'].tolist():
        tv_show_details1.append(db.tv_shows.find({'Title' : title},{'_id':0,'Title' : 1,'imdbRating' : 1 ,'Genre' : 1,'Plot' : 1 ,'Poster' : 1}))
    
    less_time=df[(df.Runtime > 30) & (df.Runtime <60)].sort_values(by = ['imdbRating'],ascending= False).head(6)
    tv_show_details7=[]
    for title in less_time['Title'].tolist():
        tv_show_details7.append(db.tv_shows.find({'Title' : title},{'_id':0,'Title' : 1,'imdbRating' : 1 ,'Genre' : 1,'Plot' : 1 ,'Poster' : 1}))

    more_time=df[(df.Runtime > 0) & (df.Runtime <30)].sort_values(by = ['imdbRating'],ascending= False).head(6)
    tv_show_details8=[]
    for title in more_time['Title'].tolist():
        tv_show_details8.append(db.tv_shows.find({'Title' : title},{'_id':0,'Title' : 1,'imdbRating' : 1 ,'Genre' : 1,'Plot' : 1 ,'Poster' : 1}))

    indian_list=df.loc[df['Country'] == 'India'].sort_values(by = ['imdbRating'],ascending= False).head(6)
    tv_show_details2=[]
    for title in indian_list['Title'].tolist():
        tv_show_details2.append(db.tv_shows.find({'Title' : title},{'_id':0,'Title' : 1,'imdbRating' : 1 ,'Genre' : 1,'Plot' : 1 ,'Poster' : 1}))
    
    romance_list=df[df["Genre"].str.contains('Romance',na=False)].sort_values(by = ['imdbRating','imdbVotes'],ascending= False).head(6)
    tv_show_details3=[]
    for title in romance_list['Title'].tolist():
        tv_show_details3.append(db.tv_shows.find({'Title' : title},{'_id':0,'Title' : 1,'imdbRating' : 1 ,'Genre' : 1,'Plot' : 1 ,'Poster' : 1}))

    comedy_list=df[df["Genre"].str.contains('Comedy',na=False)].sort_values(by =['imdbRating','imdbVotes'],ascending= False).head(6)
    tv_show_details4=[]
    for title in comedy_list['Title'].tolist():
        tv_show_details4.append(db.tv_shows.find({'Title' : title},{'_id':0,'Title' : 1,'imdbRating' : 1 ,'Genre' : 1,'Plot' : 1 ,'Poster' : 1}))
    
    action_list=df[df["Genre"].str.contains('Action',na=False)].sort_values(by =['imdbRating','imdbVotes'],ascending= False).head(6)
    tv_show_details5=[]
    for title in action_list['Title'].tolist():
        tv_show_details5.append(db.tv_shows.find({'Title' : title},{'_id':0,'Title' : 1,'imdbRating' : 1 ,'Genre' : 1,'Plot' : 1 ,'Poster' : 1})) 

    action_list=df[df["Genre"].str.contains('Animation',na=False)].sort_values(by =['imdbRating','imdbVotes'],ascending= False).head(6)
    tv_show_details6=[]
    for title in action_list['Title'].tolist():
        tv_show_details6.append(db.tv_shows.find({'Title' : title},{'_id':0,'Title' : 1,'imdbRating' : 1 ,'Genre' : 1,'Plot' : 1 ,'Poster' : 1})) 

    return render_template('tvshow-home.html',tv_show_details=tv_show_details,tv_show_details1=tv_show_details1,tv_show_details2=tv_show_details2,tv_show_details3=tv_show_details3,tv_show_details4=tv_show_details4,tv_show_details5=tv_show_details5,tv_show_details6=tv_show_details6,tv_show_details7=tv_show_details7,tv_show_details8=tv_show_details8)  

@app.route("/tvshow_details/<name>")
def tvshow_details(name):
    tvshow_name=db.tv_shows.find({'Title' : name})
    return render_template('tvshow-details.html',tv_show_details=tvshow_name)
 

@app.route("/movies_home")
def movies_home():
    toplist=get_top_movies_list().tolist()

    actionlist=get_genre_list('Action').tolist()
    horrorlist=get_genre_list('Horror').tolist()
    dramalist=get_genre_list('Drama').tolist()
    thrillerlist=get_genre_list('Thriller').tolist()
    comedylist=get_genre_list('Comedy').tolist()
    romancelist=get_genre_list('Romance').tolist()

    user_history = db.users.find({'id' : session['id']},{'_id':0,'history' : 1 })
    recommendation=[]

    for doc in user_history:
        for movies in doc['history']['movies']:
            temp=get_movie_recommendation(movies).tolist()
            recommendation.append(temp)
,recommendation=recommendation ,toplist=toplist,actionlist=actionlist,comedylist=comedylist,horrorlist=horrorlist,dramalist=dramalist,thrillerlist=thrillerlist,romancelist=romancelist
    return render_template('movies-home.html')

@app.route("/movies_details/<name>")
def movies_details(name):
    URL="http://www.omdbapi.com/?apikey=64a25551&t="+name
    movie_name= requests.get(url = URL)
    data = movie_name.json() 
    return render_template('movies-details.html',movie=data)

@app.route("/places-near-by")
def places_near_by():
    return render_template('places-to-visit.html')

@app.route('/surprise')
def surprise():
    name_of_surprise=""
    image_of_surprise=""
    type_of_surprise=""
    
    csvfiles=['Book1.csv','tvshow_metadata.csv']
    choice=random.choice(csvfiles)
    f = pd.read_csv(choice ,sep=',', error_bad_lines=False,warn_bad_lines=False, encoding="utf-8-sig")
    sample=f.sample()

    if choice == "Book1.csv":
        name=sample['Title'].tolist()
        image=sample['Image-URL-L'].tolist()
        name_of_surprise=name[0]
        image_of_surprise=image[0]
        type_of_surprise="Book"

    elif choice == "tvshow_metadata.csv":
        name1=sample['Title'].tolist()
        image1=sample['Poster'].tolist()
        name_of_surprise=name1[0]
        image_of_surprise=image1[0]
        type_of_surprise="TV Show"

    return render_template('surprise.html',name=name_of_surprise,image=image_of_surprise,type=type_of_surprise)

@app.route('/blockNumber',methods=['GET','POST'])
def blockNumber():
    songid=request.args.get('songid')
    Solrquery="http://localhost:8983/solr/UnifiedUserId/select?q=UnifiedId:"+str(session['id'])+"&wt=python"
    connection=urlopen(Solrquery)
    response = eval(connection.read())
    print(response)
    songuserid=response['response']['docs'][0]['SongUserId'][0]
    solr = pysolr.Solr('http://localhost:8983/solr/tempMillionSongsData')
    solr.add([
        {
            "user_id":songuserid,
            "song_id": songid,
            "listen_count":0,
        },
    ])
    solr.commit()
    fromaddr=current_web3.eth.accounts[session['id']]
    toaddr=current_web3.eth.accounts[0]
    web3.eth.sendTransaction({'from': fromaddr, 'to': toaddr, 'value': current_web3.toWei("1", 'ether')})
    balance=current_web3.eth.getBalance(current_web3.eth.accounts[0])
    return render_template('success.html',songid=songid,songuserid=songuserid,balance=balance)

@app.route('/songs_home',methods=['GET','POST'])
def songs_home():
    os.system("cls")
    user_history = db.users.find({'id' : session['id']},{'_id':0,'history' : 1 })
    title=""
    for doc in user_history:
        for songs in doc['history']['songs']:
            title=songs
            break

    title=title[:len(title)].replace(" ","%20")

    # artist_name=request.args.get('artist_name')
    # release=request.args.get('release')
    # title=request.args.get('title')

    Solrquery="http://localhost:8983/solr/SongData/select?q=(title:%22"+title+"%22)"+"&rows=1&start=0&wt=python"
    connection=urlopen(Solrquery)

    response1 = eval(connection.read())

    release=response1['response']['docs'][0]['release'][0]
    artist_name=response1['response']['docs'][0]['artist_name'][0]

    artist_name=artist_name[:len(artist_name)].replace(" ","%20")
    release=release[:len(release)].replace(" ","%20")

    Solrquery="http://localhost:8983/solr/SongData/select?q=(artist_name:%22"+artist_name+"%22%20AND%20release:%22"+release+"%22"+"%20AND%20title:%22"+title+"%22)&mlt=true&mlt.fl=title,release,artist_name&mlt.mindf=1&mlt.mintf=1&mlt.boost=true&mlt.count=10&mlt.match.include=false"+"&wt=python"

    connection=urlopen(Solrquery)
    response = eval(connection.read())
    songresultlist=[]
    songidlist=[]
    songreleaselist=[]
    songartistlist=[]
    songyearlist=[]
    for document in response['response']['docs']:
        song_id=document['id']
        i=0
        for similarsongs in response['moreLikeThis'][song_id]['docs']:
            songresultlist.append(similarsongs['title'][0])
            songidlist.append(similarsongs['song_id'][0])
            songreleaselist.append(similarsongs['release'][0])
            songartistlist.append(similarsongs['artist_name'][0])
            songyearlist.append(similarsongs['year'][0])
    return 	render_template('songs-home.html',response=songresultlist,response2=songidlist,response3=songreleaselist,response4=songartistlist,response5=songyearlist)


if __name__ == '__main__':
    app.run(debug = True, threaded = True)

#extra code:
    # for doc in user_details:
    #     for i in doc:
    #         items=doc[i]
    #         for i in items:
    #             a=items[i]
    #             for j in a:
    #                 print(j)  