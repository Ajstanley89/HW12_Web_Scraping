from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars

app = Flask(__name__)

# Use flask_pymongo to set up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)


# index route
@app.route('/')
def index():
    mars = mongo.db.mars.find_one()
    return render_template('index.html', mars=mars)
    
# Scraper route
@app.route ('/scrape')
def scraper():
    # Create mars db in Mongo db
    mars = mongo.db.mars

    # Scrape Data
    mars_data = scrape_mars.scrape()

    # Insert scraped data into Mongo db
    mars.update({}, mars_data, upsert=True)

    return redirect('/', code=302)

if __name__ == '__main__':
    app.run(debug=True)
