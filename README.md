# FlipkartReview-Scrapper
This is a scrapper for scraping text reviews from flipkart website. It internally connects to MongodB database and stores the fetched results in the database table. When a new query is made, the application first checks whether reviews for the query exists in database, if yes then reviews are fetched from the database and displayed to the user in web browser. If not, then the application searches for the reviews on flipkart websites, downloads html and searches tags using BeautifulSoup and extracts the relevant information and then it adds that to the database as well as displays on the browser.

# Main Page
![Alt Text](https://github.com/Sachin-Bharadwaj/FlipkartReview-Scrapper/blob/master/output/MainPage.png)
Lets say you entered shirts as query in above text page.

# results shown to user in browser
![Alt Text](https://github.com/Sachin-Bharadwaj/FlipkartReview-Scrapper/blob/master/output/SearchResults.png)

# This app is live on Heroku
[LiveAppLink](https://fkart-reviewscrapper.herokuapp.com/)
Note, I have removed database part from the app which is deployed on Heroku. If you want you enable it and set uo your herou account to have access to MongodB. In absence of any database, the app directly queries the flipkart site and dislays the scraped reviews on the browser.
