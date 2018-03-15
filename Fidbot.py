# Python 3.6
# Author: twitch.tv/bastixx669 Github.com/bastixx
# based on a tutorial found here: https://www.youtube.com/watch?v=5Kv3_V5wFgg by Cynigo
#
# Created as a learning project for a small Twitch community!

import socket
import numbers
import string
import time
import threading
import random
import validators  # Needs installation!
from datetime import datetime, date
from inspect import currentframe, getframeinfo

# Set all the variables necessary to connect to Twitch IRC
HOST = "irc.twitch.tv"
NICK = b"testbot"
PORT = 6667
PASS = b"<INSERT OATH TOKEN>"
CHANNEL = b'<INSERT CHANNEL>'

# For debugging purposes
printline = False
printparts = False

# Connecting to Twitch IRC by passing credentials and joining a certain channel
s = socket.socket()
s.connect((HOST, PORT))
s.send(b"PASS " + PASS + b"\r\n")
s.send(b"NICK " + NICK + b"\r\n")
s.send(b"JOIN #" + CHANNEL + b"\r\n")
# Sending a command to make twitch return tags with each message
s.send(b"CAP REQ :twitch.tv/tags \r\n")


def read_files():
    global randomendings; global permitsystem; global authorisedusers; global bets; global timers
    try:
        with open('Endings.txt') as f:
            randomendings = f.readlines()
            randomendings = [x.strip('\n') for x in randomendings]
        with open('Permitsystem.txt') as f:
            permitsystem = f.read()
        with open('AuthUsers.txt') as f:
            authorisedusers = f.read().splitlines()
        with open('Quotes.txt') as f:
            for line in f:
                split = line.split(":")
                quotes[split[0]] = split[1].rstrip('\n')
        with open('Bets.txt') as f:
            for line in f:
                (key, val) = line.split(':')
                betfromfile = str(val)[:-1]
                bets[key] = betfromfile
                t = threading.Timer(int(betfromfile) * 60, announcer, [key, betfromfile])
                timers[key] = t
    except Exception as errormsg:
        print("Error importing from files!")
        print(errormsg)
        exit()


# Method for sending messages to the Twitch channel
def send_message(message):
    s.send(b"PRIVMSG #%s :%s\r\n" % (CHANNEL, message.encode()))
    print(">>BOT : " + message)


def announcer(displayname, bettime):
    global bets
    global timers
    try:
        ending = random.choice(randomendings)
        send_message("%s's time has come with %s minutes! %s" % (displayname, bettime, ending))
        # bets.pop(displayname)
        timers.pop(displayname)

    except Exception as errormsg:
        print("Error: " + str(errormsg))
        errorlog(errormsg, "announcer()")


def errorlog(error, functionname):
    frameinfo = getframeinfo(currentframe())
    with open('Errorlog.txt', 'a') as f:
        f.write("%s : %s : %s : %s\n" % (str(datetime.time(datetime.now())), str(functionname), str(frameinfo.lineno), str(error)))
        # f.write(str(datetime.time(datetime.now())) + " : " + str(functionname) + " : " + str(frameinfo.lineno) + " : " +
        #         str(error) + "\n")


def permit(user):
    global permitted
    permitted.remove(user)
    print("%s removed from permitted" % user)


def command_limiter(command):
    global comlimits
    comlimits.remove(command)
    print("%s removed from comlimits" % command)


