import sqlite3 
from bs4 import BeautifulSoup
import requests
import re
from requests.exceptions import RequestException
import json

CACHE_FNAME = 'cache_info_pages.json'

try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

except:
    CACHE_DICTION = {}
#=======

def unique_id_combination(baseurl):
    return baseurl

def make_request_using_cache(url):
    unique_ident = url

    if unique_ident in CACHE_DICTION:
        # print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    else:
        # print("Making a request for new data...")

        resp = requests.get(url)        
        
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() 
        return CACHE_DICTION[unique_ident]


###########################################################
DBNAME = 'IMDb.db'


try:
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
except:
    print("Failed to connect to db.")



def create_imdb():


    statement = '''
        DROP TABLE IF EXISTS 'Top_250_movies';
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'Top_250_movies' (
            'Id' INTEGER PRIMARY KEY NOT NULL,
            'Title' TEXT NOT NULL,
            'ReleaseYear' INTEGER DEFAULT NULL,
            'Rate' FLOAT NOT NULL,
            'NumberofUserRatings' INTEGER DEFAULT NULL
            );
    '''
    cur.execute(statement)
    conn.commit()


    statement = '''
        DROP TABLE IF EXISTS 'Actors';
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'Actors' (
            'Id' INTEGER PRIMARY KEY NOT NULL,
            'Name' TEXT DEFAULT NULL
            );
    '''
    cur.execute(statement)
    conn.commit()



    statement = '''
        DROP TABLE IF EXISTS 'Directors';
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'Directors' (
            'Id' INTEGER PRIMARY KEY NOT NULL,
            'Name' TEXT DEFAULT NULL,
            'BornCountry' TEXT DEFAULT NULL
            );
    '''
    cur.execute(statement)
    conn.commit()


    # cur.execute("PRAGMA foreign_keys = ON")
    conn.commit()

    statement = '''
        DROP TABLE IF EXISTS 'Cast_in_movie';
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'Cast_in_movie' (
            'CastId' INTEGER PRIMARY KEY AUTOINCREMENT,
            'ActorId' INTEGER NOT NULL,
            'MovieId' INTEGER NOT NULL
            -- CONSTRAINT 'ActorId' FOREIGN KEY ('ActorId') REFERENCES 'Actors' ('Id') ON DELETE NO ACTION ON UPDATE NO ACTION,
            -- CONSTRAINT 'MovieId' FOREIGN KEY ('MovieId') REFERENCES 'Top_250_movies' ('Id') ON DELETE NO ACTION ON UPDATE NO ACTION
            );
    '''
    cur.execute(statement)
    conn.commit()




    statement = '''
        DROP TABLE IF EXISTS 'Direct_movie';
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''
        CREATE TABLE 'Direct_movie' (
        'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
        'DirectorId' INTEGER NOT NULL,
        'MovieId' INTEGER NOT NULL
        -- CONSTRAINT 'DirectorId' FOREIGN KEY ('DirectorId') REFERENCES 'Directors' ('Id') ON DELETE NO ACTION ON UPDATE NO ACTION
        );
    '''
    cur.execute(statement)
    conn.commit()





def get_top250_movies_list():
    url = "http://www.imdb.com/chart/top"
    try:
        
        response = make_request_using_cache(url)

        try:
            html = response
            soup = BeautifulSoup(html, 'html.parser')
            movies = soup.find('tbody',class_= "lister-list")
            

            for movie in movies.find_all("tr"):
            # print(type(movie))
                poster = movie.find(class_='posterColumn')
                score = poster.find(name='span', attrs={'name':'ir'})['data-value']
                
                movie_link = movie.find(class_ = 'titleColumn').find('a')['href']
                
                year_str = movie.find(class_ = 'titleColumn').find('span').text
                year_pattern = re.compile('\d{4}')
                year = int(year_pattern.search(year_str).group())
                
                id_pattern = re.compile(r'(?<=tt)\d+(?=/?)')
                movie_id = int(id_pattern.search(movie_link).group())
                
                movie_name = movie.find(class_='titleColumn').find('a').string
                
                user_digit = filter(str.isdigit, movie.find(class_ = 'ratingColumn imdbRating').find("strong")["title"][13:-12])
                user_num_rating = ""
                for i in user_digit:
                    user_num_rating += i
                
                yield  {
                    'movie_id': movie_id,
                    'movie_name': movie_name,
                    'year': year,
                    'movie_link': movie_link,
                    'movie_rate': float(score),
                    'user_num_rating': int(user_num_rating)
                }
        except:
            print("Failed to parse.")

    except RequestException:
        print("Request Failed.")

    return None




def store_movie_data_to_db(movie_data):
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Failed to connect to db.")


    statement = '''
    INSERT INTO Top_250_movies
    VALUES (?, ?, ?, ?, ?)
    '''
    insertion = (movie_data['movie_id'], movie_data['movie_name'], movie_data['year'], movie_data['movie_rate'], movie_data['user_num_rating'])


    try:
        cur.execute(statement, insertion)
        conn.commit()
        # print("Movie data INSERT INTO table Top_250_movies!")
        

    except:  
        conn.rollback()



# ##############################################################################


# #get directors and casts info

