# -*- coding: utf-8 -*-

import os
import configparser
import socket

rootPath = os.path.dirname(__file__)
configPath = os.path.join(rootPath, "config.ini")

conf = configparser.ConfigParser()


class Config(object):
    class server(object):
        name = socket.gethostname()+"-LFT-Server"
        ip = "0.0.0.0"
        port = "6981"
        save_path = os.path.join(os.getcwd(), "receive")

    class client(object):
        ip = "127.0.0.1"
        port = "6981"


def initConfig():
    with open(configPath, "w") as f:
        conf.read(configPath)
        if not conf.has_section("server"):
            conf.add_section("server")
        conf.set("server", "name", socket.gethostname()+"-LFT-Server")
        conf.set("server", "ip", "0.0.0.0")
        conf.set("server", "port", "6981")
        conf.set("server", "save_path", os.path.join(os.getcwd(), "receive"))
        if not conf.has_section("client"):
            conf.add_section("client")
        conf.set("client", "ip", "127.0.0.1")
        conf.set("client", "port", "6981")
        conf.write(f)


def readConfig():
    if not os.path.isfile(configPath) or os.path.getsize(configPath) == 0:
        initConfig()
        return
    conf.read(configPath)
    Config.server.name = conf.get("server", "name")
    Config.server.ip = conf.get("server", "ip")
    Config.server.port = conf.get("server", "port")
    Config.server.save_path = conf.get("server", "save_path")
    Config.client.ip = conf.get("client", "ip")
    Config.client.port = conf.get("client", "port")


def saveConfig():
    with open(configPath, "w") as f:
        conf.read(configPath)
        conf.set("server", "name", Config.server.name)
        conf.set("server", "ip", Config.server.ip)
        conf.set("server", "port", Config.server.port)
        conf.set("server", "save_path", Config.server.save_path)
        conf.set("client", "ip", Config.client.ip)
        conf.set("client", "port", Config.client.port)
        conf.write(f)
