# -*- coding: utf-8 -*-

"""Manage your tailscale connections and toggle the status of your connections.

WIP: This extensions will allow you to control your local tailscale instance. \
Using the trigger "ts " will show a list of tailscale nodes in your network. \
Selecting one of them will copy their IP address to your clipboard. \

Synopsis: <trigger> [delay|throw] <query>"""

from albert import *
import os
from time import sleep

import json
import subprocess

from functools import total_ordering


__title__ = "Tailscale"
__version__ = "0.1.0"
__triggers__ = "ts "
__authors__ = "maxgallup"
#__exec_deps__ = ["whatever"]

iconPath = iconLookup("albert")


# Can be omitted
def initialize():
    pass


# Can be omitted
def finalize():
    pass


statusString = "Status: "
enabledEmoji = "✅"
disabledEmoji = "❌"
ownConnectionEmoji = "💻"

@total_ordering
class TailscaleNode:
    def __init__(self, name, ip, online, offersExit, usesExit, isSelf):
        self.name = name  
        self.ip = ip 
        self.online = online
        self.offersExit = offersExit
        self.usesExit = usesExit
        self.isSelf = isSelf

    def get_status_line(self):
        if (self.isSelf):
            statusIcon = ownConnectionEmoji
        elif (self.online):
            statusIcon = enabledEmoji
        else:
            statusIcon = disabledEmoji

        return statusIcon + " " + self.name + " " + self.ip
    
    def __eq__(self, n):
        return (self.online and n.online) or (not self.online and not n.online)

    def __gt__(self, n):
        return (not self.online and n.online)

    def __lt__(self, n):
        return (self.isSelf and not n.isSelf) or (self.online and not n.online)


def initNode(node, isSelf):
    return TailscaleNode(node["DNSName"].split(".")[0], node["TailscaleIPs"][0], node["Online"], node["ExitNodeOption"], node["ExitNode"], isSelf)

def tailscaleStatus():
    nodes = []
    raw = subprocess.check_output(['tailscale', 'status', '--json']).decode('utf-8')
    status = json.loads(raw)
    me = status["Self"]
    nodes.append(initNode(me, True))

    for peer in status["Peer"]:
        nodes.append(initNode(status["Peer"][peer], False))

    return nodes




def handleQuery(query):
    if not query.isTriggered:
        return

    
    results = []

    nodes = sorted(tailscaleStatus())


    for node in nodes:
        item = Item(id=__title__,
                    icon=os.path.dirname(__file__)+"/plugin.svg",
                    text=node.get_status_line(),
                    actions=[
                        ClipAction(text="Clipaction", clipboardText=node.ip)
                        ],
                    )
        results.append(item)


    return results