def main():
    global timeractive
    global bets
    global timers
    global permitted
    global randomendings
    global comlimits
    global quotes
    global permitsystem
    # Setting of a lot of variables
    readbuffer = ""
    modt = False
    timeractive = False
    betsopen = False
    timercount = False
    timers = {}
    bets = {}
    permitted = []
    comlimits = []
    quotes = {}

    # Import stuff from storage files
    read_files()
    while True:
        readbuffer = readbuffer + s.recv(1024).decode()
        temp = str.split(readbuffer, "\n")
        readbuffer = temp.pop()

        for line in temp:
            if printline:
                print(line)
            # Checks whether the message is PING because its a method of Twitch to check if you're afk
            if "PING" in line:
                s.send(b"PONG\r\n")
                # print ">>>Pong send!"
                if bets != {}:
                    with open("Bets.txt", 'w') as f:
                        for key in bets:
                            f.write(key + ":" + str(bets[key]) + "\n")
                if betsopen:
                    if timercount:
                        send_message("Bets are opened! Use !bet <number> to place your bet.")
                        timercount = False
                    else:
                        timercount = True

            else:
                # Splits the given string so we can work with it better
                # partstemp = line.split("!")
                if modt and "ACK" not in line:
                    parts = line.split(" :", 2)
                else:
                    parts = line.split(":", 2)
                if printparts:
                    print(parts)
                if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PART" not in parts[1] and "ACK" not in parts[1]:
                    issub = False
                    ismod = False

                    try:
                        # Sets the message variable to the actual message sent
                        message = parts[2][:len(parts[2]) - 1]
                    except:
                        message = ""
                        # Sets the username variable to the actual username
                    usernamesplit = str.split(parts[1], "!")
                    username = usernamesplit[0]
                    displayname = username
                    tags = str.split(parts[0], ';')

                    # Get index of mod and sub status dynamically because tag indexes are not fixed
                    subindex = [i for i, z in enumerate(tags) if 'subscriber' in z]
                    modindex = [i for i, z in enumerate(tags) if 'mod' in z]
                    displayindex = [i for i, z in enumerate(tags) if 'display-name' in z]

                    # Only works after twitch is done announcing stuff (modt = Message of the day)
                    if modt:
                        try:
                            subindex = subindex[0]
                            modindex = modindex[0]
                            displayindex = displayindex[0]
                            if tags[displayindex] != 'display-name=':
                                displayname = tags[displayindex]
                                displayname = displayname.split("=")[1]
                        except:
                            pass

                        try:
                            if tags[subindex] == 'subscriber=1':
                                issub = True

                            if tags[modindex] == 'mod=1':
                                ismod = True
                        except Exception as errormsg:
                            errorlog(errormsg, "issub/ismod")

                        print(displayname + ": " + message)

                        # Permit system: Prevent links if activated unless permitted, subbed or a mod.
                        if validators.url("http://" + message) and validators.url("http://www." + message) \
                                and permitsystem == 'True':
                            if username not in permitted or issub or ismod:
                                send_message("/timeout " + displayname + " 1")
                                send_message("Please ask permission before posting links.")

                        # filters commands for efficiency
                        if message[0] == '!':
                            if message == "!test" and (username in authorisedusers or ismod):
                                send_message("Test successful!")

                            elif message == "!bonercommands":
                                send_message("The current commands can be found here: https://pastebin.com/yitr7Ds0 ")

                            elif message == "!starttimer" and (username in authorisedusers or ismod):
                                if timeractive:
                                    send_message("Timer already started!")
                                else:
                                    timeractive = True
                                    betsopen = False
                                    starttime = datetime.time(datetime.now())
                                    # Start all timer threads
                                    for t in list(timers.values()):
                                        t.start()
                                        print(t)
                                    send_message("The timer has been started. No more bets can be placed! "
                                                 "Good luck all!! fideli1Love ")

                            elif message == "!stoptimer" and (username in authorisedusers or ismod):  # stop de timer
                                if timeractive:
                                    timeractive = False
                                    for t in list(timers.values()):
                                        t.cancel()
                                    timers = {}
                                    timenow = datetime.time(datetime.now())
                                    # Calculates the time since timer started
                                    timer = datetime.combine(date.today(), timenow) - datetime.combine(date.today(),
                                                                                                       starttime)
                                    # Crude way to add the hours to the total minute count
                                    endtime = str(timer).split(':')[1]
                                    if str(timer).split(':')[0] == '1':
                                        endtime += (int(endtime) + 60)
                                    if str(timer).split(':')[0] == '2':
                                        endtime += (int(endtime) + 120)
                                    # calculate the closest bet to the endtime
                                    winningtime = int(min(bets.values(), key=lambda x: abs(int(x) - int(endtime))))

                                    # winningtime = min(list(bets.items()), key=lambda __v1: abs(int(__v1[1]) - int(endtime)))[1]
                                    print("winningtime: " + str(winningtime))
                                    try:
                                        # check if winningtime is within 5 minutes of the endtime
                                        if (int(endtime) - 5) <= winningtime <= (int(endtime) + 5):
                                            betval = list(bets.values())
                                            # Check if there are more winners. Slightly different code if there are
                                            # multiple peope with the same time
                                            if betval.count(str(winningtime)) > 1:
                                                winners = []
                                                for i in list(bets.items()):
                                                    if i[1] == str(winningtime):
                                                        winners.append(i[0])
                                                winnerstr = " and ".join(winners)
                                                print(winnerstr)
                                                send_message("Bones have been broken! The timer is on " +
                                                             endtime + " minute(s)! The winners are: " + winnerstr +
                                                             " with " + str(winningtime) + " minutes!")
                                                with open('PrevWinners.txt', 'a') as f:
                                                    for i in winners:
                                                        f.write(i + ":" + str(winningtime) + "\n")
                                                with open("Titleholder.txt", "w") as f:
                                                    f.write(winnerstr)
                                            else:
                                                winner = list(bets.keys())[list(bets.values()).index((str(winningtime)))]
                                                # winner = min(list(bets.items()),
                                                #              key=lambda __v: abs(int(__v[1]) - int(endtime)))
                                                send_message("Bones have been broken! The timer is on " +
                                                             endtime + " minute(s)! The winner is: " + winner +
                                                             " with " + str(winningtime) + " minutes!")
                                                with open('PrevWinners.txt', 'a') as f:
                                                    f.write(winner + ":" + str(winningtime) + "\n")
                                                with open("Titleholder.txt", "w") as f:
                                                    f.write(winner)
                                        else:
                                            send_message("Bones have been broken! The timer is on " +
                                                         endtime + " minutes. No bets are within 5 minutes of the "
                                                                   "timer. That means there is no winner this round!")
                                            bets = {}
                                        print("endtime: " + endtime)
                                        print("endtime - 5: " + str(int(endtime) - 5))
                                        print("endtime + 5: " + str(int(endtime) + 5))
                                        print("winning time: " + str(winningtime))
                                    except Exception as errormsg:
                                        print("Error: " + str(errormsg))
                                        errorlog(errormsg, message)
                                    else:
                                        with open('PrevBets.txt', 'a')as f:
                                            f.write("\n" + "Bets ended on: " + str(time.strftime("%x")) + " " +
                                                    str(time.strftime("%X")) + "\n")
                                            for key in bets:
                                                f.write(key + ":" + str(bets[key]) + "\n")
                                        bets = {}
                                        with open("Bets.txt", 'w') as f:
                                            f.write('')

                                else:
                                    send_message("There is currently no timer active!")

                            elif message == "!timer":  # shows current time on the timer
                                if timeractive:
                                    timenow = datetime.time(datetime.now())
                                    timer = datetime.combine(date.today(), timenow) - datetime.combine(date.today(),
                                                                                                       starttime)
                                    print(timer)
                                    timer = str(timer).split('.')[0]
                                    timersplit = timer.split(':')
                                    endtime = ":".join(timersplit)
                                    print(endtime)
                                    send_message("Fid has been alive for: " + endtime)
                                else:
                                    send_message("There is currently no timer active!")

                            elif message == "!resettimer" and (username in authorisedusers or ismod):
                                timeractive = False
                                betsopen = True
                                for t in list(timers.values()):
                                    t.cancel()
                                time.sleep(1)
                                timers = {}
                                send_message("Timer reset. Bets are now open again!")

                            elif message == "!fidwins" and (username in authorisedusers or ismod):
                                try:
                                    if timeractive:
                                        timeractive = False
                                        for t in list(timers.values()):
                                            t.cancel()
                                        time.sleep(1)
                                        timers = {}
                                        with open("Titleholder.txt", "w") as f:
                                            f.write("FideliasFK")
                                        timenow = datetime.time(datetime.now())
                                        timer = datetime.combine(date.today(), timenow) - datetime.combine(date.today(),
                                                                                                           starttime)
                                        endtime = str(timer).split(':')[1]
                                        if str(timer).split(':')[0] == '1':
                                            endtime += (int(endtime) + 60)
                                        if str(timer).split(':')[0] == '2':
                                            endtime += (int(endtime) + 120)
                                        send_message("The timer is on " + endtime + " minute(s)!")
                                        send_message("No boners have been broken this round. The winner is FideliasFK!")
                                        bets = {}
                                    else:
                                        send_message("There is no timer active!")
                                except Exception as errormsg:
                                    send_message("Error lettting fid win.")
                                    print("Error: " + str(errormsg))
                                    errorlog(errormsg, message)
                                else:
                                    with open('PrevBets.txt', 'a')as f:
                                        f.write("\n" + "Bets ended on: " + str(time.strftime("%x")) + " " +
                                                str(time.strftime("%X")) + "\n")
                                        for key in bets:
                                            f.write(key + ":" + str(bets[key]) + "\n")
                                    bets = {}
                                    with open("Bets.txt", 'w') as f:
                                        f.write('')

                            elif "!winner" in message and (username in authorisedusers or ismod):
                                winner = message.split(" ")[1]
                                try:
                                    if timeractive:
                                        timeractive = False
                                        for t in list(timers.values()):
                                            t.cancel()
                                        time.sleep(1)
                                        timers = {}
                                        with open("Titleholder.txt", "w") as f:
                                            f.write(winner)
                                        send_message("The winner this round is %s!" % winner)
                                        bets = {}
                                    else:
                                        send_message("There is no timer active!")
                                except Exception as errormsg:
                                    send_message("There was an error setting %s as winner." % winner)
                                    print("Error: " + str(errormsg))
                                    errorlog(errormsg, message)
                                else:
                                    with open('PrevBets.txt', 'a')as f:
                                        f.write("\n" + "Bets ended on: " + str(time.strftime("%x")) + " " +
                                                str(time.strftime("%X")) + "\n")
                                        for key in bets:
                                            f.write(key + ":" + str(bets[key]) + "\n")
                                    bets = {}
                                    with open("Bets.txt", 'w') as f:
                                        f.write('')

                            elif message == "!openbets" and (username in authorisedusers or ismod):
                                if not betsopen:
                                    betsopen = True
                                    send_message("Taking bets for the Broken Boner game! "
                                                 "Use !bet <number> to join in!")
                                else:
                                    send_message("Bets already opened!")

                            elif message == "!closebets" and (username in authorisedusers or ismod):
                                betsopen = False
                                send_message("Bets are now closed!")

                            elif "!setboner" in message and (username in authorisedusers or ismod):
                                keyword = "!setboner "
                                titleholder = message[message.index(keyword) + len(keyword):]
                                with open("Titleholder.txt", "w") as f:
                                    f.write(titleholder)
                                send_message("Registered " + titleholder + " as the new owner of \"Broken Boner\" ")

                            elif message == "!currentboner" or message == "!boner":
                                try:
                                    f = open("Titleholder.txt", "r")
                                    titleholder = f.read()
                                    send_message("The current owner of the title \"Broken Boner\" is: " +
                                                 titleholder + "!")
                                except Exception as errormsg:
                                    print("Error: " + str(errormsg))
                                    errorlog(errormsg, message)
                                    send_message("Error reading current boner")

                            elif message == "!brokenboner":
                                send_message("The game is to bet how long it takes for Fid to break a leg or "
                                             "die in ARMA. "
                                             "The timer starts after the TP pole or as the convoy moves out. "
                                             "Anyone can join to try and win the title \"Broken Boner\"! "
                                             "Use !bet <number of minutes> to place your bets!")

                            elif message == "!betstats" or message == "!bets":
                                if 'betstats' not in comlimits:
                                    if bets != {}:
                                        print(bets)
                                        try:
                                            threading.Timer(10, command_limiter, ['betstats']).start()
                                            comlimits.append('betstats')
                                        except Exception as e:
                                            print(e)
                                        try:
                                            betvalues = [int(i) for i in list(bets.values())]
                                            lowest = min(betvalues)
                                            highest = max(betvalues)
                                            betsum = 0.0
                                            for key in bets:
                                                betsum += int(bets[key])
                                            length = len(bets)
                                            avg = round((betsum / len(bets)), 2)
                                            send_message(str(length) + " people are betting this round. The lowest bet is "
                                                         + str(lowest) + " minutes and the highest bet is "
                                                         + str(highest) + " minutes. The average is " + str(avg) +
                                                         " minutes.")
                                        except Exception as errormsg:
                                            print("Error: " + str(errormsg))
                                            errorlog(errormsg, message)
                                            send_message("Error calculating numbers")
                                    else:
                                        send_message("No bets registered!")

                            elif "!bet" in message and len(message) <= 8:
                                if betsopen:
                                    bet = ''
                                    keyword = "!bet "
                                    try:
                                        bet = message[message.index(keyword) + len(keyword):]
                                        if isinstance(int(bet), numbers.Number):
                                            if int(bet) <= 0:
                                                send_message("Please don't try to invoke the apocalypse. Thanks.")
                                                break
                                            if displayname in bets.keys():
                                                bets[displayname] = bet
                                                betsec = int(bet) * 60
                                                t = threading.Timer(betsec, announcer, [displayname, bet])
                                                timers[displayname] = t
                                                print(bets)
                                                send_message("@" + displayname + " Bet updated! Your new bet is: "
                                                             + bet + " minutes!")
                                            else:
                                                bets[displayname] = bet
                                                betsec = int(bet) * 60
                                                t = threading.Timer(betsec, announcer, [displayname, bet])
                                                timers[displayname] = t
                                                print(bets)
                                                send_message(
                                                    "@" + displayname + " Bet registered: " + bet + " minutes!")
                                        else:
                                            send_message("Bet is not a number")
                                    except ValueError as e:
                                        if str(e) == 'substring not found':
                                            send_message("Use !bet <number> to enter the competition!")
                                        else:
                                            send_message("%s is not a valid bet. Please use whole numbers only." % bet)
                                        print(e)
                                    except Exception as errormsg:
                                        print("Error: " + str(errormsg))
                                        errorlog(errormsg, message)
                                        send_message("There was an error registering your bet. Please try again.")
                                else:
                                    send_message("Bets are not currently opened.")

                            elif "!addbet" in message and (username in authorisedusers or ismod):
                                try:
                                    addbet = message.split(' ')
                                    bets[addbet[1]] = addbet[2]
                                    # with open('Bets.txt', 'a') as f:
                                    #     f.write(addbet[1] + ":" + addbet[2] + "\n")
                                    t = threading.Timer((int(addbet[2]) * 60), announcer, [addbet[1], addbet[2]])
                                    timers[addbet[1]] = t
                                    print(bets)
                                    send_message("Bet for " + addbet[1] + " with " + addbet[2] +
                                                 " minutes added to pool!")
                                except Exception as errormsg:
                                    send_message("Error adding bet for this user.")
                                    print("Error: " + str(errormsg))
                                    errorlog(errormsg, message)

                            elif "!removebet" in message or "!rembet" in message and \
                                    (username in authorisedusers or ismod):
                                try:
                                    rembet = message.split(" ")[1]
                                    try:
                                        if all(i.isdigit() for i in rembet):
                                            print("all digits")
                                            if int(rembet) in list(bets.values()):
                                                if list(bets.values()).count(int(rembet)) > 1:
                                                    userbets = []
                                                    index = 0
                                                    for i in list(bets.values()):
                                                        if int(rembet) == i:
                                                            userbets.append(list(bets.keys())[index])
                                                        index += 1
                                                    send_message("Found more than one bet of " + rembet +
                                                                 " by these users: " + str(userbets))

                                                else:
                                                    print("number in bets")
                                                    rembet = list(bets.keys())[list(bets.values()).index(int(rembet))]
                                                    print(rembet)
                                                    del bets[rembet]
                                                    del timers[rembet]
                                                    send_message("Bet for " + rembet + " removed from pool.")
                                            else:
                                                raise Exception
                                        else:
                                            print("not all digits")
                                            if rembet in list(bets.keys()):
                                                print("name in keys")
                                                del bets[rembet]
                                                del timers[rembet]
                                                send_message("Bet for " + rembet + " removed from pool")
                                            else:
                                                raise Exception
                                    except Exception as errormsg:
                                        send_message("There are no bets with this name or value.")
                                        print("Error: " + str(errormsg))
                                        errorlog(errormsg, message)
                                    else:
                                        with open('Bets.txt', 'w') as f:
                                            for key in bets:
                                                f.write(key + ":" + str(bets[key]) + "\n")

                                except Exception as errormsg:
                                    send_message("Error removing user from current pool.")
                                    print("Error: " + str(errormsg))
                                    errorlog(errormsg, message)

                            elif message == "!clearbets" and (username in authorisedusers or ismod):
                                bets = {}
                                timers = {}
                                send_message("Bets cleared!")

                            elif message == "!bonermods":
                                try:
                                    modusers = ", ".join(authorisedusers)
                                    send_message("The current authorised users are: " + modusers + " and all mods.")
                                except Exception as errormsg:
                                    send_message("Error listing mods.")
                                    print("Error: " + str(errormsg))
                                    errorlog(errormsg, message)

                            elif message == "!mybet":
                                try:
                                    if bets.get(displayname):
                                        send_message(displayname + " your bet is: " +
                                                     str(bets.get(displayname)) + " minutes!")
                                    else:
                                        send_message("No bet registered!")
                                except Exception as errormsg:
                                    send_message("There was an error showing your bet!")
                                    print("Error: " + str(errormsg))
                                    errorlog(errormsg, message)

                            elif "!adduser" in message and (username in authorisedusers or ismod):
                                try:
                                    keyword = "!adduser "
                                    newuser = message[message.index(keyword) + len(keyword):]
                                    if newuser not in authorisedusers:
                                        authorisedusers.append(newuser.lower())
                                        with open('AuthUsers.txt', 'w') as out_file:
                                            out_file.write('\n'.join(authorisedusers))
                                        send_message(newuser + " has been added to the authorised users!")
                                    else:
                                        send_message(newuser + " already in list!")
                                except Exception as errormsg:
                                    send_message("Error adding user to the authorised users!")
                                    print("Error: " + str(errormsg))
                                    errorlog(errormsg, message)

                            elif "!removeuser" in message or "!remuser" in message and \
                                    (username in authorisedusers or ismod):
                                try:
                                    if "!removeuser" in message:
                                        keyword = "!removeuser "
                                    else:
                                        keyword = "!remuser "
                                    olduser = (message[message.index(keyword) + len(keyword):])
                                    olduserlow = olduser.lower()
                                    if olduser.length() == 0:
                                        send_message("Use !remuser <name> to remove that person from the authorised users.")
                                    if olduserlow in authorisedusers:
                                        authorisedusers.remove(olduserlow)
                                        with open('AuthUsers.txt', 'w') as out_file:
                                            out_file.write('\n'.join(authorisedusers))
                                        send_message(olduser + " has been removed from the authorised users!")
                                    else:
                                        send_message(olduser + " not in list!")
                                except Exception as errormsg:
                                    send_message("Error removing user from the authorised users!")
                                    print("Error: " + str(errormsg))
                                    errorlog(errormsg, message)

                            elif message == "!screwnightbot":
                                send_message("Screw Nightbot! I am the better bot! VoHiYo")

                            elif "!boneridea" in message:
                                try:
                                    keyword = "!boneridea "
                                    idea = message[message.index(keyword) + len(keyword):]
                                    with open('Ideas.txt', 'a') as f:
                                        f.write(displayname + " : " + idea + "\n")
                                    send_message("Thank you for suggestion! <3")
                                except Exception as errormsg:
                                    send_message("There was an error registering your idea. Please try again!")
                                    print("Error: " + str(errormsg))
                                    errorlog(errormsg, message)

                            elif message == '!permitted':
                                if permitted:
                                    permittedstr = ", ".join(permitted)
                                    send_message("Permitted users are: %s" % permittedstr)
                                else:
                                    send_message("No permitted users at this time.")

                            elif "!permit" in message and (issub or ismod or (username in permitted) or username == 'bastixx669'):
                                try:
                                    keyword = "!permit "
                                    permituser = message[message.index(keyword) + len(keyword):]
                                    permitted.append(permituser.lower())
                                    threading.Timer(60.0, permit, [permituser]).start()
                                    send_message("Permitted " + permituser + " to post links for 1 minute.")
                                except Exception as errormsg:
                                    send_message("There was an error permitting this user!")
                                    print("Error: " + str(errormsg))
                                    errorlog(errormsg, message)

                            elif "!addending" in message and (username in permitted or issub or ismod):
                                try:
                                    keyword = "!addending "
                                    newending = message[message.index(keyword) + len(keyword):]
                                    with open("Endings.txt", "a") as f:
                                        f.write(newending + "\n")
                                    send_message("Ending added to the list!")
                                except Exception as errormsg:
                                    send_message("There was an error registering your text. Please try again!")
                                    print("Error: " + str(errormsg))
                                    errorlog(errormsg, message)

                            elif "!addquote" in message and (ismod or username == 'bastixx669'):
                                try:
                                    keyword = "!addquote "
                                    newquote = message[message.index(keyword) + len(keyword):]
                                    quotes[str(len(quotes)+1)] = newquote
                                    with open("Quotes.txt", 'a') as f:
                                        f.write("%s:%s\n" % (len(quotes), newquote))
                                    send_message("Quote added!")
                                except Exception as errormsg:
                                    send_message("There was an error adding this quote. Please try again!")
                                    print("Error: " + str(errormsg))
                                    errorlog(errormsg, message)

                            elif message == "!quote":
                                randomindex = random.randint(1, len(quotes))
                                randomquote = quotes[str(randomindex)]
                                send_message("Quote %s: %s" % (randomindex, randomquote))

                            elif "!quote" in message:
                                try:
                                    quoteindex = message.split(" ")[1]
                                    quote = quotes[quoteindex]
                                    send_message("Quote %s: %s" % (quoteindex, quote))
                                except:
                                    send_message("This quote does not exist!")



                            # Testing commands:
                            elif username == 'bastixx669':
                                if message == '!createthread':
                                    t = threading.Timer(5, announcer, ['test', 'test'])
                                    print(t)
                                    t.start()
                                    print("thread started: " + str(t))

                                elif message == '!activethreads':
                                    print(threading.enumerate())

                                elif message == '!timers':
                                    print(timers)

                                elif message == '!cleartimers':
                                    bets = {}
                                    timers.clear()

                                elif message == '!permsyson':
                                    permitsystem = 'True'
                                    with open('Permitsystem.txt', 'w')as f:
                                        f.write(str(permitsystem))
                                    send_message("Permit system enabled")

                                elif message == '!permsysoff':
                                    permitsystem = 'False'
                                    with open('Permitsystem.txt', 'w')as f:
                                        f.write(str(permitsystem))
                                    send_message("Permit system disabled")

                                elif message == '!savebets':
                                    with open("Bets.txt", 'w') as f:
                                        for key in bets:
                                            f.write(key + ":" + str(bets[key]) + "\n")
                                    send_message("Pool saved!")


                    for l in parts:
                        if "End of /NAMES list" in l:
                            modt = True


main()
