# Start here

Welcome. This page assumes you have never used a terminal. Follow it in order; the installer checks
each requirement, refuses to overwrite anything, and tells you the exact recovery command if it
stops.

## What this creates

Your workspace is a folder of ordinary Markdown files plus git history. An AI coding assistant
reads the folder, keeps the journal and registers current, and stops for your approval before a
consequential action. There is no workspace service or database to subscribe to.

You need a Mac, Linux computer, or Windows with WSL; an internet connection for installation; and
an AI coding assistant that can open a local folder and run terminal commands.

## Windows: set up WSL first

The automatic guards use Linux/Mac shell hooks. On Windows, use Microsoft's Windows Subsystem for
Linux (WSL):

1. Press the Windows key, type `powershell`, right-click **Windows PowerShell**, and choose
   **Run as administrator**.
2. Run `wsl --install`, then restart when asked.
3. Open **Ubuntu** from the Start menu. Choose any username and password.

Use that Ubuntu window for every command below, not Command Prompt or PowerShell. Native Windows
without WSL may create the files, but its guard hooks will not be reliable.

## Install one workspace

### 1. Open a terminal

- **Windows:** open the Ubuntu (WSL) window.
- **Mac:** press Cmd + Space, type `terminal`, then press Enter.
- **Linux:** press Ctrl + Alt + T, or open Terminal from the applications menu.

You will see text and a blinking cursor. Paste commands there and press Enter.

### 2. Run the installer

Paste this exact line:

```text
curl -fsSL https://raw.githubusercontent.com/CORBEL-Technology/agent-workspace-templates/main/install.sh | sh
```

It checks git, Python 3.8 or newer, Git identity, and PyYAML; downloads the templates without
leaving a partial clone; then creates `my-workspace` in your home folder with its first git commit.

If the terminal says `curl: command not found`, use this equivalent command:
`wget -qO- https://raw.githubusercontent.com/CORBEL-Technology/agent-workspace-templates/main/install.sh | sh`.
If neither downloader exists, Ubuntu/WSL users can run `sudo apt install curl`, then paste the
original command again.

### 3. Follow the two lines under `Done. Next step:`

The installer prints an exact `cd '...'` command. Paste it. On a PEP 668-protected Linux system it
also prints:

```text
. .venv/bin/activate
```

Paste that too, now and whenever you reopen this workspace. The `.venv` keeps the one Python
dependency isolated; it is inside the workspace and ignored by git.

### 4. Open the folder in your AI coding assistant

Start the assistant from this terminal after the `cd` command, or use its desktop **Open folder**
action and select `my-workspace`. If the assistant itself is not installed, follow its own install
guide first; the workspace does not require a particular vendor.

Your first message should be:

> Read AGENTS.md and introduce yourself.

The assistant should immediately say the workspace is uninitialised and start onboarding. If it
answers an unrelated task first, tell it: `Run the onboarding playbook in core/onboarding/ONBOARDING.md now.`

## What onboarding does

The assistant handles the files; you only answer and confirm:

1. It asks for the workspace name, entity, owner name, agent name, root environment-variable name,
   and optional shared-context path.
2. It derives two safe slugs and today's date, shows all nine values, and waits for your **yes**.
3. It writes `values.json` at the workspace root and runs the atomic onboarding engine. Invalid
   values change nothing; interruption is recovered on the next run.
4. It sets the live identity and current focus, appends the first journal event, then removes
   `.uninitialised`. That sentinel is removed last, so an interrupted interview always resumes.

Success means the assistant says the workspace is live. On the next session the onboarding gate is
silent and the normal session brief appears. Keep [`folder-agent-workspace/REFERENCE.md`](folder-agent-workspace/REFERENCE.md)
for the after-week-one file map, script list, memory search, hook checks, backup, updates, and
uninstall.

## Install a different member or path

The default creates the workspace most people need. These argument forms are also supported:

**Another workspace** (each additional one just needs its own name):

```bash
curl -fsSL https://raw.githubusercontent.com/CORBEL-Technology/agent-workspace-templates/main/install.sh | sh -s -- ~/second-workspace
```

**The shared brain** that sits above several workspaces (at `~/my-shared`):

```bash
curl -fsSL https://raw.githubusercontent.com/CORBEL-Technology/agent-workspace-templates/main/install.sh | sh -s -- shared-context
```

**The versioned tooling registry** (at `~/my-registry`):

```bash
curl -fsSL https://raw.githubusercontent.com/CORBEL-Technology/agent-workspace-templates/main/install.sh | sh -s -- capability-registry
```

For both a member and a custom path, put the member first:
`... | sh -s -- shared-context ~/our-shared-brain`. Paths with spaces are supported and every
printed command will quote them safely.

## How memory behaves

The journal under `20_memory/journal/` is append-only truth. A bounded sleep pass turns supported
recurring evidence into small memory cards; the deterministic reaper then promotes, cools,
archives, or quarantines them according to `20_memory/homeostasis.yml`. Nothing is silently
deleted, and every asserted card must cite evidence. Prove the loop any time from inside the
workspace with `python3 tools/memory-selftest.py`.

