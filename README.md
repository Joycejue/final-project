# final-project
1. Data Source

I use data scraping from IMDb web pages.
API keys or client secrets are not needed.

-----------------------------------------------------------------------------------------------------------------------
2. Other information

I use Plotly in my project to present some outcomes.
This is the link about how to get started with Plotly with Python: https://plot.ly/python/getting-started/

-----------------------------------------------------------------------------------------------------------------------
3. Brief description of structure of code

(1). Data access and storage: 
"data_access_storage.py" works for data scraping and crawling from web pages and storaging into the database.

Main functions are:
create_imdb(): Create IMDB.db and tables in it.
get_top250_movies_list(): Scrap info from https://www.imdb.com/chart/top

store_movie_data_to_db(movie_data): Store data scraping by using "get_top250_movies_list()" to the table "Top_250_movies".

get_movie_detail_data(movie_data): Scrap info from web pages; Separated into two parts, storing data into director related tables "Directors", "Actors" and actor related tables "Direct_movie", "Cast_in_movie".

(2). Data processing:
"process_data.py" works for data processing, interaction and presentation.

Main functions are:
interactive_prompt(): For interactive purpose; In this function, class and fuctions will be called depending on the user's  input.

The required one class:
class Director_movie(): This class takes results from other functions as input, and generates instances related to directors and movies.

Many other functions are in the file, but not listed here.

-----------------------------------------------------------------------------------------------------------------------
4.Brief user guide
You can enter "help" for all available commands and user guide.

Thanks! :)


