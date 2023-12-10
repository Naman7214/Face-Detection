from flask import Flask, render_template, request, redirect, url_for
import cv2
import os
from mtcnn.mtcnn import MTCNN

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_faces(image_path, result_path):
    detector = MTCNN()
    image = cv2.imread(image_path)
    result_image = image.copy()

    faces = detector.detect_faces(image)

    for face in faces:
        x, y, w, h = face['box']
        cv2.rectangle(result_image, (x, y), (x+w, y+h), (255, 0, 0), 2)

    face_count = len(faces)
    cv2.imwrite(result_path, result_image)
    return face_count

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            return redirect(url_for('result', filename=file.filename))

    return render_template('upload.html')

@app.route('/result/<filename>')
def result(filename):
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    result_path = os.path.join('static', 'result', filename)

    face_count = detect_faces(image_path, result_path)

    return render_template('result.html', filename=filename, face_count=face_count)

if __name__ == '__main__':
    app.run(debug=True)
