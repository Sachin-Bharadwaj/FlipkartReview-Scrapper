# This is a sample Python script.

from flask import Flask, render_template, request, jsonify
import pymongo
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
max_num_pages = 5  # maximum pages to fetch from external webpage
flipkartbase_url = 'http://www.flipkart.com'

def populate_dict(URL, searchString):
    '''
    :param URL
    :return:
    '''
    flag = False  # if this is set true, we will add None to dict for all keys
    try:
        req_data = requests.get(URL)
    except:
        if req_data.status_code != 200:
            print(f"page_{i} cannot be accessed, exiting!")
        return None, None

    review_soup = BeautifulSoup(req_data.content, 'html.parser')  # home page review soup

    ########## add  reviews ########################################
    try:
        # find_all returns a list, below rating is a list with all matched html tags
        all_rev = review_soup.find_all('div', {'class': 'qwjRop'})  # find_all works on html elements, not on list
        # NOTE bs4 method works on bs4 objects which are elements of the rating list, therefore iterate on the list
        all_rev = [e.get_text() for e in all_rev]
        all_rev = [e if e[0].isalpha() else e[1::] for e in all_rev]
        # in some of the pages, the reviews tag contains ratings as well

        ##########  add user ratings ################################## hGSR34 _1nLEql E_uFuv
        # find_all returns a list, below rating is a list with all matched html tags
        #rating = review_soup.find_all('div', {'class': ['hGSR34 E_uFuv', 'hGSR34 _1nLEql E_uFuv', \
        #                                                'hGSR34 _1x2VEC E_uFuv', 'hGSR34']})  # find_all works on html elements, not on list
        rating = review_soup.find_all('div', {'class': 'qwjRop'})
        if len(rating[0].find_all('div', {'class': 'hGSR34'})) > 0:
            rating_text = [e.find_all('div', {'class': 'hGSR34'})[0].get_text() for e in rating]
        else:
            rating = review_soup.find_all('div', {'class': ['hGSR34 E_uFuv', 'hGSR34 _1nLEql E_uFuv', \
                                                                'hGSR34 _1x2VEC E_uFuv']})
            rating_text = [e.get_text() for e in rating]

        # NOTE bs4 method works on bs4 objects which are elements of the rating list, therefore iterate on the list
        #rating_text = [e.get_text() for e in rating]

        ########## add  header ########################################
        # find_all returns a list, below rating is a list with all matched html tags
        headers = review_soup.find_all('p', {'class': '_2xg6Ul'})  # find_all works on html elements, not on list
        # NOTE bs4 method works on bs4 objects which are elements of the rating list, therefore iterate on the list
        headers_ = [e.get_text() for e in headers]
        if len(headers) == 0: # incase header is missing, assign review to header
            headers_ = all_rev

        ########## add  user name ########################################
        # find_all returns a list, below rating is a list with all matched html tags
        users_name = review_soup.find_all('div',
                                          {'class': 'row _2pclJg'})  # find_all works on html elements, not on list
        # NOTE bs4 method works on bs4 objects which are elements of the rating list, therefore iterate on the list
        users_name = [e.div.find_all('p')[0].get_text() for e in users_name]

        ########## add  date ########################################
        # find_all returns a list, below rating is a list with all matched html tags
        dates_ = review_soup.find_all('div', {'class': 'row _2pclJg'})
        # NOTE bs4 method works on bs4 objects which are elements of the rating list, therefore iterate on the list
        dates = [e.div.find_all('p')[1].get_text() for e in dates_]

        ########## add  thumbs up/down count ########################################
        # find_all returns a list, below rating is a list with all matched html tags
        thumbs_cnt = review_soup.find_all('span', {'class': '_1_BQL8'})  # find_all works on html elements, not on list
        thumbs_up = thumbs_cnt[0::2]
        thumbs_down = thumbs_cnt[1::2]
        # NOTE bs4 method works on bs4 objects which are elements of the rating list, therefore iterate on the list
        thumbs_up = [e.get_text() for e in thumbs_up]
        thumbs_down = [e.get_text() for e in thumbs_down]

        ########### add product name #########################################
        prod_name = searchString
    except:
        flag = True

    if len(rating_text) != len(thumbs_up):
        flag = True

    # populate dict
    if flag == False:
        number_of_dicts = len(all_rev)
        op = []
        for i in range(number_of_dicts):
            curr_dict = {'review': all_rev[i],
                        'ratings': rating_text[i],
                         'header': headers_[i],
                         'name': users_name[i],
                         'date': dates[i],
                         'thumbsup': thumbs_up[i],
                         'thumbsdown': thumbs_down[i],
                         'prod_name': prod_name
                         }
            op.append(curr_dict)
    else:
        op = None

    try:
        ## get the Full URL of the next page, a class=_3fVaIS
        next_partial_url = review_soup.find_all('a', {'class': '_3fVaIS'})

        Full_URL = flipkartbase_url + next_partial_url[-1].get(
            'href')  # taking next_partial_url[-1] because sometimes there are multiple tags of class _3fVaIS
    except:
        Full_URL = None

    return op, Full_URL


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # first get the search string from the form and replace spaces with empty char
        searchString = request.form['content'].replace(" ", "")

        # open database connection
        try:
            dbConn = pymongo.MongoClient("mongodb://localhost:27017/")
            # get the database handle
            db = dbConn['crawlerDB']  # connecting to the database called crawlerDB
            table = db[searchString]  # this the table we will use
            # Now, within this database search for table (collections) named searchString
            reviews = table.find({})  # eq. to import * from table
            if reviews.count() > 0:
                return render_template('results.html', reviews= reviews)

            else:
                # construct search query for flipkart
                flipkart_url = flipkartbase_url + "/search?q=" + searchString
                req_data = requests.get(flipkart_url)
                search_reviews = BeautifulSoup(req_data.content, 'html.parser')
                Full_URL = flipkart_url
                allusers_review = []

                # find div class = '_KigyA' and from there we can extract link for all the products for search query
                all_products = search_reviews.find_all('div',
                                                       {'class': '_KigyA'})  # all the products from this search query
                # all_products is bs4.element.ResultSet type and hence we can iterate over it
                for prod in all_products:
                    prod_url = flipkartbase_url + prod.find('a')['href']
                    # fetch the page
                    prod_page = requests.get(prod_url)
                    prod_page_soup = BeautifulSoup(prod_page.content, 'html.parser')
                    # from above page, find the hyperlink to access all reviews
                    try: # sometimes, NEXT link is not there if reviews are very less
                        prod_all_reviews_page_link = flipkartbase_url + prod_page_soup.find_all('div', {'class': 'swINJg'})[0].parent['href']
                        prod_all_reviews_page = requests.get(prod_all_reviews_page_link)
                        prod_all_reviews_page_soup = BeautifulSoup(prod_all_reviews_page.content, 'html.parser')
                        # Now we need to access the hyperlink associated with Next button and iterate over pages
                        URL = prod_all_reviews_page_link
                    except:
                        URL = prod_url

                    finally:
                        for j in range(max_num_pages):
                            op, URL = populate_dict(URL, searchString)
                            if op is not None:
                                allusers_review.extend(op)
                            if URL == None: #  no more pages available
                                break

                # once all reviews are collected, insert the reviews in database
                table.insert_many(allusers_review)
                return render_template('results.html', reviews=allusers_review)  # showing the review to the user


        except:
            return 'Database connection cannot be opened, something is wrong!'

    else:  # it not a post method, show the main page (index.html)
        return render_template('index.html')



if __name__ == '__main__':
    app.config["DEBUG"] = True
    app.run('localhost', port=8010)
