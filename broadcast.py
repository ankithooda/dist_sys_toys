#!/usr/bin/env python3

from enum import Enum
import json
import sys


class MessageType(Enum):
    """ENum representing different types of Maelstrom message types.
    """
    INIT = "init"
    INIT_OK = "init_ok"
    ECHO = "echo"
    ECHO_OK = "echo_ok"


class Node:
    """
    Node class represents a node in the broadcast system.
    """
    MSG_TYPES = {
        "INIT": "init",
        "INIT_OK": "init_ok",
        "ECHO": "echo",
        "ECHO_OK": "echo_ok"
    }


    def __init__(self, node_id=None, neighbours=None):
        """
        Args:
            node_id (any, optional): Unique ID assigned to the node. Defaults to None.
            neighbours (list, optional): List of Node IDs of neighbours. Defaults to None.
        """

        self.node_id = node_id
        self.neighbours = neighbours or []
        self.msg_counter = 0

    def send(self, dest, msg_body):
        """Sends a message on the wire (STDOUT).
        Message format
        {
            'id': Driven by msg_counter.
            'dest': Given by Callee
            'src': Sender Node ID
            'body': Given by callee.
        }

        Args:
            dest (any): ID of the destination node.
            msg_body (dict): Dict representing the message body.
        """

        msg = {
            'id': self.msg_counter,
            'dest': dest,
            'src': self.node_id,
            'body': msg_body
        }

        # Add the reply type
        sys.stderr.write(json.dumps(msg) + "\n")
        sys.stdout.write(json.dumps(msg) + "\n")
        sys.stdout.flush()
        # Increment message counter.
        self.msg_counter = self.msg_counter + 1


    def handle_init(self, payload):
        """Handles INIT message.
        See - https://github.com/jepsen-io/maelstrom/blob/main/doc/protocol.md

        Args:
            payload (dict): Request body of the init message received.
        """
        self.node_id = payload['body']['node_id']
        sys.stderr.write(f"Initialized node with id {self.node_id}" + "\n")

        body = {
            "in_reply_to": payload['body']['msg_id'],
            "type": MessageType.INIT_OK.value
        }
        self.send(payload['src'], body)

    def handle_echo(self, payload):
        """Handles ECHO message.
        See - https://github.com/jepsen-io/maelstrom/blob/main/doc/protocol.md

        Args:
            payload (dict): Request body of the ECHO message.
        """
        sys.stderr.write("Replying to Echo")

        body = json.loads(json.dumps(payload['body']))

        # set correct type for echo reply messages
        body['type'] = MessageType.ECHO_OK.value
        body['in_reply_to'] = payload['body']['msg_id']
        self.send(payload['src'], body)

    def run(self):
        """Run the event loop.
        """
        for line in sys.stdin:
            try:
                payload = json.loads(line)
                sys.stderr.write(f"Got {str(payload)}\n")
                if payload['body']['type'] == MessageType.INIT.value:
                    self.handle_init(payload)
                elif payload['body']['type'] == MessageType.ECHO.value:
                    self.handle_echo(payload)
                else:
                    sys.stderr.write("\nSome other message type received \n")
            except Exception as loop_exception:
                sys.stderr.write(str(loop_exception))

e = Node()
e.run()
