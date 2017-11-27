import json
import sys
import subprocess

ON_POSIX = 'posix' in sys.builtin_module_names

json_in = open(sys.argv[1], "r")
a = json.load(json_in)

suc = a['success']

frames = suc['frames']

command = ["./meanmax", "-test"]


class unit:

    def __init__(self):
        self.x = 0
        self.y = 0
        self.vx = 0
        self.vy = 0
        self.playerId = -1
        self.unitType = 0
        self.radius = 0
        self.mass = -1
        self.water = -1
        self.capacity = -1
        self.unitID = 0
        self.initX = 0
        self.initY = 0
        self.initVX = 0
        self.initVY = 0
        self.friction = 0

    def updateMass(self):
        if self.unitType == 0:
            self.mass = 0.5
        elif self.unitType == 1:
            self.mass = 1.5
        elif self.unitType == 2:
            self.mass = 1
        elif self.unitType == 3:
            self.mass = 2.5 + (self.water / 2)

    def setFriction(self):
        if self.unitType == 0:
            self.friction = 0.8
        elif self.unitType == 1:
            self.friction = 0.7
        elif self.unitType == 2:
            self.friction = 0.75
        elif self.unitType == 3:
            self.friction = 0.6

    def __repr__(self):
        self.updateMass()
        return " ".join(map(str, [self.unitID, self.unitType, self.playerId, self.mass, self.radius, self.x, self.y, self.vx, self.vy, self.water, self.capacity]))


class game:

    def __init__(self):
        self.radius_dict = {}
        self.unit_type = {}
        self.units = {}

    def parseUnit(self, unitstring):
        data = unitstring.split(" ")
        id = data[0].split("@")

        data = data[1:]
        if len(data) > 0 and data[len(data) - 1] == 'd':
            return ""
        # print(data)
        unitData = list(map(int, map(float, data)))
        un = unit()
        if id[0] in self.units:
            un = self.units[id[0]]
            if len(unitData) == 4:
                un.x = unitData[0]
                un.y = unitData[1]
                un.vx = round(unitData[2] * un.friction)
                un.vy = round(unitData[3] * un.friction)
                print(un.vx, unitData[2], un.friction * unitData[2])
            if un.unitType in [3, 4]:
                un.water = int(id[1])
        else:
            un.unitType = unitData[4]
            un.x = unitData[0]
            un.y = unitData[1]
            un.vx = unitData[2]
            un.vy = unitData[3]
            un.initX = unitData[0]
            un.initY = unitData[1]
            un.initVX = unitData[2]
            un.initVY = unitData[3]
            un.radius = unitData[5]
            if un.unitType == 4:
                un.water = int(id[1])
            if un.unitType == 3:
                un.water = int(id[1])
                un.capacity = 10
            if un.unitType < 3:
                un.playerId = unitData[6]
            un.setFriction()
            un.unitID = id[0]

        self.units[id[0]] = un
        return str(un)

    def parseOutput(self, outstring):
        lines = outstring.strip().split("\n")
        gameInput = []
        if lines[0] == '0':
            # discard useless starting data
            lines = lines[5:]
        lines = lines[1:]
        # first 6 lines are scores / rage
        for x in lines[:6]:
            gameInput.append(x)
        # skip an extra 9 lines as we don't care about shoutouts
        lines = lines[6 + 9:]
        while lines[0] != "#1.00000":
            # skip collisions
            if lines[0][0] != '#':
                self.parseUnit(lines[0])
            lines = lines[1:]
        lines = lines[1:]
        # print(lines, gameInput)
        gameInput.append(0)
        for x in lines:
            s = self.parseUnit(x)
            if s != "":
                gameInput.append(self.parseUnit(x))
                gameInput[6] = gameInput[6] + 1
        gameInput[6] = str(gameInput[6])
        return gameInput

    def parseInput(self, outstring):
        lines = outstring.strip().split("\n")

        return lines


class turn:

    def __init__(self):
        self.inputLines = []
        self.nextLines = []
        self.playerOutput = []
        self.water = []
        self.oil = []
        self.tar = []


g = game()
turns = []
nextturn = turn()
lastin = []
first = True
v = []
for f in frames:

    if 'stderr' in f and f['agentId'] == 0:
        v = g.parseInput(f['stderr'])
       # print(v)
        nextturn.nextLines = v
        if first:
            first = False
        else:
            turns.append(nextturn)
        nextturn = turn()
        nextturn.inputLines = v
    if 'stdout' in f:
        for o in f['stdout'].strip().split("\n"):
            o = " ".join(o.split(" ")[:3])
            nextturn.playerOutput.append(o)

