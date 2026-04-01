from flask import Flask, render_template
from ai_backend import fileUpload

#Intialized the Flask application 
app = Flask(__name__)

#Calling the fileUpload Blueprint handled in the Flask API backend 
app.register_blueprint(fileUpload, url_prefix="/fileUpload")

#Created a default route which handles displaying the webpage credentials 
@app.route("/")
def default() :
     return render_template("index.html")

#Starting the application 
if __name__ == "__main__" :
  app.run(debug=True,use_reloader=False)