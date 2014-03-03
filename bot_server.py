#!/usr/bin/python

from flask import Flask, jsonify, render_template, request

from rivescript import RiveScript
from rivescript import sentences

rs = RiveScript(debug=False, utf8=True)
rs.load_directory("./brain_zh")
rs.sort_replies()

# Only have to train once
#rs.train_topics()

app = Flask(__name__)

@app.route('/reply')
def get_reply():
    print 'hear'
    user = request.args.get('u','')
    print user
    line = request.args.get('l','')

    user = user.strip()
    res = []
    if user != '':
        for msg in sentences(line):
            if  msg.strip() == '':
                continue
            reply = rs.reply(user, msg)
            res.append(reply)
    print res
    return jsonify(result=res)

@app.route('/')
def index():
    print 'index'
    return render_template('index.html')

if __name__ == '__main__':
    app.run('0.0.0.0', '9000')

