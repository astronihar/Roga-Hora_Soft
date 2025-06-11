from flask import Flask
from routes.main_routes import main_routes
from routes.home_routes import home_routes
from routes.anatomy_routes import anatomy_routes
from routes.charts_routes import charts_routes
from routes.dasha_routes import dasha_routes
from routes.transit_routes import transit_routes
from routes.api_location import api_location  # assuming you have a blueprint here too
import os


app = Flask(__name__)
app.secret_key = os.urandom(24)  




# Register Blueprints
app.register_blueprint(main_routes)
app.register_blueprint(home_routes)
app.register_blueprint(anatomy_routes)
app.register_blueprint(charts_routes)
app.register_blueprint(dasha_routes)
app.register_blueprint(transit_routes)
app.register_blueprint(api_location)

if __name__ == '__main__':
    app.run(debug=True)


