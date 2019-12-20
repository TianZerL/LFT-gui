# -*- coding: utf-8 -*-

import subprocess
from threading import Thread
from queue import Queue, Empty


def LFTSend(src, ip, port="6981"):
    LFT = subprocess.Popen(args=["LFT", "-d", src, "-ip", ip, "-port",
                                 port], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    if LFT.wait() == 0:
        return "send successfully"
    else:
        err = LFT.stderr.readlines()[-1].strip().decode("utf-8").split(" ")
        err = " ".join(err[2:])
        return err


def LFTScan(infoChan, ips, ports="6981"):
    LFT = subprocess.Popen(args=["LFT", "-scan", "-ip", ips, "-port",
                                 ports], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    while LFT.poll() is None:
        lineData = LFT.stdout.readline().strip().decode('utf-8')
        if lineData:
            infoChan.put(lineData.split("   "))
    infoChan.put("__finished__")


def LFTServer(infoChan, controlChan, ip="0.0.0.0", port="6981", name="LFT-Server", savePath="./receive"):
    LFT = subprocess.Popen(args=["LFT", "-w", "-ip", ip, "-port", port,
                                 "-name", name, "-d", savePath], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    q = Queue()
    reader = Thread(target=readLine, args=(LFT.stderr, q))
    reader.daemon = True
    reader.start()
    while LFT.poll() is None:
        try:
            line = q.get_nowait()
            infoChan.put(line.split(" "))
        except Empty:
            pass
        if not controlChan.empty():
            LFT.terminate()
    infoChan.put("__finished__")


def readLine(out, q):
    for line in iter(out.readline, b''):
        q.put(line.strip().decode('utf-8'))
