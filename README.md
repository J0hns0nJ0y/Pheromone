[![](https://raw.githubusercontent.com/J0hns0nJ0y/Pheromone/master/pheromone.gif)]()

Pheromone is a tiny, temporary, command-line chat which can be used anytime and anywhere.

You create a one-time **room code**, give it to one person together with the `client.py` file and a time to show up. At that time you both run the client, enter the code, and chat inside your terminals. When either of you closes the terminal, the conversation is gone. Nothing is written to disk or to a database.

## ⚙️ How it works

```
 you (client.py) ──┐
                   ├──>  relay server (server.py, hosted on web service provider)  <── checks codes against a hosted codes.json (GitHub Gist)
 them (client.py) ─┘
```

| File | What it is |
|---|---|
| `gen_code.py` | Generates a room code and the hash to put in the Gist |
| `server.py` | The relay server (you deploy this) |
| `client.py` | The chat client (you give this to your recipient) |
| `requirements.txt` | Python dependencies for the server (`websockets`) |

When you remove a hash from the Gist, that code stops working for new joins.

---

## Step 1: Get the files

Clone or download this repo.

```
git clone <this-repo-url>
cd pheromone
pip install -U websockets
```

## Step 2: Create a room code (`gen_code.py`)

Run:

```
python gen_code.py
```

It prints two lines:

- **Give recipient** is the room code. Send this to the person you want to chat with. Keep it private.
- **Put in file** is the hash. This is what goes into the Gist (Step 3).

Make a new code for every chat and never reuse one.

## Step 3: Create the Gist that holds valid codes

1. Set the filename to `codes.json`.
2. Paste in a list of hashes, for example:
   ```json
   ["paste-your-first-hash-here"]
   ```
3. Click **Create secret gist**. "Secret" means it is not listed publicly. Anyone who has the link can open it, which is fine because it only contains hashes.
4. Click the **Raw** button on the Gist page and copy the URL from the address bar. It looks like:
   ```
   https://gist.githubusercontent.com/<you>/<gist-id>/raw/<long-commit-hash>/codes.json
   ```
5. Delete the `<long-commit-hash>/` part so it becomes:

   ```
   https://gist.githubusercontent.com/<you>/<gist-id>/raw/codes.json
   ```
   This version always shows your latest edit. This is your **CODES_URL**.

## Step 4: Deploy the server

1. Create a new GitHub repo (private is fine) and upload `server.py` and `requirements.txt` (which contains the single line `websockets`).
2. Pick your repo on the web service provider.
4. Use these settings:
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python server.py`
   - **Instance type:** Free
5. Under **Environment Variables**, add:
   - **Key:** `CODES_URL`
   - **Value:** your raw Gist URL from Step 3
6. Click **Create Web Service** and wait until it says **Live**.
7. Copy the address at the top, for example `https://my-pheromone.webservicer.com`.

## Step 5: Update `client.py`

Open `client.py` and find this line near the top:

```python
SERVER = "wss://yourhost.webservice.com"
```

Replace it with your own hosted address. Use `wss://` (not `https://`).

Then send this edited `client.py` to your recipient. They need Python 3.10+ and must run `pip install -U websockets` once.

## 🥷🏻 Chatting anonymously

Pheromone is designed to leave no trace on your devices, but be realistic about what "anonymous" means here.

What helps:

- **Nothing is stored.** Messages live only in the server's memory while being forwarded and in each terminal window. Closing the terminal clears them from view.
- **Use throwaway names.** The client asks for a display name. Use a nickname, not your real name.
- **No accounts.** There is no signup, email, or phone number. Only a one-time code.
- **One code per person, used once.** Remove the hash from the Gist after every chat.
- **Tell your recipient to close the terminal after chatting.** Terminal scrollback can keep text until the window is closed.

What does NOT make you anonymous:

- **The server operator can see traffic.** Whoever runs the relay (you) can technically see messages passing through and the IP addresses of both clients. If you want the content hidden even from the server, you would have to add end-to-end encryption, which Pheromone does not do.
- **IP addresses are visible** to the host. For stronger network anonymity, both people can use a VPN or Tor, which is outside the scope of this project.
- **Screenshots, copy/paste, and terminal scrollback** cannot be controlled by this tool. "Gone" means "not stored by Pheromone", not "unrecoverable".
- **Anyone who learns the room code while it is active** can try to join. Rooms are limited to 2 people, and the server shows a "joined" message for each connection, so watch for unexpected joins and share the code only over a channel you trust. Codes should be long and random (the generator makes 12 characters from letters and digits using Python's `secrets` module).

## 🐜 Security notes

- The server checks codes itself, so a modified `client.py` cannot skip verification.
- Repeated wrong codes from one IP are rate limited.
- Never put secrets in this public repo or in `client.py`. The client only needs the server address.
- Never reuse a room code.

## ⚠️ Troubleshooting

| Problem | Likely cause |
|---|---|
| `ERR invalid code` | The hash is not in the Gist yet, the Gist was not saved, or the raw file is cached. Wait a minute or two and retry. |
| `ERR server could not check codes` | `CODES_URL` is wrong. Make sure it starts with `gist.githubusercontent.com` and ends with `/raw/codes.json`. |
| `ERR room full` | Two people are already in that room. |
| `ERR too many attempts` | Too many wrong codes from your IP. Wait about 5 minutes. |
| Connection hangs at first | The server was asleep. Wait up to a minute. |
| Connection refused / cannot connect | The server is suspended, or `SERVER` in `client.py` is wrong (check `wss://`, the dot in URL, no trailing slash). |

---
_🫱🏼‍🫲🏼 Raise a Issue or a Pull Request._

[![](https://raw.githubusercontent.com/J0hns0nJ0y/Pheromone/master/contribute.gif)]()

_# Reach Me Out on Telegram @maisogov, If you want me to setup your custom anonymous relay and plan execution._
```shell              
      _,-'\   /|   .    .    /`.
  _,-'     \_/_|_  |\   |`. /   `._,--===--.__
 ^       _/"/  " \ : \__|_ /.   ,'    :.  :. .`-._
        // ^   /7 t'""    "`-._/ ,'\   :   :  :  .`.                                           P H E R O M O N E : Type & Disappear
        Y      L/ )\         ]],'   \  :   :  :   : `.                                                ( Inspired by Ants )
        |        /  `.n_n_n,','\_    \ ;   ;  ;   ;  _>                                        @J0hns0nJ0y
        |__    ,'     |  \`-'    `-.__\_______.==---'
       //  `""\\      |   \            \
       \|     |/      /    \            \
                     /     |             `.
                    ^      |               ^
                           ^
```
<p align="center"><sub><i>Built With 💗 For Anonymity Using Python</i></sub></p>
