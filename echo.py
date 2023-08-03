#!/usr/bin/env python3

import json
import sys


class EchoServer:

    def __init__(self, node_id=None):

        self.node_id = node_id
        self.msg_counter = 0

    def send_reply(self, payload, reply_type):

        # {src: "n1",
        #  dest: "c1",
        #  body: {msg_id: 123
        #         in_reply_to: 1
        #         type: "init_ok"}}

        # Increment message counter first.
        self.msg_counter = self.msg_counter + 1

        # Construct reply body
        reply_msg = {'body': {}}
        reply_msg['src'] = self.node_id
        reply_msg['dest'] = payload['src']
        reply_msg['body']['msg_id'] = self.msg_counter
        reply_msg['body']['in_reply_to'] = payload['id']

        # Add the reply type
        reply_msg['body']['type'] = reply_type

        sys.stderr.write(json.dumps(reply_msg) + "\n")
        sys.stdout.write(json.dumps(reply_msg) + "\n")

    def reply_to_init(self, payload):
        self.node_id = payload['body']['node_id']
        self.send_reply(payload, "init_ok")

    def run(self):
        for line in sys.stdin:
            try:
                payload = json.loads(line)

                sys.stderr.write("\n" + str(payload) + "\n")

                if payload['body']['type'] == "init":
                    self.reply_to_init(payload)
                    
                else:
                    sys.stderr.write("\nSome other message type received \n")

                sys.stderr.write("\nDONE.\n")

            except Exception as e:
                sys.stderr.write(str(e))

e = EchoServer()
e.run()
