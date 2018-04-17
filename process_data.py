import sqlite3 
import plotly.plotly as py
from prettytable import PrettyTable
import plotly.graph_objs as go




def search_movies_by_director():
    DBNAME = 'IMDb.db'


    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Failed to connect to db.")

    input_DireName = ""


    while input_DireName=="" or input_DireName.isspace():
        input_DireName = input("Which director would you like to search for? ")





    statement_movies_by_specificDire = '''
        SELECT Top_250_movies.Title, Directors.Name, Directors.BornCountry
        FROM Top_250_movies 
        JOIN Direct_movie
        ON Direct_movie.MovieId = Top_250_movies.Id
        JOIN Directors
        ON Direct_movie.DirectorId = Directors.Id
        WHERE Directors.Name LIKE "{}"

    '''.format("%{}%".format(input_DireName))

    cur.execute(statement_movies_by_specificDire)
    conn.commit()
    
    result = cur.fetchall()
    if result.__len__() == 0:
        result_tuple_1 = ()
        return result_tuple_1

    else:
        director_specific_name = result[0][1]
        director_born_country = result[0][2]
        movie_name_list = []
        for row in result:
            director_specific_name = row[1]
            director_born_country = row[2]
            movie_name_list.append(row[0])
            

        conn.close()

        result_tuple_1 = (director_specific_name, director_born_country, movie_name_list)

        return result_tuple_1



def movie_details_by_director(input_DireName):
    DBNAME = 'IMDb.db'


    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Failed to connect to db.")

    # input_DireName = input("Which director would you like to search for? ")


    statement = '''
        SELECT Top_250_movies.Title, Top_250_movies.ReleaseYear, round(Top_250_movies.Rate,2)
        FROM Top_250_movies 
        JOIN Direct_movie
        ON Direct_movie.MovieId = Top_250_movies.Id
        JOIN Directors
        ON Direct_movie.DirectorId = Directors.Id
        WHERE Directors.Name LIKE "{}"

    '''.format("%{}%".format(input_DireName))


    cur.execute(statement)
    conn.commit()
    
    
    movie_detail_list = []
    for row in cur:
        movie_detail_list.append(row)
        

    conn.close()

    result_2 =  movie_detail_list
   
    return result_2





class Director_movie():
    def __init__(self, result_1, result_2):

        self.name = result_1[0]
        self.born = result_1[1]
          
        self.name_of_movie = result_1[2] #list
        self.number_of_movie = len(self.name_of_movie)
        self.movies = result_2 #a list
        
         

    def __str__(self):
        return "{} ({}): {} movies on the Top 250 list.".format(self.name, self.born, self.number_of_movie)



def search_actor():
    DBNAME = 'IMDb.db'


    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Failed to connect to db.")

    input_ActorName = ""


    while input_ActorName=="" or input_ActorName.isspace():
        input_ActorName = input("Which Actor would you like to search for? ")


    statement = '''
        SELECT Top_250_movies.Title, Top_250_movies.ReleaseYear, round(Top_250_movies.Rate,2),Actors.Name
        FROM Top_250_movies 
        JOIN Cast_in_movie
        ON Cast_in_movie.MovieId = Top_250_movies.Id
        JOIN Actors
        ON Cast_in_movie.ActorId = Actors.Id
        WHERE Actors.Name LIKE "%{}%"
    '''.format("%{}%".format(input_ActorName))


    cur.execute(statement)
    conn.commit()
    
    result = cur.fetchall()

    if result.__len__() == 0:
        result_tuple = ()
        return result_tuple

    else:
        actor_specific_name = result[0][-1]
        
        movie_list = []
        for row in result:
            movie_list.append(row[:-1])
            

        conn.close()

        result_tuple = (actor_specific_name, movie_list)

        return result_tuple





class Actor_movie():
    def __init__(self, result):

        self.name = result[0]          
        self.movies = result[1] #list
        self.number_of_movie = len(self.movies)
        
    def __str__(self):
        return "{} : {} movies on the Top 250 list.".format(self.name, self.number_of_movie)




def top_director(order, limit):
    DBNAME = 'IMDb.db'

    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Failed to connect to db.")


    if order != "bottom":
        p_order = "DESC"
    else:
        p_order = ""
    
    if limit == "": 
        p_limit = 10
    else:
        p_limit = limit    



    statement_top_directors = '''
            SELECT d.Name, count(dm.DirectorId) as direct_count
            FROM Direct_movie as dm
            JOIN Directors as d ON d.Id = dm.DirectorId
            GROUP by dm.DirectorId
            HAVING d.Name <> "Unknown" 
            ORDER by direct_count {}
            LIMIT {}
    '''.format(p_order,p_limit)

    cur.execute(statement_top_directors)
    conn.commit()

    result = cur.fetchall()
    
    cur.close()
    return result
    




