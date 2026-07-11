# Start here

Welcome. This page assumes nothing. If you have never opened a terminal in your life, you are in
exactly the right place. Follow the steps in order and you will be done in about 15 minutes.

## What this is

Agent-Workspace-Templates is a filing cabinet that your AI assistant keeps tidy for you. Your notes, decisions, and
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

**4. Download Agent-Workspace-Templates.** Two ways; pick one.

- **No git knowledge needed:** open
  [github.com/corbel-technology-ltd/agent-workspace-templates](https://github.com/corbel-technology-ltd/agent-workspace-templates) in your
  browser, click the green **Code** button, click **Download ZIP**, then unzip it into your home
  folder (double-click the ZIP on Mac, right-click and "Extract All" on Windows). You get a folder
  called `Agent-Workspace-Templates-main`.
- **With git:** in your terminal, type:

```text
git clone https://github.com/corbel-technology-ltd/agent-workspace-templates.git
```

You should see lines ending in `done.`, and a new `Agent-Workspace-Templates` folder appears.

**5. Go into the folder.** Type (use `Agent-Workspace-Templates-main` if you downloaded the ZIP):

```text
cd Agent-Workspace-Templates
```

Nothing dramatic happens; the text before your cursor now ends in the folder name. That means you
are "inside" it. If you get "No such file or directory", the folder is somewhere else; try
`cd Downloads` first and then this step again.

**6. Create your workspace.** Type:

```text
python3 instantiate.py folder-agent-workspace my-workspace
```

You should see `instantiate: folder-agent-workspace -> my-workspace` and a "Next:" line. That is success:
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

## How your workspace remembers (nothing for you to manage)

Your agent keeps a diary and a memory, and both run themselves:

- **The journal** (`20_memory/journal/`) records what happened, every session, append-only.
  Nothing can edit or delete an entry - a guard blocks it, so the history is trustworthy.
- **Sleep** happens when enough diary has piled up: the workspace tells the agent "a memory-sleep
  run is due" at the start of a session. Say "go ahead" and it distils the recurring facts into
  small memory cards - who does what, preferences you stated, procedures that worked - each one
  traceable back to the diary entries that support it. The agent cannot invent memories: a
  validator rejects any card that lacks evidence or names something the store has never seen.
- **The reaper** runs at the end of every session and keeps the memory healthy on its own:
  facts you keep touching climb into long-term memory, facts that go cold sink and eventually
  archive (never delete), duplicates merge, and anything unsourced is quarantined. Preferences
  and anything marked pivotal never decay.

So: talk to your agent, approve a sleep run when it asks, and the memory takes care of itself.
If you are curious, `python3 tools/memory-selftest.py` inside your workspace proves the whole
loop in about two seconds.

## Level up: a second workspace and the shared brain

One workspace is plenty to start. The moment you want a second (say, one for work and one for
personal), add the **shared context store** so both know who you are without repeating yourself:

**1. Create the store and a second workspace** (from the `Agent-Workspace-Templates` folder):

```text
python3 instantiate.py shared-context my-shared
python3 instantiate.py folder-agent-workspace my-workspace-two
```

**2. Onboard the store.** Open `my-shared` in your agent runtime (`cd my-shared` then `claude`)
and say "Read AGENTS.md and introduce yourself" - it fills in who you are once: your identity,
how agents should behave, the people, places, and tech that every workspace shares.

**3. Link each workspace in.** From inside `my-shared`:

```text
python3 core/link-workspace.py --name my-workspace --path /full/path/to/my-workspace --agent <its agent name>
```

That registers the workspace on the store's roster and prints a one-line boot rule; paste it
where the tool tells you. Repeat for `my-workspace-two`. (A Folder-Agent-Workspace workspace asks for the
shared store's path during onboarding - if you gave it then, this is already wired.)

From then on every workspace loads the shared brain at session start, corrections land once and
reach all of them, and the store's ledger (`CHANGES.md`) records every change with an objection
window - your agents co-own the brain without being able to quietly rewrite it. Fill
`people/`, `places/`, `concepts/`, `automations/`, and `tech-stack/` from their `_*-template.md`
files as real entries come up - your machines, your software, the people your agents deal with -
so every present and future workspace knows your world.

## Something went wrong

| What you see | What to do |
| --- | --- |
| `python3: command not found` or `not recognised` | Python is missing or hidden. Redo step 2; on Windows remember the "Add Python to PATH" tick box, then reopen the terminal. |
| `git: command not found` or `not recognised` | Git is missing. Redo step 3, then reopen the terminal. |
| `Permission denied` | The Agent-Workspace-Templates folder is somewhere protected. Move it to your home folder or Downloads, then start again from step 5 (no `sudo` needed, ever). |
| `can't open file 'instantiate.py'` | You are in the wrong folder. Type `cd` then redo step 5, checking the folder name (`Agent-Workspace-Templates` or `Agent-Workspace-Templates-main`). |
| Step 5 works but the folder looks empty | The ZIP unpacked a folder inside a folder. Type `cd Agent-Workspace-Templates-main` a second time, then redo step 6. |
| The agent says it cannot see any files | It was opened in the wrong folder. Close it, make sure you are inside `my-workspace` (step 7), and start it again. |

Still stuck? Open an issue at
[github.com/corbel-technology-ltd/agent-workspace-templates/issues](https://github.com/corbel-technology-ltd/agent-workspace-templates/issues)
and paste in exactly what you typed and what the screen said. No question is too basic.

## What next

Your workspace is the **Folder-Agent-Workspace** member of the Agent-Workspace-Templates family. When you are curious about
the other two (a shared brain across several workspaces, and a registry that keeps their tooling
in sync), read [FAMILY.md](FAMILY.md). No rush; the workspace stands alone.
