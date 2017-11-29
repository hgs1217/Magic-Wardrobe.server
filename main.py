# @Author:      HgS_1217_
# @Create Date: 2017/11/20

from flask import Flask, request, jsonify, send_from_directory, abort
from config import UPLOAD_IMAGE_FOLDER, UPLOAD_VIDEO_FOLDER, ALLOWED_IMAGE_EXTENSIONS, \
    ALLOWED_VIDEO_EXTENSIONS, SOCKET_HOST, SOCKET_PORT, SOCKET_REPLY_PATH
import os
import time
import socket
import codecs


app = Flask("ClothesImageProcessing")
app.secret_key = "sjtu"


def allowed_img(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_IMAGE_EXTENSIONS


def allowed_video(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_VIDEO_EXTENSIONS


def socket_communication(cmd):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(cmd, (SOCKET_HOST, SOCKET_PORT))


def get_socket_reply():
    with codecs.open("E:/a.txt", "r", encoding="gbk") as f:
        return f.read()


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


@app.route("/socket/posture", methods=['GET'])
def posture_analysis():
    gender = request.args.get("gender")
    tp = request.args.get("type")
    img_url = request.args.get("imgUrl")
    cmd = ";".join(["2", gender, tp, img_url]) + ";"

    try:
        socket_communication(cmd)
        reply = get_socket_reply()

        [x, y, w, h] = reply.split(";")[0:4]
        dic = {"x": x, "y": y, "width": w, "height": h, "error": 0, "msg": "Posture analysis success"}
        return jsonify(dic), 200
    except:
        dic = {"error": 2, "msg": "Posture analysis error"}
        return jsonify(dic), 404


@app.route("/socket/once_search", methods=['GET'])
def once_search():
    gender = request.args.get("gender")
    tp = request.args.get("type")
    img_url = request.args.get("imgUrl")
    x = request.args.get("x")
    y = request.args.get("y")
    width = request.args.get("width")
    height = request.args.get("height")
    alo = request.args.get("alo")
    cmd = ";".join(["0", gender, tp, x, y, width, height, img_url, alo]) + ";"

    try:
        socket_communication(cmd)
        reply = get_socket_reply()

        reply_list = reply[:-1].split(";")
        h, s, v, attr_num = reply_list[0], reply_list[1], reply_list[2], reply_list[3]
        attrs = reply_list[4:4+attr_num]
        imgs = reply_list[4+attr_num:]
        img_list = list(zip(*[iter(imgs)]*3))
        img_dics = [{"imgUrl": img[0], "imgWidth": img[1], "imgHeight": img[2]} for img in img_list]

        dic = {"h": h, "s": s, "v": v, "attrs": attrs, "images": img_dics,
               "error": 0, "msg": "Once search success"}
        return jsonify(dic), 200
    except:
        dic = {"error": 3, "msg": "Once search error"}
        return jsonify(dic), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