def top_actor(order, limit):
    DBNAME = 'IMDb.db'

    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
    except:
        print("Failed to connect to db.")


    if order != "bottom":
        p_order = "DESC"
    else:
        p_order = ""
    
    if limit == "": 
        p_limit = 10
    else:
        p_limit = limit    


    statement_top_actors = '''
            SELECT a.Name, count(cm.ActorId) as count_of_act
            FROM Cast_in_movie as cm
            JOIN Actors as a ON a.Id = cm.ActorId
            GROUP by cm.ActorId
            HAVING a.Name <> "Unknown"
            ORDER by count_of_act {}
            LIMIT {}
    '''.format(p_order,p_limit)

    cur.execute(statement_top_actors)
    conn.commit()

    result = []
    for row in cur:
        if row[0] != "Unknown":
            result.append(row)
    
    return result
    





def bar_charts(result,name,title):
    


    key = []
    va = []
    for i in result:
        key.append(i[0])
        va.append(i[1])
    


    dataset = {'x':key,
            'y1': va}

    data_g = []

    tr_y1 = go.Bar(
        x = dataset['x'],
        y = dataset['y1'],
        name = 'v1',
        text=dataset['y1'],
                textposition = 'auto',
                marker=dict(
                    color='rgb(158,202,225)',
                    line=dict(
                        color='rgb(8,48,107)',
                        width=1.5),
                ),
                opacity=0.6
      )
    
    data_g.append(tr_y1)


    layout = go.Layout(title=title, xaxis={'title':'Director Name'}, yaxis={'title':'Number of Movies'})

    fig = go.Figure(data=data_g, layout=layout)

    py.plot(fig, filename=name)




def parse_command(response):

    params_dic = {}
    if "bottom" in response:
        params_dic["order"] = "bottom"
        try:
            p = response.index("bottom")
            index = p + 1
            params_dic["limit"] = response[index] 
        except:
            params_dic["limit"] = 10   
    elif "top" in response:
        params_dic["order"] = "top"
        try:
            p = response.index("top")
            index = p + 1
            params_dic["limit"] = response[index]
        except:
            params_dic["limit"] = 10    
    else:
        params_dic["order"] = "top"
        params_dic["limit"] = 10

    return params_dic





def load_help_text():
    with open('help.txt') as f:
        return f.read()




def interactive_prompt():

    help_text = load_help_text()
    response = ''
    while response != 'exit':
        response = input('Enter a command: ')
        
        if response.lower() == 'help':
            print(help_text)
            continue

        elif response.lower() == 'search director':
            result_1 = search_movies_by_director()
            
            if len(result_1)==0:
                print("This director is not on the Top 205 list.")

            else:

                result_2 = movie_details_by_director(result_1[0])
                instance = Director_movie(result_1,result_2)
                print(instance)  #use the str method of the Class

                title = []
                releaseyear = []
                rate = []
                
                for t in instance.movies:
                    # print(t)
                    title.append(t[0])
                    releaseyear.append(t[1])
                    rate.append(t[2])
                    
                col = PrettyTable()
                col.add_column("Movie Title", title)
                col.add_column("Release Year", releaseyear)
                col.add_column("Rate", rate)
                col.align = 'l'
                # col.border = 0
                print(col)
            

        elif response.lower() ==  "search actor":
            result = search_actor()

            if len(result) == 0:
                print("This actor is not on the Top 205 list.")
            
            else:
                instance = Actor_movie(result)
                print(instance)

                title = []
                releaseyear = []
                rate = []
                
                for t in instance.movies:
                    # print(t)
                    title.append(t[0])
                    releaseyear.append(t[1])
                    rate.append(t[2])
                    
                col = PrettyTable()
                col.add_column("Movie Title", title)
                col.add_column("Release Year", releaseyear)
                col.add_column("Rate", rate)
                col.align = 'l'
                # col.border = 0
                print(col)


        elif response.lower().split()[0] == "director":
            
            response = response.split()
            result = top_director(**parse_command(response))

            name = []
            count = []                
            for t in result:
                # print(t)
                name.append(t[0])
                count.append(t[1])
                
            col = PrettyTable()
            col.add_column("Director Name", name)
            col.add_column("Movie Count", count)
            col.align = 'l'
            # col.border = 0
            print(col)


        elif response.lower().split()[0] == "actor":
            response = response.split()
            result = top_actor(**parse_command(response))


            name = []
            count = []                            
            for t in result:
                # print(t)
                name.append(t[0])
                count.append(t[1])
                
            col = PrettyTable()
            col.add_column("Director Name", name)
            col.add_column("Movie Count", count)
            col.align = 'l'
            # col.border = 0
            print(col)

                

        elif response.lower() == "top directors bar chart":
            number = int(input("How many? "))
            params_dic = {"order":"top","limit":number}
            result = top_director(**params_dic)
            bar_charts(result = result, name = "Top {} Directors Bar Chart".format(number), title = "Top {} Directors Bar Chart".format(number))


        elif response.lower() == "exit":
            print("Bye!")


       
        else:
            print('''Oops! Command not recognized: \"{}\"\nPlease enter a correct command.'''.format(response))
           








if __name__=="__main__":
    interactive_prompt()










