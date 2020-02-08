import socket
from threading import Thread
import pickle
import time
import math
from configparser import ConfigParser
import lupa

print("Launching the server...")

class Server:
    def __init__(self, hostname,gamemode, language, port, maxplayers, rconpassword, password):
        self.hostname = hostname
        self.gamemode = gamemode
        self.language = language
        self.port = port
        self.maxplayers = maxplayers
        self.rconpassword = rconpassword
        self.password = password
        print(f"{self.hostname} has been successfuly launched on {port} with {maxplayers} max player count.")

lua = lupa.LuaRuntime(unpack_returned_tuples=True)
config = ConfigParser()

try:
    config.read('server_config.ini')
    shs=config.get("main", "hostname")
    sl=config.get("main", "language")
    sp=config.get("main", "port")
    smp=config.get("main", "maxplayers")
    srp=config.get("main", "rconpassword")
    sps=config.get("main","password")
    sgm=config.get("main","gamemode")
except:
    print("Config file doesn't exist or lacks keys.")
    quit()

#
SOUTH = 0
WEST = 1
NORTH = 2
EAST = 3

def GetTheDistanceBetweenTwoPoints(x,y,x1,y1):
    return math.sqrt(((x-x1)**2)+((y-y1)**2))

class Player:
    def __init__(self, ID,IDINT,NAME, IP, HEALTH, X,Y,team,skin):
        self.id = ID
        self.idint = IDINT
        self.name = NAME
        self.ip = IP
        self.Health = HEALTH
        self.x = X
        self.y = Y
        self.score = 0
        self.direction = SOUTH
        self.team = team
        self.skin = skin
        self.admin = False
    def GetPlayerPosition(self):
        return self.x,self.y
    def GetPlayerName(self):
        return self.name
    def GetPlayerHealth(self):
        return self.Health
    def GetPlayerIp(self):
        return self.ip
    def GetPlayerScore(self):
        return self.score
    def printInformation(self):
        print("Name: " + self.name + " IP: " + str(self.ip) + " Health: " + str(self.Health) + " X: " +str(self.x) +" Y: "+str(self.y))
    def IsInRangeOfPoint(self, range, x,y):
        R=GetTheDistanceBetweenTwoPoints(self.x, self.y, x,y)
        if(R <= range):
            return True
        else:
            return False
clients = []

IP = '127.0.0.1'
PORT = 8545
s = socket.socket()
s.bind((IP,PORT))
s.listen(50)
s.settimeout(0.0001)
s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
def CommunicateWithPlayer(__client__):
    while True:
        try:
            message = __client__.id.recv(1024).decode("UTF-8")
            pText = message[1:]
            if(message[0] == 'A'):
                __client__.x+=5 #right
                __client__.direction = EAST
                UpdatePlayers()

            elif(message[0] == 'B'):
                __client__.x-=5 #left
                __client__.direction = WEST
                UpdatePlayers()

            elif(message[0] == 'C'):
                __client__.y+=5 #down
                __client__.direction = SOUTH
                UpdatePlayers()

            elif(message[0] == 'D'):
                __client__.y-=5 #up
                __client__.direction = NORTH
                UpdatePlayers()

            elif(message[0] == 'E'):
                r=lua.eval(f'OnPlayerText({__client__.idint}, {pText})')
                if(r != -1):
                    pMessage = f'{__client__.name}: {pText}'
                    SendAllPlayersMessage(pMessage)
                    print(pMessage)
        except:
            pass

def UpdatePlayers():
    players = []
    for client in clients:
        playerDict = {'type': 'player', 'id':client.idint,'name': client.name, 'X': client.x, 'Y':client.y, 'H':client.Health, 'S':client.score, 'D': client.direction}
        players.append(playerDict)
    obj = pickle.dumps(players)
    for c in clients:
        c.id.send(obj)

def HandleConnections():
    while True:
        try:
            client, address = s.accept()
            client.setblocking(0)
            name = client.recv(500)
            for p in clients:
                if(p.name == name):
                    client.close()
                    break
            else:
                player = Player(client, len(clients),name.decode('UTF-8'), address, 100.0, 15, 15, 0,0)
                player.printInformation()
                clients.append(player)
                thread = Thread(target=CommunicateWithPlayer, args=[player])
                thread.start()
                print(player.name + " has connected. IP: " + str(player.ip))
                lua.eval(f"OnPlayerConnect({player.idint})")
                time.sleep(1.2)
                UpdatePlayers()
        except:
            pass

#SERVER FUNCTIONS
def SendAllPlayersMessage(message):
    message = f'$F{message}£'
    for client in clients:
        client.id.sendall(message.encode('UTF-8'))

def GetPlayerName(playerid):
    name = ''
    for client in clients:
        if(client.idint == playerid):
            name = client.name
            break
    return name

def SendPlayerMessage(playerid,message):
    message = f'$F{message}£'
    for client in clients:
        if(client.idint == playerid):
            client.id.sendall(message.encode('UTF-8'))
            break

def SetPlayerTeam(playerid, teamid):
    for client in clients:
        if(client.idint == playerid):
            client.team = teamid
            break

def SetPlayerSkin(playerid, skinid):
    for client in clients:
        if(client.idint == playerid):
            client.skin == skinid
            break

def SetPlayerAdmin(playerid, a):
    for client in clients:
        if(client.idint == playerid):
            client.admin = a
            print(f'{client.name} is now a server administrator.')
            break

def KickPlayer(playerid):
    for client in clients:
        if(client.idint == playerid):
            client.id.close()
            clients.remove(client)
            break

def GetPlayerIp(playerid):
    ip = ''
    for client in clients:
        if(client.idint == playerid):
            ip = client.GetPlayerIp()
            break
    return ip

def ShowPlayerDialog(playerid, dialogid,type, title, content,button1,button2):
    time.sleep(0.1)
    for client in clients:
        if(client.idint == playerid):
            dialogcode = f"$W{type}{dialogid}{title}語{content}語{button1}語{button2}£"
            client.id.sendall(dialogcode.encode('UTF-8'))
            break

if(__name__=='__main__'):
    ConnectionHandler = Thread(target=HandleConnections)
    ConnectionHandler.start()

server = Server(shs,sgm,sl,sp,smp,srp,sps)

lua.execute(open(server.gamemode,'r').read())