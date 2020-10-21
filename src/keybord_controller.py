#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import time
import _thread
import json
from bottle import *


DEV_PATH = r'/dev/hidg0'
NULL_CHAR = chr(0)
keyboard = {}
keyboard["a"] = chr(4)
keyboard["b"] = chr(5)
keyboard["c"] = chr(6)
keyboard["d"] = chr(7)
keyboard["e"] = chr(8)
keyboard["f"] = chr(9)
keyboard["g"] = chr(10)
keyboard["h"] = chr(11)
keyboard["i"] = chr(12)
keyboard["j"] = chr(13)
keyboard["k"] = chr(14)
keyboard["l"] = chr(15)
keyboard["m"] = chr(16)
keyboard["n"] = chr(17)
keyboard["o"] = chr(18)
keyboard["p"] = chr(19)
keyboard["q"] = chr(20)
keyboard["r"] = chr(21)
keyboard["s"] = chr(22)
keyboard["t"] = chr(23)
keyboard["u"] = chr(24)
keyboard["v"] = chr(25)
keyboard["w"] = chr(26)
keyboard["x"] = chr(27)
keyboard["y"] = chr(28)
keyboard["z"] = chr(29)
keyboard["1"] = chr(30)
keyboard["2"] = chr(31)
keyboard["3"] = chr(32)
keyboard["4"] = chr(33)
keyboard["5"] = chr(34)
keyboard["6"] = chr(35)
keyboard["7"] = chr(36)
keyboard["8"] = chr(37)
keyboard["9"] = chr(38)
keyboard["0"] = chr(39)
keyboard[" "] = chr(44)
keyboard[","] = chr(54)
keyboard["."] = chr(55)
keyboard["-"] = chr(45)
keyboard[";"] = chr(51)
keyboard["'"] = chr(52)
keyboard["\n"] = chr(40)
keyboard["\t"] = chr(43)
keyboard["enter"] = chr(40)
keyboard["backspace"] = chr(42)
keyboard["uparrow"] = chr(82)
keyboard["downarrow"] = chr(81)
keyboard["leftarrow"] = chr(80)
keyboard["rightarrow"] = chr(79)
keyboard["shift"] = chr(32)
keyboard["ctrl"] = chr(16)


def bin_to_str(s):
    return ''.join([chr(i) for i in [int(b, 2) for b in s.split(' ')]])


class kbManager:
    def __init__(self):
        self.write_report = [NULL_CHAR for _ in range(8)]
        self.keyboard_stause = {}
        for key in keyboard:
            self.keyboard_stause[key] = -1
        self.fd = open(DEV_PATH, 'rb+')

    def write(self):
        char = self.write_report[0]
        for i in range(1, 8):
            char += self.write_report[i]
        print(char.encode())
        self.fd.write(char.encode())
        self.fd.flush()

    def down(self, key):
        if key not in keyboard:
            print("illegal key", key)
            return
        index_range = None
        cg_flag = False
        if key == "ctrl" or key == "shift":
            index_range = range(1)
        else:
            index_range = range(2, 8)
        for i in index_range:
            self.keyboard_stause[key] = -1
            if self.write_report[i] == NULL_CHAR:
                self.keyboard_stause[key] = i
                self.write_report[i] = keyboard[key]
                cg_flag = True
                break
        if cg_flag:
            self.write()

    def up(self, key):
        if key not in keyboard:
            print("illegal key", key)
            return
        if self.keyboard_stause[key] != -1:
            self.write_report[self.keyboard_stause[key]] = NULL_CHAR
            self.write()

    def _close(self):
        self.fd.write((NULL_CHAR*8).encode())
        self.fd.close()


interrupt_flag = False
running_flag = False


def run_script(script):
    global interrupt_flag, running_flag
    if running_flag == True:
        return
    randomSleep = 0
    km = kbManager()
    running_flag = True

    def run_once():
        for action in script["actions"]:
            time.sleep(random.uniform(0, randomSleep))
            if action[0] == "press":
                km.down(action[1])
            elif action[0] == "release":
                km.up(action[1])
            elif action[0] == "sleep":
                time.sleep(random.uniform(action[1], action[2])/1000)
            else:
                print("illegal type")
    if script["insertRandom"] == True:
        randomSleep = 0.01
    if script["loop"] == True:
        while not interrupt_flag:
            run_once()
        interrupt_flag = False
    else:
        run_once()
    running_flag = False
    km._close()


