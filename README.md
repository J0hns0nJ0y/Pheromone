# Pheromone

Pheromone is a tiny, temporary, command-line chat written in Python.

You create a one-time **room code**, give it to one person together with the `client.py` file and a time to show up. At that time you both run the client, enter the code, and chat inside your terminals. When either of you closes the terminal, the conversation is gone. Nothing is written to disk or to a database.

## How it works

```
 you (client.py) ──┐
                   ├──>  relay server (server.py, hosted on Render)  <── checks codes against a hosted codes.json (GitHub Gist)
 them (client.py) ─┘
```

- **gen_code.py** creates a random room code and its SHA-256 hash.
- **codes.json** (hosted as a GitHub Gist) is a list of the hashes of currently valid codes. Only hashes are stored there, never the codes themselves.
- **server.py** is a relay. It checks the code you type against the Gist, puts you in a room, allows at most 2 people per room, and forwards messages. It keeps messages in memory only while they pass through.
- **client.py** is the program your recipient runs.

When you remove a hash from the Gist, that code stops working for new joins.

## Requirements

- Python 3.10 or newer
- `pip install -U websockets` (version 13 or newer)
- A free GitHub account
- A free Render account (or any host that runs a normal always-on Python program; Vercel does not work because it cannot hold WebSocket connections open)

## Files in this repo

| File | What it is |
|---|---|
| `gen_code.py` | Generates a room code and the hash to put in the Gist |
| `server.py` | The relay server (you deploy this) |
| `client.py` | The chat client (you give this to your recipient) |
| `requirements.txt` | Python dependencies for the server (`websockets`) |

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

```
Give recipient : <12-character random code>
Put in file    : <64-character hash>
```

- **Give recipient** is the room code. Send this to the person you want to chat with. Keep it private.
- **Put in file** is the hash. This is what goes into the Gist (Step 3).

Make a new code for every chat and never reuse one.

## Step 3: Create the Gist that holds valid codes

1. Go to <https://gist.github.com> and sign in.
2. Set the filename to `codes.json`.
3. Paste in a list of hashes, for example:
   ```json
   ["paste-your-first-hash-here"]
   ```
   For several codes, separate hashes with commas. No comma after the last one.
4. Click **Create secret gist**. "Secret" means it is not listed publicly. Anyone who has the link can open it, which is fine because it only contains hashes.
5. Click the **Raw** button on the Gist page and copy the URL from the address bar. It looks like:
   ```
   https://gist.githubusercontent.com/<you>/<gist-id>/raw/<long-commit-hash>/codes.json
   ```
6. Delete the `<long-commit-hash>/` part so it becomes:
   ```
   https://gist.githubusercontent.com/<you>/<gist-id>/raw/codes.json
   ```
   This version always shows your latest edit. This is your **CODES_URL**.

Check it: open the CODES_URL in a browser. You should see only your list of hashes as plain text.

**Adding or removing a code later:** open the Gist, click **Edit**, change the list, click **Update gist**. GitHub may cache the raw file for a minute or two, and the server re-reads it about every 20 seconds, so add codes a few minutes before the chat.

## Step 4: Test locally first (optional but recommended)

Make a local `codes.json` containing your hash, then start the server pointing to that file.

**Windows (cmd):**
```
set CODES_URL=file:///C:/full/path/to/codes.json
python server.py
```

**Mac / Linux:**
```
CODES_URL=file:///full/path/to/codes.json python server.py
```

In `client.py`, temporarily set:
```python
SERVER = "ws://localhost:8765"
```

Open two more terminals and run `python client.py` in each. Enter the code and a name in both and chat. Try a wrong code (it should be refused) and a third client (it should say the room is full).

## Step 5: Deploy the server on Render

Use **your own separate repo** for hosting, containing only `server.py` and `requirements.txt`. Do not put `codes.json` or `gen_code.py` in it.

1. Create a new GitHub repo (private is fine) and upload `server.py` and `requirements.txt` (which contains the single line `websockets`).
2. Sign up at <https://render.com> with your GitHub account.
3. Click **New**, then **Web Service**, and pick your repo.
4. Use these settings:
   - **Runtime:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python server.py`
   - **Instance type:** Free
5. Under **Environment Variables**, add:
   - **Key:** `CODES_URL`
   - **Value:** your raw Gist URL from Step 3
6. Click **Create Web Service** and wait until it says **Live**.
7. Copy the address at the top, for example `https://my-pheromone.onrender.com`.