def get_movie_detail_data(movie_data):
   
    url = "http://www.imdb.com" + movie_data['movie_link']
    
    try:
        
        response = make_request_using_cache(url)

        try:
           
            html = response
            soup = BeautifulSoup(html, 'html.parser')
            #Scrap director's info
            director = soup.find(itemprop="director")

            person_link = director.find('a')['href']

            director_name = director.find(itemprop="name")
            movie_data['director_name'] = director_name.string

        
            id_pattern = re.compile(r'(?<=nm)\d+(?=/?)')
            person_id = int(id_pattern.search(person_link).group())
            
            movie_data['director_id'] = person_id

                

            detailed_url = "http://www.imdb.com" + person_link

            d_response = make_request_using_cache(detailed_url)
            d_soup = BeautifulSoup(d_response, 'html.parser')

            try:
                country = d_soup.find(id="name-born-info").find_all('a')[2].text.split(",")[-1].lstrip(" ")
                movie_data["BornCountry"] = country
                
            except:
                movie_data["BornCountry"] = "Unknown"

            store_director_data_in_db(movie_data)############################

        
            #scrap Cast's data
            
            cast = soup.find('table', class_="cast_list").find_all("tr")
            # print(cast)
            
        
            for actor in get_cast_data(cast):    
                # print("hi")
                store_actor_data_to_db(actor, movie_data)        

        except Exception as e:
            print("Failed to parse movie detaile.")
            print(e)

    except RequestException:
        print("Get Movie URL failed!")
    
    return movie_data



def get_cast_data(cast):
    try:
        for actor in cast[1:]:
            # print(actor)
            actor_data = actor.find('td',itemprop="actor").find('a')
            # print(actor_data)
            person_link = actor_data['href']
            id_pattern = re.compile(r'(?<=nm)\d+(?=/)')
            person_id = int(id_pattern.search(person_link).group())
            actor_name = actor_data.get_text().strip()
            yield {
                'actor_id': person_id,
                'actor_name': actor_name
            }
    except:
        # print("Failed to cast data.")
        yield {
                'actor_id': 00000000,
                'actor_name': "Unknown"
            }


def store_director_data_in_db(movie):
    statement = '''SELECT * FROM Directors 
               WHERE Id = {}'''.format(movie['director_id']) 

    try:
        cur.execute(statement)
        result = cur.fetchall()

    except:
        # print("Failed to fetch data")
        pass


    if result.__len__() == 0:

        statement = '''
        INSERT INTO Directors 
        VALUES (?, ?, ?)    
        '''          
        insertion = (movie['director_id'], movie['director_name'], movie['BornCountry'])


        try:
            cur.execute(statement, insertion)
            conn.commit()
            # print("Director data ADDED to DB table directors!", movie['director_name'] )
        except Exception as e:
            # conn.rollback()
            print("Failed to add to table directors")
            print(e)
    else:
        # print("This Director ALREADY EXISTED!!")
        pass

                
    ########table Directors_movie            
    statement = '''SELECT * FROM Direct_movie 
                WHERE DirectorId =  {} AND MovieId = {}
                '''.format(movie['director_id'], movie['movie_id'])
 

    try:
        cur.execute(statement)
        result = cur.fetchall()

    except:
        # print("Failed to fetch data")
        pass
  
    if result.__len__() == 0:

        statement = '''
        INSERT INTO Direct_movie (DirectorId, MovieId) 
        VALUES (?, ?) 
        '''
        insertion = (movie['director_id'], movie['movie_id'])

        try:
            cur.execute(statement,insertion)
            conn.commit()
            # print("Director direct movie data ADD to DB table direct_movie!")

        except:
            print("Failed to add to table direct_movie")
            conn.rollback()

    else:
        # print("This Director direct movie ALREADY EXISTED!!")
        pass
       




def store_actor_data_to_db(actor, movie):
    statement = '''SELECT * FROM Actors 
           WHERE Id = {}'''.format(actor['actor_id'])

    
    try:
        cur.execute(statement)
        result = cur.fetchall()

    except:
        # print("Failed to fetch data")
        pass


    
    if result.__len__() == 0:

        statement = '''
        INSERT INTO Actors 
        VALUES (?, ?)
        '''                  
        insertion =  (actor['actor_id'], actor['actor_name'])

        try:
            cur.execute(statement,insertion)
            conn.commit()
            # print("Actor data ADDED to DB table actors!")
        except Exception as e:
            print(e)
            conn.rollback()
    else:
        # print("This actor has been saved already.") 
        pass       
            

    statement = '''SELECT * FROM Cast_in_movie 
               WHERE ActorId =  {} AND MovieId = {}'''.format(actor['actor_id'], movie['movie_id'])
    try:
        cur.execute(statement)
        result = cur.fetchall()

    except:
        # print("Failed to fetch data")
        pass


    
    if result.__len__() == 0:

        statement = '''
        INSERT INTO Cast_in_movie (ActorId, MovieId)
        VALUES (?, ?)
        '''                 
        insertion = (actor['actor_id'], movie['movie_id'])

        try:
            cur.execute(statement,insertion)
            conn.commit()
            # print("Actor casted in movie data ADDED to DB table cast_in_movie!")
        except Exception as e:
            print(e)

            conn.rollback()
            

    else:
        # print("This actor casted in movie data already existed.")  
        pass      


if __name__ == '__main__':
    create_imdb()
    for movie in get_top250_movies_list():
        # print(movie)
        store_movie_data_to_db(movie)
        get_movie_detail_data(movie)
        # print(movie)



    conn.close()