for t in turns:
    valid = {}
    water = []
    tar = []
    oil = []
    for x in t.inputLines[7:]:
        v = x.split(" ")
        valid[v[0]] = True
    olines = []
    for x in t.nextLines[7:]:
        v = x.split(" ")

        if v[1] == "4":
            v[0] = "0"
            water.append(" ".join(v))
        elif v[1] == "5":
            v[0] = "0"
            tar.append(" ".join(v))
        elif v[1] == "6":
            v[0] = "0"
            oil.append(" ".join(v))
        elif v[0] in valid and int(v[1]) < 4:
            olines.append(x)
    t.nextLines = t.nextLines[:6]
    t.nextLines.append(str(len(olines)))
    t.nextLines.extend(olines)
    t.water = water
    t.oil = oil
    t.tar = tar


def offBy1(a, b):
    v = a.split(" ")
    z = b.split(" ")
    error = True
    for i in range(0, len(v)):
        if i < 5:
            if v[i] != z[i]:
                return False
        elif i < 9:
            vv = int(v[i])
            zz = int(z[i])
            if abs(vv - zz) > 1:
                return False
        else:
            if v[i] != z[i]:
                return False
    return True


def outputTurn(t, dest):
    for x in t.inputLines:
        print(x, file=dest)
    for x in t.playerOutput:
        print(x, file=dest)


def getGame(out):
    game = out[:6]
    out = out[6:]
    v = int(out[0])
    game.extend(out[:1 + v])
    out = out[1 + v:]
    # water
    v = int(out[0])
    game.extend(out[:1 + v])
    out = out[1 + v:]
    # tar
    v = int(out[0])
    game.extend(out[:1 + v])
    out = out[1 + v:]
    # oil
    v = int(out[0])
    game.extend(out[:1 + v])
    out = out[1 + v:]
    return game, out


def inputTurn(t, out):
    outline = 0
    error = False
    for i in range(0, len(t.nextLines)):
        if out[outline].strip() != t.nextLines[i].strip():
            print("ERROR line", i + 1)
            print("EXP: ", t.nextLines[i])
            print("REC: ", out[i])
            if offBy1(out[outline].strip(), t.nextLines[i].strip()):
                print("OFF BY 1")
            else:
                error = True
        if outline < (len(out) - 1):
            outline += 1

    if (out[outline]) != str(len(t.water)):
        print("ERROR Water Count")
        print("EXP: ", len(t.water))
        print("REC: ", out[outline])
        error = True
    if outline < (len(out) - 1):
        outline += 1
    for x in t.water:
        if outline == len(out):
            error = True
            continue
        if out[outline].strip() != x.strip():
            print("ERROR line", i + 1)
            print("EXP: ", x)
            print("REC: ", out[outline])
            error = True
        outline += 1

    if (out[outline]) != str(len(t.tar)):
        print("ERROR tar Count")
        print("EXP: ", len(t.tar))
        print("REC: ", out[outline])
        error = True
    if outline < (len(out) - 1):
        outline += 1
    for x in t.tar:
        if outline == len(out):
            error = True
            continue
        if out[outline].strip() != x.strip():
            print("ERROR line", i + 1)
            print("EXP: ", x)
            print("REC: ", out[outline])
            error = True
        outline += 1

    if (out[outline]) != str(len(t.oil)):
        print("ERROR Oil Count")
        print("EXP: ", len(t.oil))
        print("REC: ", out[outline])
        error = True
    if outline < (len(out) - 1):
        outline += 1
    for x in t.oil:
        if outline == len(out):
            error = True
            continue
        if out[outline].strip() != x.strip():
            print("ERROR line", i + 1)
            print("EXP: ", x)
            print("REC: ", out[outline])
            error = True
        outline += 1
    return error

turnsout = len(turns)
turnCount = 0
while turnCount < len(turns):

    simulator_pid = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     bufsize=20, universal_newlines=True)
    tout = min(turnsout, 2)
    print(tout, file=simulator_pid.stdin)
    for i in range(0, tout):
        outputTurn(turns[turnCount + i], simulator_pid.stdin)

    out, err = simulator_pid.communicate()
    out = out.strip().split("\n")
    # for x in out:
    #    print(x, file=sys.stderr)
    for i in range(0, tout):
        game, out = getGame(out)
        t = turns[turnCount + i]
        error = inputTurn(t, game)
        if error:
            print("1", file=sys.stderr)
            for x in t.inputLines:
                print(x, file=sys.stderr)
            for x in t.playerOutput:
                print(x, file=sys.stderr)
            for x in t.nextLines:
                print(x, file=sys.stderr)
            print(len(t.water), file=sys.stderr)
            for x in t.water:
                print(x, file=sys.stderr)
            for x in out:
                print(x, file=sys.stderr)
            exit(0)
        print("VALID")
    turnsout -= tout
    turnCount += tout
    # else:
    #    print("REC: ", out[i])
