#!/usr/bin/env python3
from simple_term_menu import TerminalMenu
import os
import time
import yaml
import TTP


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def EnterMainMenu():
    # Some basic tasks that need to happen everytime the main menu is opened.
    clear()
    TTP.SendDEFCONLevel()
    TTP.GetCurrentMessage()
    TTP.ParseDEFCONStatus()
    TTP.PrintDEFCONLevel()
    TTP.PrintGlobalScores()
    TTP.PrintOurScores()


def EnterManualMenuTasks():
    # Some basic tasks that need to happen everytime the manual menu is opened.
    clear()
    TTP.GetCurrentMessage()
    TTP.ParseGameID()
    TTP.ParseGameState()
    TTP.ParsePlayboard()
    TTP.PrintOurScores()
    print("Playing field:")
    TTP.PrintPlayboard()


def EnterBotPwnerMenuTasks():
    # Some basic tasks that need to happen everytime the BotPwner menu is opened.
    EnterManualMenuTasks()


def PrintDeathToAllHumans():
    print("💀 Death to all Humans 💀\nPress 'CTRL + C' to stop.\n")

def PrintHerosNeverDie():
    print("🙏 Hero's Never Die 🙏\nPress 'CTRL + C' to stop.\n")

def StartManualGame(manual_play_menu, game_ended):
    # Function that handles the manual game.
    TTP.SendStartGame()
    while not game_ended:
        EnterManualMenuTasks()
        if TTP.GameStatus in ["won", "lost", "tied", "timeout"]:
            game_ended = True
            TTP.UpdateScores()
            print("We " + TTP.GameStatus + " !")
            time.sleep(2)
        if not game_ended:
            edit_sel = manual_play_menu.show()
            if TTP.GameStatus not in ["won", "lost", "tied", "timeout"]:
                TTP.SendNumberEmoji(str(edit_sel+1))


def StartBotPwnerGame(exit_function):
    # Function that handles the BotPwner game.
    TTP.SendStartGame()
    TTP.InitBotPwner(TTP.winning_plays[0])
    while not exit_function:
        EnterBotPwnerMenuTasks()
        if TTP.GameStatus in ["won", "lost", "tied", "timeout"]:
            exit_function = True
            TTP.UpdateScores()
            TTP.PrintBotPwnerGameStatus()
            time.sleep(2)
        if not exit_function:
            TTP.PrintBotPwnerRunning()
            if TTP.GameStatus not in ["won", "lost", "tied", "timeout"]:
                TTP.RunBotPwner()


def StartPrimeWOPRToKill(exit_function):
    # Function that loops indefinitely until canceld with CTRL+C.
    # Keeps starting new games and not actually playing them.
    # If a game is left 'open/running' for to long this will result in a timeout.
    # A timed out game will be counted as WOPR winning the match, thus raising the DEFCON Level.
    # Takes a while to get going. The highest total amount of wins for WOPR I was able to get during SenseCon2021 was around 1290.
    while not exit_function:
        i = 0
        clear()
        TTP.PrintDEFCONLevel()
        TTP.PrintGlobalScores()
        TTP.PrintOurScores()
        PrintDeathToAllHumans()
        while not exit_function:
            try:
                # Only updating the score each 5 runs speeds up the killing >:)
                if i == 5:
                    i = 0
                    clear()
                    TTP.SendDEFCONLevel()
                    TTP.GetCurrentMessage()
                    TTP.ParseDEFCONStatus()
                    TTP.PrintDEFCONLevel()
                    TTP.PrintGlobalScores()
                    TTP.PrintOurScores()
                    PrintDeathToAllHumans()
                TTP.SendStartGame()
                TTP.SessionLossess += 1
                i += 1
                time.sleep(1)
            except KeyboardInterrupt:
                exit_function = True


def StartPrimeWOPRToRevive(exit_function, game_ended):
    # Function that loops indefinitely until canceld with CTRL+C.
    # Uses BotPwner logic to win games, which lowers the DEFCON Level.
    while not exit_function:
        try:
            clear()
            TTP.PrintDEFCONLevel()
            TTP.PrintGlobalScores()
            PrintHerosNeverDie()
            while True:
                clear()

                TTP.SendDEFCONLevel()
                TTP.GetCurrentMessage()
                TTP.ParseDEFCONStatus()

                TTP.PrintDEFCONLevel()
                TTP.PrintGlobalScores()
                TTP.PrintOurScores()
                PrintHerosNeverDie()

                TTP.GetCurrentMessage()
                TTP.SendStartGame()
                TTP.InitBotPwner(TTP.winning_plays[0])
                while not game_ended:
                    clear()

                    TTP.GetCurrentMessage()

                    TTP.ParseGameID()
                    TTP.ParseGameState()
                    TTP.ParsePlayboard()

                    TTP.PrintDEFCONLevel()
                    TTP.PrintGlobalScores()
                    TTP.PrintOurScores()

                    PrintHerosNeverDie()
                    if TTP.GameStatus in ["won", "lost", "tied", "timeout"]:
                        game_ended = True
                        TTP.UpdateScores()
                        TTP.PrintBotPwnerGameStatus()
                        time.sleep(2)
                    if not game_ended:
                        TTP.PrintBotPwnerRunning()
                        if TTP.GameStatus not in ["won", "lost", "tied", "timeout"]:
                            TTP.RunBotPwner()
                    time.sleep(1)
                game_ended = False
        except KeyboardInterrupt:
            exit_function = True


def main():
    # Main function
    # Setup the simple_term_menu menu's and start the main menu.

    main_menu_title = ""
    main_menu_items = ["Play a manual game", "Let 🤖Pwner play a game",
                       "Prime WOPR to 💀", "Prime WOPR to 🙏", "Quit 👋"]
    main_menu_cursor = "> "
    main_menu_cursor_style = ("fg_purple", "bold")
    main_menu_style = ("bg_black", "bg_black")
    main_menu_exit = False

    main_menu = TerminalMenu(
        menu_entries=main_menu_items,
        title=main_menu_title,
        menu_cursor=main_menu_cursor,
        menu_cursor_style=main_menu_cursor_style,
        menu_highlight_style=main_menu_style,
        cycle_cursor=True
    )

    manual_play_menu_title = ""
    manual_play_menu_items = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
    manual_play_menu = TerminalMenu(
        manual_play_menu_items,
        title=manual_play_menu_title,
        menu_cursor=main_menu_cursor,
        menu_cursor_style=main_menu_cursor_style,
        menu_highlight_style=main_menu_style,
        cycle_cursor=True,
    )

    while not main_menu_exit:
        EnterMainMenu()
        main_sel = main_menu.show()
        if main_sel == 0:
            StartManualGame(manual_play_menu, False)
        if main_sel == 1:
            StartBotPwnerGame(False)
        if main_sel == 2:
            StartPrimeWOPRToKill(False)
        if main_sel == 3:
            StartPrimeWOPRToRevive(False, False)
        if main_sel == 4:
            print("Bye!")
            main_menu_exit = True


if __name__ == "__main__":
    # Load the config.yml file
    try:
        with open('config.yml') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
    except:
        print("[x] Could not find the 'config.yml' config file.\n    Copy the 'config.yml.example' file and setup the values.")
        exit(0)

    # Start a new instance of TicTacPwn
    TTP = TTP.TicTacPwn(config['discord_cookies'],
                        config['discord_headers'],
                        config['discord_chat_id'],
                        config['discord_mention_you'],
                        config['discord_mention_wopr']
                        )
    # Run main
    main()