script = None


@route('/setScript', method='POST')
def setScript():
    global script
    data = json.loads(request.body.read())
    script = data
    print(data)
    return json.dumps(data)


@route('/runScript', method='GET')
def setScript():
    global interrupt_flag
    if script is None:
        return "no script available"
    elif running_flag == True:
        return "a script is already running"
    else:
        interrupt_flag = False
        _thread.start_new_thread(run_script, (script,))
        return "script is now running"


@route('/interrupt', method="GET")
def interrupt():
    global interrupt_flag
    interrupt_flag = True
    return "script will be interrupted next loop"


# @route('/exit', method="GET")
# def exit():
#     global interrupt_flag, running_flag
#     interrupt_flag = True
#     while running_flag:
#         print("waiting for script to exit")
#         time.sleep(1)
#     exit()


@route('/stause')
def stause():
    global script, interrupt_flag, running_flag

    return json.dumps({
        "interrupt_flag": interrupt_flag,
        "running_flag": running_flag,
        "script": script
    })


@route('/')
def index():
    return '''
    <!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="maximum-scale=1.0,minimum-scale=1.0,user-scalable=no,
        width=device-width,initial-scale=1.0" />
    <title>Document</title>
    <script type="text/javascript">
        var script = ""
        function print(str) {
            document.getElementById("resultTextarea").value = str;
        }


        function stause() {
            fetch('./stause', {
                method: 'GET',
                credentials: "include",
                mode: 'cors',
                cache: 'no-store'
            }).then(response => response.text())
                .then(data => print(data))
                .catch(err => print(err))
        }
        function setScript() {
            var str = document.getElementById("scriptInput").value;
            try {
                JSON.parse(str);
                fetch('./setScript', {
                    method: 'POST',
                    body: str,
                    mode: 'cors',
                    cache: 'no-store'
                }).then(response => response.text())
                    .then(data => print(data))
                    .catch(err => print(err))
            } catch (e) {
                document.getElementById("resultTextarea").value = "脚本格式错误"
            }
        }
        function runScript() {
            fetch('./runScript', {
                method: 'GET',
                credentials: "include",
                mode: 'cors',
                cache: 'no-store'
            }).then(response => response.text())
                .then(data => print(data))
                .catch(err => print(err))
        }
        function interrupt() {
            fetch('./interrupt', {
                method: 'GET',
                credentials: "include",
                mode: 'cors',
                cache: 'no-store'
            }).then(response => response.text())
                .then(data => print(data))
                .catch(err => print(err))
        }
    </script>
    <style type="text/css">
        .container {
            display: flex;
            flex-direction: column;
        }

        .button_container {
            margin: 20px 10px;
            width: 392px;
            height: 60px;
        }

        .scriptInput {
            width: 392px;
            height: 540px;
            border: 1px solid black;
            border-radius: 6px;
            resize: none;
            outline: none;
        }

        .resultTextarea {
            width: 392px;
            height: 180px;
            border: 1px solid black;
            border-radius: 6px;
            resize: none;
            outline: none;
        }

        button {
            width: 80px;
            height: 40px;
            color: #ffffff;
            background-color: #C2185B;
            border: 1px solid #C2185B;
            background-color: #C2185B;
            border-radius: 6px;
            transition: 0.5s;
            outline: none;
        }

        button:hover {
            background-color: #c45d86;
            border: 1px solid #c45d86;
            background-color: #c45d86;
            transition: 0.2s;
        }

        button:active {
            height: 30px;
            /* width: 60px; */
        }
    </style>
</head>

<body>
    <div class="container">
        <textarea class="scriptInput" id="scriptInput" type="text"></textarea>
        <div class="button_container">
            <button onclick=stause()>状态</button>
            <button onclick=setScript()>上传脚本</button>
            <button onclick=runScript()>开始执行</button>
            <button onclick=interrupt()>中断</button>
        </div>
        <textarea readonly class="resultTextarea" id="resultTextarea" type="text"></textarea>
    </div>
</body>

</html>'''


run(host='0.0.0.0', port=8003, reloader=False)
