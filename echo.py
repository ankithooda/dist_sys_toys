#!/usr/bin/env python3

import json
import sys


class EchoServer:

    def __init__(self, node_id=None):

        self.node_id = node_id
        self.msg_counter = 0

    def send_reply(self, req_payload, body):

        # {src: "n1",
        #  dest: "c1",
        #  body: {msg_id: 123
        #         in_reply_to: 1
        #         type: "init_ok"}}


        # Construct reply body
        reply_msg = {'body': {}}
        reply_msg['id'] = self.msg_counter
        reply_msg['src'] = self.node_id
        reply_msg['dest'] = req_payload['src']
        reply_msg['body'] = body

        # Add the reply type
        sys.stderr.write(json.dumps(reply_msg) + "\n")
        sys.stdout.write(json.dumps(reply_msg) + "\n")
        sys.stdout.flush()
        
        # Increment message counter.
        self.msg_counter = self.msg_counter + 1

    def handle_init(self, payload):
        self.node_id = payload['body']['node_id']
        sys.stderr.write(f"Initialized node with id {self.node_id}" + "\n")

        body = {
            "in_reply_to": payload['body']['msg_id'],
            "type": "init_ok"
        }
        self.send_reply(payload, body)

    def handle_echo(self, payload):
        sys.stderr.write("Replying to Echo")

        body = json.loads(json.dumps(payload['body']))

        # set correct type for echo reply messages
        body['type'] = "echo_ok"
        body['in_reply_to'] = payload['body']['msg_id']
        self.send_reply(payload, body)

    def run(self):
        for line in sys.stdin:
            try:
                payload = json.loads(line)
                sys.stderr.write(f"Got {str(payload)}\n")
                if payload['body']['type'] == "init":
                    self.handle_init(payload)
                elif payload['body']['type'] == "echo":
                    self.handle_echo(payload)
                else:
                    sys.stderr.write("\nSome other message type received \n")
            except Exception as e:
                sys.stderr.write(str(e))

e = EchoServer()
e.run()
clownworld_