# SenseCon2021-TicTacPwn

**WARNING** It is against discord's ToS to use your personal account as a bot. You may get banned when using this, you have been warned.

## Setup

1. Install the `requirements.txt`

```bash
pip3 install -r requirements.txt
```

2. Create copy of `config.yml.example`

```bash
cp config.yml.example config.yml
```

3. Intercept discord (webui + discord) and talk to WOPR.
4. Win and lose a game of TicTacToe.
5. Look at intercepted traffic and copy the following
   1. Copy _all_ cookies of a request and place these in `discord_cookies` as a dict.
   2. Copy _all_ headers of a request and place these is `discord_headers` as a dict.
   3. Copy the chat id (https://discord.com/channels/@me/ThisIsTheChatID) of WOPR and place this in `discord_chat_id` as a string.
   4. Find the message that contains the mention of you. Copy the mention ID (<@A123456789>) and place this in `discord_mention_you` as a string.
   5. Find the message that contains the mention of WOPR. Copy the mention ID (<@A123456789>) and place this in `discord_mention_wopr` as a string.
6. Run `TicTacPwn.py`
