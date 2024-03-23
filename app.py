# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template, Response,url_for,redirect
import requests
import json
import os

app = Flask(__name__)

# 从配置文件中settings加载配置
app.config.from_pyfile('settings.py')

object=None
begin=0
check=0

# @app.route("/", methods=["GET"])
# def index():
#     return render_template("chat.html")

@app.route('/')
def home():
    return render_template('index.html')

# @app.route('/chat1')
# def chat1():
#     return redirect(url_for('main'))


@app.route("/chat", methods=["GET","POST"])
def chat():
    if request.method == "GET":
        # 处理 GET 请求的逻辑，可能是返回一个页面或者其他内容
        return render_template("chat.html")
    elif request.method == "POST":
        global begin
        global object
        messages = request.form.get("prompts", None)
        apiKey = request.form.get("apiKey", None)
        model = request.form.get("model", "gpt-3.5-turbo")
        """show_list=messages.split("}")
        object=show_list[begin][55:-1]
        begin+=2
        url = "https://api.zhishuyun.com/midjourney/imagine?token=1e0242a1b5534eb8a2663fc2fcf5778e"
    
        headers1 = {
            "content-type": "application/json"
        }
    
        payload = {
            "prompt": object,
            "translation": True
        }
        response = requests.post(url, json=payload, headers=headers1)
        picture = response.json()["image_url"]"""
        if messages is None:
            return jsonify({"error": {"message": "请输入prompts！", "type": "invalid_request_error", "code": ""}})

        if apiKey is None:
            apiKey = os.environ.get('OPENAI_API_KEY',app.config["OPENAI_API_KEY"])

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {apiKey}",
        }

        # json串转对象
        prompts = json.loads(messages)

        data = {
            "messages": prompts,
            "model": model,
            "max_tokens": 1024,
            "temperature": 0.5,
            "top_p": 1,
            "n": 1,
            "stream": True,
        }

        try:
            resp = requests.post(
                url=app.config["URL"],
                headers=headers,
                json=data,
                stream=True,
                timeout=(10, 10)  # 连接超时时间为10秒，读取超时时间为10秒
            )
        except requests.exceptions.Timeout:
            return jsonify({"error": {"message": "请求超时，请稍后再试！", "type": "timeout_error", "code": ""}})

        # 迭代器实现流式响应
        def generate():
            errorStr = ""
            for chunk in resp.iter_lines():
                if chunk:
                    streamStr = chunk.decode("utf-8").replace("data: ", "")
                    try:
                        streamDict = json.loads(streamStr)  # 说明出现返回信息不是正常数据,是接口返回的具体错误信息
                    except:
                        errorStr += streamStr.strip()  # 错误流式数据累加
                        continue
                    delData = streamDict["choices"][0]
                    if delData["finish_reason"] != None :
                        break
                    else:
                        if "content" in delData["delta"]:
                            respStr = delData["delta"]["content"]
                            # print(respStr)
                            yield respStr

            # 如果出现错误，此时错误信息迭代器已处理完，app_context已经出栈，要返回错误信息，需要将app_context手动入栈
            if errorStr != "":
                with app.app_context():
                    yield errorStr
        return Response(generate(), content_type='application/octet-stream')

if __name__ == '__main__':
    app.run(port=5000,debug=True)
