require("m711lib")

print("gamemode has been loaded")

OnPlayerConnect = function(playerid)
	local playername = GetPlayerName(playerid)
	SendAllPlayersMessage(playername.." has joined the game.")
	SendPlayerMessage(playerid, string.format("Welcome to the server %s.", playername))
	ShowPlayerDialog(playerid, 0, "Login", "Write down your username please.", "Okay")
end
OnPlayerText = function(playerid,text)
	return 1 --return (-1) to prevent the text from being sent.
end