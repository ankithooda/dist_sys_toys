#!/usr/bin/env python3

from copy import deepcopy
from enum import Enum
import json
import sys


class MessageType(Enum):
    """Enum representing different types of Maelstrom message types.
    """
    INIT = "init"
    INIT_OK = "init_ok"
    ECHO = "echo"
    ECHO_OK = "echo_ok"
    TOPOLOGY = "topology"
    TOPOLOGY_OK = "topology_ok"
    BROADCAST = "broadcast"
    BROADCAST_OK = "broadcast_ok"
    READ = "read"
    READ_OK = "read_ok"


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
        self.messages = []

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
        body = json.loads(json.dumps(payload['body']))

        # set correct type for echo reply messages
        body['type'] = MessageType.ECHO_OK.value
        body['in_reply_to'] = payload['body']['msg_id']
        self.send(payload['src'], body)

    def handle_topology(self, payload):
        """Handles TOPOLOGY message.
        See - https://github.com/jepsen-io/maelstrom/blob/main/doc/protocol.md

        Args:
            payload (dict): Request body of the TOPOLOGY message.
        """
        self.neighbours = payload['body']['topology'][self.node_id]
        sys.stderr.write(f"{self.node_id} intialized it's neighbours to {self.neighbours}")
        body = {
            'type': MessageType.TOPOLOGY_OK.value,
            'in_reply_to': payload['body']['msg_id']
        }
        self.send(payload['src'], body)

    def handle_broadcast(self, payload):
        """Handles BROADCAST message
        See - https://github.com/jepsen-io/maelstrom/blob/main/doc/workloads.md#workload-broadcast

        Args:
            payload (dict): Request body of BROADCAST message.
        """
        self.messages.append(payload['body']['message'])

        # Broadcast the message to neighbours
        # but without msg_id attribute
        for neighbour in self.neighbours:
            self.send(neighbour, {
                'type': MessageType.BROADCAST.value,
                'message': payload['body']['message']
            })

        # Reply to broadcast message
        if payload['body']['msg_id'] is not None:
            body = {
                'type': MessageType.BROADCAST_OK.value,
                'in_reply_to': payload['body']['msg_id']
            }
            self.send(payload['src'], body)

    def handle_read(self, payload):
        """Handles READ message
        See - https://github.com/jepsen-io/maelstrom/blob/main/doc/workloads.md#workload-broadcast

        Args:
            payload (dict): Request body of READ message.
        """
        body = {
            'type': MessageType.READ_OK.value,
            'in_reply_to': payload['body']['msg_id'],
            'messages': deepcopy(self.messages)
        }
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
                elif payload['body']['type'] == MessageType.TOPOLOGY.value:
                    self.handle_topology(payload)
                elif payload['body']['type'] == MessageType.BROADCAST.value:
                    self.handle_broadcast(payload)
                elif payload['body']['type'] == MessageType.READ.value:
                    self.handle_read(payload)
                else:
                    sys.stderr.write("\nSome other message type received \n")
            except Exception as loop_exception:
                sys.stderr.write(str(loop_exception))

e = Node()
e.run()
