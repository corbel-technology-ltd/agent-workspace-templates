# Start here

Welcome. This page assumes nothing. If you have never opened a terminal in your life, you are in
exactly the right place. Follow the steps in order and you will be done in about 15 minutes.

## What this is

Harbour is a filing cabinet that your AI assistant keeps tidy for you. Your notes, decisions, and
plans live in ordinary files on your own computer, and an AI assistant (such as Claude) reads
them, updates them, and asks you before doing anything important. No app to subscribe to, no
account to create, and everything stays yours.

## What you need

- A computer running Windows, Mac, or Linux.
- About 15 minutes.
- An AI coding assistant. We use **Claude Code** below. Two ways to get it:
  - **Easiest:** download the Claude desktop app from [claude.ai/download](https://claude.ai/download),
    install it, and sign in (create a free account if you do not have one).
  - **Terminal route:** install Node.js from [nodejs.org](https://nodejs.org) (big green button,
    accept the defaults), then run this in a terminal: `npm install -g @anthropic-ai/claude-code`

Do not worry if words like "terminal" mean nothing yet. Step 1 covers it.

## The steps

**1. Open a terminal.** This is the window where you type commands.

- **Windows:** press the Windows key, type `cmd`, press Enter.
- **Mac:** press Cmd + Space, type `terminal`, press Enter.
- **Linux:** press Ctrl + Alt + T, or find "Terminal" in your applications.

You should see a mostly empty window with some text and a blinking cursor. That is it. You type a
command, press Enter, and the computer replies.

**2. Check you have Python 3.** Type this and press Enter (on Windows, type `python` instead of
`python3` here and everywhere below):

```text
python3 --version
```

You should see something like `Python 3.12.4`. Any number starting with 3 is fine.

If you get "not found" or "not recognised" instead: on **Windows**, download Python from
[python.org/downloads](https://www.python.org/downloads/), run the installer, and **tick the box
that says "Add Python to PATH"** before clicking Install, then close and reopen your terminal.
On **Mac**, download it from the same page and run the installer. On **Linux**, run
`sudo apt install python3` (Ubuntu) or use your usual package manager.

**3. Check you have git.** Type:

```text
git --version
```

You should see something like `git version 2.45.0`.

If not: on **Windows**, download it from [git-scm.com](https://git-scm.com) and accept every
default in the installer. On **Mac**, a pop-up will offer to install "command line developer
tools"; click Install and wait. On **Linux**, run `sudo apt install git`.

**4. Download Harbour.** Two ways; pick one.

- **No git knowledge needed:** open
  [github.com/CORBEL-Technology/Harbour](https://github.com/CORBEL-Technology/Harbour) in your
  browser, click the green **Code** button, click **Download ZIP**, then unzip it into your home
  folder (double-click the ZIP on Mac, right-click and "Extract All" on Windows). You get a folder
  called `Harbour-main`.
- **With git:** in your terminal, type:

```text
git clone https://github.com/CORBEL-Technology/Harbour.git
```

You should see lines ending in `done.`, and a new `Harbour` folder appears.

**5. Go into the folder.** Type (use `Harbour-main` if you downloaded the ZIP):

```text
cd Harbour
```

Nothing dramatic happens; the text before your cursor now ends in the folder name. That means you
are "inside" it. If you get "No such file or directory", the folder is somewhere else; try
`cd Downloads` first and then this step again.

**6. Create your workspace.** Type:

```text
python3 instantiate.py commonplace my-workspace
```

You should see `instantiate: commonplace -> my-workspace` and a "Next:" line. That is success:
you now have your own workspace folder, completely separate from the template.

If you see an error instead, check the table below.

**7. Open the workspace in Claude Code.** Type:

```text
cd my-workspace
claude
```

Claude Code starts inside your new workspace. The first time, it may ask you to log in; follow
the prompts in the terminal (it opens your browser to sign in). If you installed the desktop app
instead, open the app and open the `my-workspace` folder from there.

**8. Say hello.** Type this as your first message to the agent:

> Read AGENTS.md and introduce yourself.

The agent reads its instructions, then walks you through a short onboarding: your name, a name
for the workspace, a name for the agent. Answer the questions and you are live. From then on,
just talk to it about your work.

## Something went wrong

| What you see | What to do |
| --- | --- |
| `python3: command not found` or `not recognised` | Python is missing or hidden. Redo step 2; on Windows remember the "Add Python to PATH" tick box, then reopen the terminal. |
| `git: command not found` or `not recognised` | Git is missing. Redo step 3, then reopen the terminal. |
| `Permission denied` | The Harbour folder is somewhere protected. Move it to your home folder or Downloads, then start again from step 5 (no `sudo` needed, ever). |
| `can't open file 'instantiate.py'` | You are in the wrong folder. Type `cd` then redo step 5, checking the folder name (`Harbour` or `Harbour-main`). |
| Step 5 works but the folder looks empty | The ZIP unpacked a folder inside a folder. Type `cd Harbour-main` a second time, then redo step 6. |
| The agent says it cannot see any files | It was opened in the wrong folder. Close it, make sure you are inside `my-workspace` (step 7), and start it again. |

Still stuck? Open an issue at
[github.com/CORBEL-Technology/Harbour/issues](https://github.com/CORBEL-Technology/Harbour/issues)
and paste in exactly what you typed and what the screen said. No question is too basic.

## What next

Your workspace is the **Commonplace** member of the Harbour family. When you are curious about
the other two (a shared brain across several workspaces, and a registry that keeps their tooling
in sync), read [FAMILY.md](FAMILY.md). No rush; the workspace stands alone.
