#!/usr/bin/python

import re
from flask import Flask, jsonify, render_template, request

from rivescript import RiveScript
from rivescript import sentences

rs = RiveScript(debug=False, utf8=True)
rs.load_directory("./brain_zh")
rs.sort_replies()
rs.train()

app = Flask(__name__)

@app.route('/reply')
def get_reply():
    user = re.sub(ur'\W', '', request.remote_addr)
    print user
    line = request.args.get('l','')

    user = user.strip()
    res = []
    req = []
    if user != '':
        for msg,ask in sentences(line):
            if  msg.strip() == '':
                continue
            reply = rs.reply(user, msg, ask)
            req.append(msg)
            res.append(reply)
    return jsonify(req=req, reply=res)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run('0.0.0.0', '9000')

