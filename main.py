# @Author:      HgS_1217_
# @Create Date: 2017/11/20

from flask import Flask, request, jsonify, send_from_directory, abort
from config import UPLOAD_IMAGE_FOLDER, UPLOAD_VIDEO_FOLDER, ALLOWED_IMAGE_EXTENSIONS, ALLOWED_VIDEO_EXTENSIONS
import os
import time


app = Flask("ClothesImageProcessing")
app.secret_key = "sjtu"


def allowed_img(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_IMAGE_EXTENSIONS


def allowed_video(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_VIDEO_EXTENSIONS


@app.route('/')
def main():
    return "Welcome"


@app.route("/upload/img", methods=['POST'])
def upload_img():
    file = request.files['image']
    if file and allowed_img(file.filename):
        current_time = time.localtime()
        filename = time.strftime("%Y%m%d%H%M%S", current_time) + '.' + file.filename.rsplit('.', 1)[1]
        path = UPLOAD_IMAGE_FOLDER + "/" + filename
        file.save(path)
        dic = {"fileName": filename, "path": path, "error": 0, "msg": "Upload file success"}
        return jsonify(dic), 200
    dic = {"error": 1, "msg": "file error or unsupported file format"}
    return jsonify(dic), 404


@app.route("/upload/video", methods=['POST'])
def upload_video():
    file = request.files['file']
    if file and allowed_video(file.filename):
        current_time = time.localtime()
        filename = time.strftime("%Y%m%d%H%M%S", current_time) + '.' + file.filename.rsplit('.', 1)[1]
        path = UPLOAD_VIDEO_FOLDER + "/" + filename
        file.save(path)
        dic = {"fileName": filename, "path": path, "error": 0, "msg": "Upload file success"}
        return jsonify(dic), 200
    dic = {"error": 1, "msg": "file error or unsupported file format"}
    return jsonify(dic), 404


@app.route("/img/<img_path>", methods=['GET'])
def get_img(img_path):
    if os.path.isfile(img_path):
        dirs = img_path.split("/")
        folder, img_name = "/".join(dirs[:-1]), dirs[-1]
        return send_from_directory(folder, img_name, as_attachment=True)
    abort(404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)