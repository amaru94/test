# AutoFix ChatBot (Windows EXE Ready)

A lightweight chatbot-style IT support assistant for call centers using **Five9**, **Genesys**, and **NICE**.

It reads issue descriptions, matches them to routing rules, and then suggests or runs scripts/flows from `C:\AutoFix\`.

## Folder assumptions

The app expects this structure (existing or auto-created):

- `C:\AutoFix\logs`
- `C:\AutoFix\scripts`
- `C:\AutoFix\tools`
- `C:\AutoFix\flows`

Routing file:

- `C:\AutoFix\flows\routing_rules.json`

## Features

- Chat-style terminal interaction.
- Keyword routing to scripts/flows.
- Default rules for Five9 / Genesys / NICE.
- Dry-run mode by default (safe).
- Optional execution mode with `AUTOFIX_ALLOW_EXECUTE=1`.
- Daily interaction logs in `C:\AutoFix\logs`.

## Run locally

```bash
python autofix_chatbot.py
```

## Build Windows EXE

On a Windows machine with Python installed:

```bat
build_windows_exe.bat
```

Output:

- `dist\AutoFixChatBot.exe`

## Customize routing

Edit `C:\AutoFix\flows\routing_rules.json` and add new rules:

```json
{
  "name": "VPN reset",
  "keywords": ["vpn", "disconnect", "forticlient"],
  "action_type": "script",
  "action_path": "scripts/vpn_fix.ps1",
  "notes": "Restart VPN services and clear cached creds"
}
```

## Safety notes

- Keep script execution disabled until scripts are validated.
- Restrict write permissions on `C:\AutoFix`.
- Digitally sign scripts and EXE for enterprise environments.
