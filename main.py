from flask import Flask, redirect
from routes.auth import auth_routes
from routes.recommendation import recommendation_routes

app = Flask(__name__)
app.config.from_pyfile('config.py')

app.register_blueprint(auth_routes)
app.register_blueprint(recommendation_routes)



@app.route("/")
def index():
    return redirect("/login")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)