## Add a second workspace and shared context

When two workspaces need the same identity and operating rules, create the shared store and another
workspace:

```text
curl -fsSL https://raw.githubusercontent.com/CORBEL-Technology/agent-workspace-templates/main/install.sh | sh -s -- shared-context
curl -fsSL https://raw.githubusercontent.com/CORBEL-Technology/agent-workspace-templates/main/install.sh | sh -s -- ~/my-workspace-two
```

Onboard each one with the same first message. The shared store's onboarding/linking instructions
then register each workspace; there is no need to add this layer when one workspace is enough.

## Something went wrong

Match the first line you see. Commands shown by the installer contain your real path; paste those
instead of retyping them.

| Exact message or screen text | What it means and the next action |
|---|---|
| `curl: command not found` | Run the `wget -qO- ... \| sh` alternative above, or `sudo apt install curl`, then paste the unchanged installer command again. |
| `install: git is not installed.` | Mac: run `xcode-select --install`. Ubuntu/WSL: run `sudo apt install git`. Then rerun the same installer command. |
| `install: Python 3 is not installed.` | Install Python from `https://python.org/downloads`; Ubuntu/WSL can run `sudo apt install python3`. Then rerun. |
| `install: Python 3.8 or newer is required` | Upgrade Python; a version such as 3.12 is suitable. Then rerun. |
| `instantiate: git needs your name and email before it can create the first save.` | Run the two `git config --global ...` commands printed immediately below it, replacing the examples, then paste the printed retry command. No workspace was created. |
| `Valid members: folder-agent-workspace, shared-context, capability-registry.` | The member name was mistyped. Paste the suggested command printed underneath. |
| `install: download failed. No partial template download was kept; any existing workspace was untouched.` | Restore the internet connection, then paste the exact retry command printed underneath. |
| `exists but is not a complete template download.` | Paste the printed `rm -rf -- 'agent-workspace-templates'` command, then paste the printed retry command. Only the incomplete download is removed. |
| `install: PyYAML could not be downloaded.` | Restore the internet connection, then paste the printed retry command. No workspace files were changed. |
| `system Python is protected (PEP 668); using an isolated .venv` | This is not an error. At the end, paste both `cd '...'` and `. .venv/bin/activate`; repeat the activation whenever you reopen the workspace. |
| `install: Python could not create a virtual environment` | Ubuntu/WSL: run `sudo apt install python3-venv`, then paste the printed retry command. A just-created workspace is removed; a resumed existing workspace is kept. |
| `-> a fresh workspace already exists at ...; resuming the dependency check without overwriting it` | A previous run already copied the workspace. Let this run finish, then follow its `Done. Next step:` commands. |
| `install: a workspace already exists at ... Nothing was overwritten.` | Paste the printed `cd '...'` command to open the existing workspace. |
| `install: the target already exists:` | Nothing was overwritten. Paste the printed example command ending in `-new`, or choose another unused path. |
| `[onboarding-gate] This workspace is UNINITIALISED` | Expected on first open. Tell the assistant to read and follow `core/onboarding/ONBOARDING.md` before other work. |
| `values.json is in the wrong place:` | Paste the two printed commands: the first moves it to the workspace root, the second reruns onboarding. |
| `values.json is missing from the workspace root:` | The interview has not written its confirmed values yet. Resume the onboarding interview; do not create guesses by hand. |
| `values.json is not valid JSON:` | Ask the assistant to correct the root `values.json`, then paste `python3 core/onboarding/apply.py --root .`. No workspace files changed. |
| `values.json has invalid values:` | Read every listed key, correct it to the stated rule, then paste `python3 core/onboarding/apply.py --root .`. No workspace files changed. |
| `apply.py: recovered an interrupted earlier run` | Recovery succeeded and the command is safely restarting. Let it finish. |
| `apply.py: nothing to do — no values.json and no leftover tokens (already applied). exit 0.` | The fill already completed; continue with identity/current-focus/journal setup and remove the sentinel last. |
| `apply.py: PyYAML is missing.` | If `.venv` exists, paste `. .venv/bin/activate`, then rerun the exact apply command printed. Otherwise rerun the family installer. |
| The assistant cannot see files or no session brief appears | Close it, paste the installer's `cd '...'` command, activate `.venv` if present, and reopen it. Then check the adapter entry in `core/RUNTIMES.md`. |
| `Permission denied` | Move the template/workspace under your home folder; do not use `sudo` to run the installer or workspace. |

Still stuck? Open an issue at
[github.com/CORBEL-Technology/agent-workspace-templates/issues](https://github.com/CORBEL-Technology/agent-workspace-templates/issues)
and paste exactly what you typed plus the complete message. No terminal knowledge is assumed.

## What next

The workspace stands alone. Read [FAMILY.md](FAMILY.md) only when you want shared context across
several workspaces or a registry for keeping their deterministic tooling in sync.
