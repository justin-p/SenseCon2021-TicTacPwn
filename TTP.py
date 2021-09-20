import requests
import json
import time
import re


class TicTacPwn:
    def __init__(self, discord_cookies, discord_headers, discord_chat_id, discord_mention_you, discord_mention_wopr):
        # Setup inital default values
        self.Timeout = 1.5
        self.DEFCONLevel = 0
        self.GlobalWORPWins = 0
        self.GlobalHumanWins = 0
        self.SessionWins = 0
        self.SessionLossess = 0
        self.SessionTies = 0
        self.Turns = 0

        # List of winning play dicts ("turn": "number_to_play")
        self.winning_plays = [{"1": "9",
                               "2": "3",
                               "3": "7",
                               "4": "5"},
                              {"1": "9",
                               "2": "7",
                               "3": "1",
                               "4": "5"},
                              {"1": "9",
                               "2": "1",
                               "3": "7",
                               "4": "4"}
                              ]

        # Setup discord values
        self.discord_cookies = discord_cookies
        self.discord_headers = discord_headers
        self.discord_chat_id = discord_chat_id
        self.discord_mention_you = discord_mention_you
        self.discord_mention_wopr = discord_mention_wopr

    def SendCommand(self, command):
        # Send a command to WOPR.
        s = requests.session()
        url = "https://discord.com:443/api/v9/channels/" + \
            self.discord_chat_id + "/messages"
        data = {
            "content": command,
            "nonce": "",
            "tts": False
        }
        s.post(url, headers=self.discord_headers,
               cookies=self.discord_cookies, json=data)
        time.sleep(self.Timeout)

    def SendNumberEmoji(self, Number):
        # React with a Number Emoji on a message from WOPR.
        s = requests.session()
        url = ("https://discord.com:443/api/v9/channels/" + self.discord_chat_id +
               "/messages/" + self.GameID + "/reactions/" + Number + "%EF%B8%8F%E2%83%A3/%40me")
        s.put(url, headers=self.discord_headers, cookies=self.discord_cookies)
        time.sleep(self.Timeout)

    def SendStartGame(self):
        # Ask WOPR to start a new game.
        self.SendCommand("&gp tictactoe")

    def SendDEFCONLevel(self):
        # Ask WOPR for the current DEFCON level.
        self.SendCommand("&dl")

    def GetCurrentMessage(self):
        # Get the current message
        s = requests.session()
        url = "https://discord.com:443/api/v9/channels/" + \
            self.discord_chat_id + "/messages?limit=1"
        r = s.get(url, headers=self.discord_headers,
                  cookies=self.discord_cookies).text
        r = r.lstrip("[")
        r = r.rstrip("]")
        r_json = json.loads(r)
        self.CurrentGameMessage = r_json

    def ParseDEFCONStatus(self):
        # Parse the output of the DL command and gather the level, 'WOPR score' and 'Humans score'.
        self.DEFCONLevel = (self.CurrentGameMessage['content'].split("**"))[1]
        self.GlobalWORPWins = (self.CurrentGameMessage['content'].split(
            "WOPR vs Humans score "))[1].split(":")[0]
        self.GlobalHumanWins = (self.CurrentGameMessage['content'].split(
            "WOPR vs Humans score "))[1].split(":")[1]

    def ParseGameID(self):
        # Parse the output of a message to get the current 'GameID'.
        self.GameID = self.CurrentGameMessage['id']

    def ParseGameState(self):
        # Parse the output of the current message. Identify the state of the game.
        if re.search(r'make a move', self.CurrentGameMessage['content'], re.DOTALL) != None:
            self.GameStatus = 'clean'
        elif re.search(r'thinking', self.CurrentGameMessage['content'], re.DOTALL) != None:
            self.GameStatus = 'thinking'
        elif re.search(r'your move', self.CurrentGameMessage['content'], re.DOTALL) != None:
            self.GameStatus = 'our_turn'
        elif re.search(r'already taken spot', self.CurrentGameMessage['content'], re.DOTALL) != None:
            self.GameStatus = 'spot_taken'
        elif re.search(r'<@' + self.discord_mention_you + '>', self.CurrentGameMessage['content'], re.DOTALL) != None:
            self.GameStatus = 'won'
        elif re.search(r'<@' + self.discord_mention_wopr + '>', self.CurrentGameMessage['content'], re.DOTALL) != None:
            self.GameStatus = 'lost'
        elif re.search(r'global thermonuclear war', self.CurrentGameMessage['content'], re.DOTALL) != None:
            self.GameStatus = 'tied'
        elif re.search(r'times up buddy', self.CurrentGameMessage['content'], re.DOTALL) != None:
            self.GameStatus = 'timeout'
        else:
            self.GameStatus = 'unknown'

    def ParsePlayboard(self):
        # Parse the output of the current message to gather information about the current Playboard.
        # Regex match on DOT to Newline.
        # ._ _ _
        # |_|_|_|
        # |_|_|_|
        # |_|_|_|\n
        #
        match = re.search(
            r'\..*\n`', self.CurrentGameMessage['content'], re.DOTALL)
        # Get the content of the regex match
        self.StringField = str(match.group())
        # Strip off the markdown code brackets
        self.StringField = self.StringField.rstrip("`")
        # Split the output on the grid walls.
        field_split = self.StringField.split('|')
        # Store the current status of each grid space to the correct number.
        self.fieldArray = {'1': field_split[1], '2': field_split[2], '3': field_split[3], '4': field_split[5],
                           '5': field_split[6], '6': field_split[7], '7': field_split[9], '8': field_split[10], '9': field_split[11]}
        # Spaces WOPR occupies
        self.WOPRSpaces = [k for k, v in self.fieldArray.items() if v == "x"]
        # Spaces we occupy
        self.OurSpaces = [k for k, v in self.fieldArray.items() if v == "o"]
        # Open spaces
        self.OpenSpaces = [k for k, v in self.fieldArray.items() if v == "_"]

    def UpdateScores(self):
        # Update our score counters.
        if self.GameStatus == "won":
            self.SessionWins += 1
        elif self.GameStatus == "tied":
            self.SessionTies += 1
        else:
            self.SessionLossess += 1

    def InitBotPwner(self, sequence):
        # Set values to default for a new game.
        self.Turns = 0
        self.Block = False
        self.OneSpotLeft = False
        self.BotPwnerSequence = sequence

    def RemoveNumsForTempList(self, tempopen, n):
        # Remove a number from a list. Silently capture if it wasnt in the list in the first place.
        try:
            tempopen.remove(n)
        except:
            pass

    def AnalyseNextBotPwnMove(self):
        # If there is only one open space left, use this spot in our next turn.
        if len(self.OpenSpaces) == 1:
            print("[!] 🤖Pwner detected that there is one spot left to play something.\n    🤖Pwner thinks this will mostlikey result in a tied match.\n")
            self.OneSpotLeft = True
            self.OneSpotLeftPlay = self.OpenSpaces[0]

        # TODO: add check that ensures if we win next turn to ignore all other checks and play as normal. Currently AutoPwner prefers blocking WOPR over winning.

        # TODO: add check to ensure that if there is no more way we can win that we finish the game in a draw.

        # If there is more then 1 open space check if WOPR wins next turn using the 'middle top to down'-sequence (2,5,8).
        if self.OneSpotLeft == False:
            if (all(item in self.WOPRSpaces for item in ["2", "5"])
                or all(item in self.WOPRSpaces for item in ["2", "8"])
                or all(item in self.WOPRSpaces for item in ["5", "2"])
                or all(item in self.WOPRSpaces for item in ["5", "8"])
                or all(item in self.WOPRSpaces for item in ["8", "2"])
                    or all(item in self.WOPRSpaces for item in ["8", "5"])):
                if any(item in self.OurSpaces for item in ["2", "5", "8"]):
                    # We already blocked this sequence. No action needed.
                    print(
                        "[-] 🤖Pwner has already blocked the 'middle top to down'-sequence.\n")
                    time.sleep(2)
                else:
                    # Setup a new list with all open spaces.
                    # Remove open spaces that don't match the current sequence WOPR is using to beat us.
                    # Use this number for our next turn by setting self.Block to True and storing the play in self.BlockPlay.
                    tempopen = self.OpenSpaces
                    for n in ["1", "3", "4", "6", "7", "9"]:
                        self.RemoveNumsForTempList(tempopen, n)
                    self.Block = True
                    self.BlockPlay = str(tempopen[0])
                    print("[!] 🤖Pwner detected that WOPR will win the next turn using the 'middle top to down'-sequence (2,5,8).\n    🤖Pwner will play " +
                          str(tempopen[0]) + " to block.\n")
                    time.sleep(2)

            # If the previous checks did not find a needed block and there is more then 1 open space, check if WOPR wins next turn using the 'middle left to right'-sequence (4,5,6).
            if self.Block == False and self.OneSpotLeft == False:
                if (all(item in self.WOPRSpaces for item in ["4", "5"])
                    or all(item in self.WOPRSpaces for item in ["4", "6"])
                    or all(item in self.WOPRSpaces for item in ["5", "6"])
                    or all(item in self.WOPRSpaces for item in ["5", "4"])
                    or all(item in self.WOPRSpaces for item in ["6", "4"])
                        or all(item in self.WOPRSpaces for item in ["6", "5"])):
                    if any(item in self.OurSpaces for item in ["4", "5", "6"]):
                        # We already blocked this sequence. No action needed.
                        print(
                            "[-] 🤖Pwner has already blocked the 'middle left to right'-sequence.\n")
                        time.sleep(2)
                    else:
                        tempopen = self.OpenSpaces
                        for n in ["1", "2", "3", "7", "8", "9"]:
                            self.RemoveNumsForTempList(tempopen, n)
                        self.Block = True
                        self.BlockPlay = str(tempopen[0])
                        print("[!] 🤖Pwner detected that WOPR will win the next turn using the 'middle left to right'-sequence (4,5,6).\n    🤖Pwner will play " + str(
                            tempopen[0]) + " to block.\n")
                        time.sleep(2)

            # If the previous checks did not find a needed block and there is more then 1 open space, check if WOPR will win next turn using the 'left top to bottom'-sequence (1,4,7).
            if self.Block == False and self.OneSpotLeft == False:
                if (all(item in self.WOPRSpaces for item in ["1", "4"])
                    or all(item in self.WOPRSpaces for item in ["1", "7"])
                    or all(item in self.WOPRSpaces for item in ["4", "1"])
                    or all(item in self.WOPRSpaces for item in ["4", "7"])
                    or all(item in self.WOPRSpaces for item in ["7", "1"])
                        or all(item in self.WOPRSpaces for item in ["7", "4"])):
                    if any(item in self.OurSpaces for item in ["1", "4", "7"]):
                        print(
                            "[-] 🤖Pwner has already blocked the 'left top to bottom'-sequence.\n")
                        time.sleep(2)
                    else:
                        tempopen = self.OpenSpaces
                        for n in ["2", "3", "5", "6", "8", "9"]:
                            self.RemoveNumsForTempList(tempopen, n)
                        self.Block = True
                        self.BlockPlay = str(tempopen[0])
                        print("[!] 🤖Pwner detected that WOPR will win the next turn using the 'left top to bottom'-sequence (1,4,7).\n    🤖Pwner will play " + str(
                            tempopen[0]) + " to block.\n")
                        time.sleep(2)

            # If the previous checks did not find a needed block and there is more then 1 open space check, if WOPR will win next turn using the 'top left to right'-sequence.
            if self.Block == False and self.OneSpotLeft == False:
                if (all(item in self.WOPRSpaces for item in ["1", "2"])
                    or all(item in self.WOPRSpaces for item in ["1", "3"])
                    or all(item in self.WOPRSpaces for item in ["2", "1"])
                    or all(item in self.WOPRSpaces for item in ["2", "3"])
                    or all(item in self.WOPRSpaces for item in ["3", "1"])
                        or all(item in self.WOPRSpaces for item in ["3", "2"])):
                    if any(item in self.OurSpaces for item in ["1", "2", "3"]):
                        print(
                            "[-] 🤖Pwner has already blocked the left top to bottom sequence.\n")
                        time.sleep(2)
                    else:
                        tempopen = self.OpenSpaces
                        for n in ["4", "5", "6", "7", "8", "9"]:
                            self.RemoveNumsForTempList(tempopen, n)
                        self.Block = True
                        self.BlockPlay = str(tempopen[0])
                        print("[!] 🤖Pwner detected that WOPR will win the next turn using the 'top left to right'-sequence (1,2,3).\n    🤖Pwner will play " + str(
                            tempopen[0]) + " to block.\n")
                        time.sleep(2)

        # If the previous checks did not find a needed block and there is more then 1 open space, check if WOPR has taken one of our spots, ifso find a new sequence not containing this number.
        if self.OneSpotLeft == False and self.Block == False:
            if any(item in self.WOPRSpaces for item in self.BotPwnerSequence.values()):
                taken_spot = list(set(self.WOPRSpaces) & set(
                    self.BotPwnerSequence.values()))[0]
                print("[!] WOPR has taken our spot on turn " + str(self.Turns) +
                      ".\n    🤖Pwner will switch to sequence that does not use " + str(taken_spot) + ".\n")
                time.sleep(2)
                for wp in self.winning_plays:
                    if wp[str(self.Turns+1)] != taken_spot:
                        self.BotPwnerSequence = wp
                        break

    # TODO: add check to see if WOPR cheated and has overwritten any of our plays, if so update a counter that keeps track of the cheating.

    def RunBotPwner(self):
        # Wait for 2 seconds if WOPR is still thinking and check the message again.
        while self.GameStatus == "thinking":
            self.GetCurrentMessage()
            self.ParseGameState()
            time.sleep(2)

        # Analyse our next move.
        self.AnalyseNextBotPwnMove()

        # If our Analyse tells us WOPR is about to win, block WOPR's play.
        if self.Block == True:
            self.SendNumberEmoji(self.BlockPlay)
            self.Block = False
        # If our Analyse tells us there is only one spot left, use this spot.
        elif self.OneSpotLeft == True:
            self.SendNumberEmoji(self.OneSpotLeftPlay)
            self.OneSpotLeft = False
        # The next number in our current sequence is the best move. Play this number.
        else:
            self.SendNumberEmoji(self.BotPwnerSequence[str(self.Turns+1)])
        self.Turns += 1

    def PrintBotPwnerRunning(self):
        print("🤖Pwner is running...\n")

    def PrintBotPwnerGameStatus(self):
        print("🤖Pwner " + self.GameStatus + " !\n")

    def PrintPlayboard(self):
        print(self.StringField)

    def PrintDEFCONLevel(self):
        print("DEFCON Level: " + self.DEFCONLevel)
        print("")

    def PrintGlobalScores(self):
        print("Global WOPR vs Humans scoreboard:")
        print(" WOPR:   " + self.GlobalWORPWins)
        print(" Humans: " + self.GlobalHumanWins)
        print("")

    def PrintOurScores(self):
        print("Scoreboard of current TicTacPwn session:")
        print(" WOPR: " + str(self.SessionLossess))
        print("   Us: " + str(self.SessionWins))
        print(" Ties: " + str(self.SessionTies))
        print("")
