#!/usr/bin/python

import codecs
codecs.register(lambda name: codecs.lookup('utf-8') if name == 'cp65001' else None)

from rivescript import RiveScript

#rs = RiveScript(log='log.example', utf8=True)
rs = RiveScript(debug=False, utf8=True)
rs.bayes.train(u'music', u'changge tiaowu')

rs.load_directory("./brain_zh")
rs.sort_replies()

print """This is a bare minimal example for how to write your own RiveScript bot!

For a more full-fledged example, try running: `python rivescript brain`
This will run the built-in Interactive Mode of the RiveScript library. It has
some more advanced features like supporting JSON for communication with the
bot. See `python rivescript --help` for more info.

example.py is just a simple script that loads the RiveScript documents from
the 'brain/' folder, and lets you chat with the bot.

Type /quit when you're done to exit this example.
"""

while True:
    msg = raw_input("You> ")
    if msg == '/quit':
        quit()
    #print type(msg.decode('gbk').encode('utf-8'))
    #print type(msg)
    reply = rs.reply("localuser", msg)
    print "Bot>", reply

# vim:expandtab