Notes:

- The free tier may put the service to sleep when idle. The first connection after a sleep can take 30 to 60 seconds. Open your server address in a browser a few minutes before a chat to wake it.
- To turn the server off between chats, use **Settings > Suspend Web Service** on Render and **Resume** it before the next chat.
- Every push to the hosting repo triggers a redeploy and restarts the server. Do not push while a chat is going on, or both people get disconnected.
- Free-tier rules change, so check Render's current terms.

## Step 6: Update `client.py`

Open `client.py` and find this line near the top:

```python
SERVER = "wss://yourhost.onrender.com"
```

Replace it with your own Render address:

- Use `wss://` (not `https://`).
- Use a dot between `onrender` and `com`.
- No trailing slash.

Example:

```python
SERVER = "wss://my-pheromone.onrender.com"
```

Then send this edited `client.py` to your recipient. They need Python 3.10+ and must run `pip install -U websockets` once.

## Step 7: Running a chat (your routine)

1. Run `python gen_code.py`. Copy the code and the hash.
2. Add the hash to your Gist and click **Update gist**.
3. Send your recipient the code and the time to join (the `client.py` file only needs to be sent once).
4. A few minutes before the time, wake or resume the server.
5. At the agreed time, both of you run:
   ```
   python client.py
   ```
   Enter the room code (it is hidden as you type) and a name.
6. Chat. Type `/quit` to leave.
7. Afterwards, delete that hash from the Gist so the code is dead.

## Chatting anonymously

Pheromone is designed to leave no trace on your devices, but be realistic about what "anonymous" means here.

What helps:

- **Nothing is stored.** Messages live only in the server's memory while being forwarded and in each terminal window. Closing the terminal clears them from view.
- **Use throwaway names.** The client asks for a display name. Use a nickname, not your real name.
- **No accounts.** There is no signup, email, or phone number. Only a one-time code.
- **One code per person, used once.** Remove the hash from the Gist after every chat.
- **Tell your recipient to close the terminal after chatting.** Terminal scrollback can keep text until the window is closed.

What does NOT make you anonymous:

- **The server operator can see traffic.** Whoever runs the relay (you) can technically see messages passing through and the IP addresses of both clients. Render also keeps its own infrastructure logs. If you want the content hidden even from the server, you would have to add end-to-end encryption, which Pheromone does not do.
- **IP addresses are visible** to the host. For stronger network anonymity, both people can use a VPN or Tor, which is outside the scope of this project.
- **Screenshots, copy/paste, and terminal scrollback** cannot be controlled by this tool. "Gone" means "not stored by Pheromone", not "unrecoverable".
- **Anyone who learns the room code while it is active** can try to join. Rooms are limited to 2 people, and the server shows a "joined" message for each connection, so watch for unexpected joins and share the code only over a channel you trust. Codes should be long and random (the generator makes 12 characters from letters and digits using Python's `secrets` module).

## Security notes

- The server checks codes itself, so a modified `client.py` cannot skip verification.
- Repeated wrong codes from one IP are rate limited.
- Never put secrets in this public repo or in `client.py`. The client only needs the server address.
- Never reuse a room code.

## Troubleshooting

| Problem | Likely cause |
|---|---|
| `ERR invalid code` | The hash is not in the Gist yet, the Gist was not saved, or the raw file is cached. Wait a minute or two and retry. |
| `ERR server could not check codes` | `CODES_URL` is wrong. Make sure it starts with `gist.githubusercontent.com` and ends with `/raw/codes.json`. |
| `ERR room full` | Two people are already in that room. |
| `ERR too many attempts` | Too many wrong codes from your IP. Wait about 5 minutes. |
| Connection hangs at first | The free Render server was asleep. Wait up to a minute. |
| Connection refused / cannot connect | The server is suspended, or `SERVER` in `client.py` is wrong (check `wss://`, the dot in `.onrender.com`, no trailing slash). |

## License

Add the license of your choice here.
