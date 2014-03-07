#!/usr/bin/python

from rivescript import RiveScript
from rivescript import sentences

#rs = RiveScript(log='log.example', utf8=True)
rs = RiveScript(debug=False, utf8=True)
rs.load_directory("./brain_zh")
rs.sort_replies()

rs.train()

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
    s = raw_input("You> ")
    if s == '/quit':
        quit()
    for msg, is_ask in sentences(s):
        if  msg.strip() == '':
            continue
        reply = rs.reply("localuser", msg, is_ask)
        print "Bot>", reply

# vim:expandtab
