import unittest
from data_access_storage import *
from process_data import *





class TestDataAccess(unittest.TestCase):


    def number_in_top250_list(self):
        count = 0
        for m in get_top250_movies_list():
            count += 1
        return count

    def get_cast(self,url):
        
        html = make_request_using_cache(url)
        soup = BeautifulSoup(html, 'html.parser')
        cast = soup.find('table', class_="cast_list").find_all("tr")
        name = []
        for actor in get_cast_data(cast):
            name.append(actor["actor_name"])

        return name



    def get_director_name(self,moviename):

        for movie in get_top250_movies_list():
            if movie["movie_name"] == moviename:
                dname = get_movie_detail_data(movie)["director_name"]
                dborn = get_movie_detail_data(movie)["BornCountry"]
        return dname, dborn

    def test_basic_search(self): 
        #test web page for ecah level is correctly scrapped
        self.assertEqual(self.number_in_top250_list(), 250) #there should be 250 movies on the list
        self.assertEqual(self.get_cast(url = "https://www.imdb.com/title/tt0109830/?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=e31d89dd-322d-4646-8962-327b42fe94b1&pf_rd_r=KSD910G8WZXF1V9V13PP&pf_rd_s=center-1&pf_rd_t=15506&pf_rd_i=top&ref_=chttp_tt_12")[0], "Tom Hanks")
        self.assertEqual(self.get_director_name("Forrest Gump")[0], "Robert Zemeckis")
        self.assertEqual(self.get_director_name("Forrest Gump")[1], "USA")





class TestStorage(unittest.TestCase):

    def test_top_205_movies_table(self):
        conn = sqlite3.connect("IMDb.db")
        cur = conn.cursor()
      
        statement  = ''' SELECT Title FROM Top_250_movies '''
        results = cur.execute(statement)
        result_list = results.fetchall()
        self.assertIn(("The Help",), result_list)
        self.assertEqual(len(result_list), 250)

        statement  = ''' SELECT Title, Id, NumberofUserRatings FROM Top_250_movies WHERE ReleaseYear=2016 ORDER BY Title'''
        results = cur.execute(statement)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 4)
        self.assertIn(("La La Land",3783958,365430), result_list)
        self.assertEqual(result_list[1][0], "Hacksaw Ridge")

        conn.close()


    def test_directors_table(self):
        conn = sqlite3.connect("IMDb.db")
        cur = conn.cursor()
      
        statement  = '''SELECT Name, BornCountry, Id FROM Directors ORDER BY Name'''
        results = cur.execute(statement)
        result_list = results.fetchall()
        self.assertEqual(result_list[1][0], "Adam Elliot")
        self.assertEqual(result_list[3][1], "Mexico")
        self.assertEqual(result_list[0][2], 451148)
        

        conn.close()


    def test_actors_table(self):
        conn = sqlite3.connect("IMDb.db")
        cur = conn.cursor()
      
        statement  = '''SELECT Name, Id FROM Directors ORDER BY Name'''
        results = cur.execute(statement)
        result_list = results.fetchall()
        self.assertEqual(result_list[5][0], "Andrei Tarkovsky")
        self.assertEqual(result_list[6][1], 4056)

        conn.close()


    def test_direct_movie_tabel(self):
        conn = sqlite3.connect("IMDb.db")
        cur = conn.cursor()
      
        statement  = '''SELECT Id, DirectorId, MovieId FROM Direct_movie ORDER BY Id'''
        results = cur.execute(statement)
        result_list = results.fetchall()
        self.assertEqual(result_list[5][0], 6)
        self.assertEqual(result_list[10][1], 1392)
        self.assertIn((78,485,22100), result_list)
        self.assertEqual(len(result_list), 250)


        conn.close()


    def test_cast_movie_table(self):
        conn = sqlite3.connect("IMDb.db")
        cur = conn.cursor()
      
        statement  = '''SELECT CastId, ActorId, MovieId FROM Cast_in_movie ORDER BY CastId'''
        results = cur.execute(statement)
        result_list = results.fetchall()
        self.assertEqual(result_list[20][0], 21)
        self.assertEqual(result_list[10][1], 321358)
        self.assertIn((24,504803,68646),result_list)
        self.assertEqual(len(result_list), 3544)

        conn.close()

            
        
        
class TestProcess(unittest.TestCase):

    def test_top_actor(self):
        self.assertEqual(len(top_actor("top",5)), 5)
        self.assertEqual(top_actor("top",5)[0][0], "Robert De Niro")
        self.assertEqual(top_actor("top",6)[4], ("Tom Hanks", 6))
        
        


class TestPlot(unittest.TestCase):

    def test_charts(self):
        try:
            params_dic_1 = {"order":"top","limit":3}
            result_1 = top_director(**params_dic_1)
            bar_charts_director(result=result_1,name="test director bar chart" , title="test director bsr chart")

            params_dic_2 = {"order":"top","limit":5}
            result_2 = top_actor(**params_dic_2)
            bar_charts_actor(result = result_2, name = "test actor bar chart", title = "test actor bar chart")

            top_country_pie_chart(input_number=10, name="test country pie chart")

            line_chart_year(input_number=18, name="test year line chart")



        except:
            self.fail()

         





if __name__ == '__main__':
    unittest.main()






