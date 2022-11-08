# importing required libraries
from flask import Flask, render_template, url_for, request
from werkzeug.utils import secure_filename
import os
from recognizer import get_output

# instantiating the flask application
app = Flask(__name__)

# allowing only specified image files
ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "svg"]
# folder path to store the uploaded image
UPLOAD_FOLDER = "static/images/"

# configuring application
app.secret_key = os.urandom(24)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def is_allowed_file(filename: str) -> bool:
    """
    Checking the upload file is valid or not
    """
    return ("." in filename) and (
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# routes to home page
@app.route("/")
def index():
    return render_template("index.html")


# routes to recognize page
@app.route("/recognize", methods=["GET", "POST"])
def recognize():
    alert_box_color = "dark"
    display_output = None
    uploaded_img_path = None
    back_url = url_for("static", filename="icons/back.svg")

    if request.method == "POST":
        file = request.files["file"]
        if file and is_allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            image_url = url_for("static", filename=f"images/{file.filename}")
            output = get_output(path=image_url[1:])

            if len(output) > 1:
                output = list(map(str, output))
                display_output = f"Recognized digits are {', '.join(output)}"
                uploaded_img_path = image_url[1:]
            else:
                display_output = f"Recognized digit is {output[0]}"
                uploaded_img_path = image_url[1:]

        else:
            alert_box_color = "danger"
            display_output = f"Choosen file format is not supported. Choose only {', '.join(ALLOWED_EXTENSIONS)} images."

    return render_template(
        "recognize.html",
        back_url=back_url,
        alert_box_color=alert_box_color,
        display_output=display_output,
        uploaded_img_path=uploaded_img_path,
    )


if __name__ == "__main__":
    app.run(debug=True)
