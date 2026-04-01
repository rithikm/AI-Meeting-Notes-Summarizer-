#Refrences:
# https://flask.palletsprojects.com/en/stable/patterns/fileuploads/
# https://flask.palletsprojects.com/en/stable/api/#flask.json.jsonify

from flask import Flask, request, jsonify, Blueprint
from werkzeug.utils import secure_filename
import os 
from ai_agents import process_audio

# Create a Flask Blueprint to modularize upload-related routes.
# This allows to register this route the app.py file 
fileUpload = Blueprint("fileUpload",__name__)

#Intializing the Upload Folder which the audio recordings will be stored 
UPLOAD_FOLDER = "audio_uploads"
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a'}
#Having an Upload folder be created once the the application is runned 
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
#Check if the uploaded filename has a valid audio extension.
#Returns True if the file extension is allowed, otherwise False.
def allowed_files(filename) :
    return '.' in filename and  filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


#Created an app route which handles the upload functionality of the application through POST methods. 
@fileUpload.route("/upload",methods=["POST"])
#Created am audio_upload file which handles the  
def audio_upload() :
    # Ensure audio file is included in the request.
    if 'audio' not in request.files :
        return jsonify({"error": "No audio files were uploaded"}),400
    
    file = request.files['audio']
    # Check if the user submitted a file without a filename.
    if file.filename == '' :
        return jsonify({"error": "Audio file was not selected"}),400
    # Validate the file and ensure the extension is allowed.
    if file and allowed_files(file.filename) :
        # Sanitize the filename to prevent security issues (e.g. path traversal).
        filename = secure_filename(file.filename)
        # Create the full path where the file will be saved.
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        # Save the uploaded file to the server.
        file.save(filepath)
    
        # Process the audio file using the custom AI processing function.
        # Expected output: dict with keys "transcript" and "analysis".
        try :
            result = process_audio(filepath)
            # Return successful JSON response with AI-generated results.
            return jsonify({
                "status" : "success",
                "transcript" : result["transcript"],
                "analysis" : result["analysis"]
                })
        except Exception as e :
            # Catch any errors during audio processing and return as internal server error.
            return jsonify({"error" : str(e)}),500
    else :
        # File extension is not supported.
        return jsonify({"error": "Unsupported file type"}), 400





