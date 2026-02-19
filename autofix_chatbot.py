#!/usr/bin/env python3
"""AutoFix ChatBot for call-center desktop IT support.

This app routes an issue description to a script or flow inside C:\\AutoFix.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

AUTO_FIX_ROOT = Path(os.getenv("AUTO_FIX_ROOT", r"C:\AutoFix"))
LOG_DIR = AUTO_FIX_ROOT / "logs"
FLOWS_DIR = AUTO_FIX_ROOT / "flows"
SCRIPTS_DIR = AUTO_FIX_ROOT / "scripts"
TOOLS_DIR = AUTO_FIX_ROOT / "tools"
ROUTING_FILE = FLOWS_DIR / "routing_rules.json"


@dataclass
class RoutingRule:
    name: str
    keywords: list[str]
    action_type: str
    action_path: str
    notes: str = ""

    def score(self, issue_text: str) -> int:
        return sum(1 for kw in self.keywords if re.search(rf"\b{re.escape(kw.lower())}\b", issue_text))


class AutoFixChatBot:
    def __init__(self, allow_execute: bool = False) -> None:
        self.allow_execute = allow_execute
        self._ensure_structure()
        self._seed_default_assets()
        self.rules = self._load_rules()

    def _ensure_structure(self) -> None:
        for folder in (LOG_DIR, FLOWS_DIR, SCRIPTS_DIR, TOOLS_DIR):
            folder.mkdir(parents=True, exist_ok=True)


    def _seed_default_assets(self) -> None:
        assets = {
            SCRIPTS_DIR / "five9_audio_fix.ps1": "Write-Host \"Five9 audio placeholder fix script.\"\n",
            SCRIPTS_DIR / "genesys_login_fix.ps1": "Write-Host \"Genesys login placeholder fix script.\"\n",
            FLOWS_DIR / "nice_capture_reset.md": "# NICE Capture Reset\n1. Restart NICE capture service.\n2. Validate test call recording.\n",
        }
        for path, content in assets.items():
            if not path.exists():
                path.write_text(content, encoding="utf-8")

    def _load_rules(self) -> list[RoutingRule]:
        if not ROUTING_FILE.exists():
            self._seed_default_rules()
        with ROUTING_FILE.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        rules: list[RoutingRule] = []
        for item in payload.get("rules", []):
            rules.append(
                RoutingRule(
                    name=item["name"],
                    keywords=[kw.lower() for kw in item.get("keywords", [])],
                    action_type=item["action_type"],
                    action_path=item["action_path"],
                    notes=item.get("notes", ""),
                )
            )
        return rules

    def _seed_default_rules(self) -> None:
        template = {
            "rules": [
                {
                    "name": "Five9 softphone audio repair",
                    "keywords": ["five9", "audio", "no sound", "mic", "headset"],
                    "action_type": "script",
                    "action_path": "scripts/five9_audio_fix.ps1",
                    "notes": "Restart audio services and clear Five9 cache.",
                },
                {
                    "name": "Genesys login refresh",
                    "keywords": ["genesys", "login", "token", "sso", "loop"],
                    "action_type": "script",
                    "action_path": "scripts/genesys_login_fix.ps1",
                    "notes": "Clear stale auth tokens and reopen workspace.",
                },
                {
                    "name": "NICE screen capture reset",
                    "keywords": ["nice", "recording", "screen", "capture", "frozen"],
                    "action_type": "flow",
                    "action_path": "flows/nice_capture_reset.md",
                    "notes": "Guided manual steps for capture service reset.",
                },
            ]
        }
        with ROUTING_FILE.open("w", encoding="utf-8") as fh:
            json.dump(template, fh, indent=2)

    def route_issue(self, issue: str) -> RoutingRule | None:
        normalized = issue.lower()
        scored = sorted(((rule.score(normalized), rule) for rule in self.rules), key=lambda x: x[0], reverse=True)
        if not scored or scored[0][0] == 0:
            return None
        return scored[0][1]

    def execute_rule(self, rule: RoutingRule) -> str:
        target = AUTO_FIX_ROOT / Path(rule.action_path)
        if not target.exists():
            return f"Target file not found: {target}"

        if rule.action_type == "flow":
            return f"Open flow instructions: {target}"

        if not self.allow_execute:
            return f"[Dry run] Suggested script: {target}"

        cmd = self._build_command(target)
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return (
            f"Executed: {' '.join(shlex.quote(x) for x in cmd)}\n"
            f"Exit code: {result.returncode}\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )

    @staticmethod
    def _build_command(script_path: Path) -> list[str]:
        suffix = script_path.suffix.lower()
        if suffix == ".ps1":
            return ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_path)]
        if suffix == ".bat":
            return ["cmd", "/c", str(script_path)]
        if suffix == ".py":
            return ["python", str(script_path)]
        return [str(script_path)]

    def log_interaction(self, issue: str, response: str) -> Path:
        stamp = dt.datetime.now().strftime("%Y%m%d")
        log_file = LOG_DIR / f"autofix_chat_{stamp}.log"
        line = f"[{dt.datetime.now().isoformat(timespec='seconds')}] ISSUE={issue} | RESPONSE={response}\n"
        with log_file.open("a", encoding="utf-8") as fh:
            fh.write(line)
        return log_file


def print_banner() -> None:
    print("=" * 70)
    print("AutoFix IT ChatBot - Call Center Quick Repair Assistant")
    print("Targets: Five9, Genesys, NICE, and custom local flows/scripts")
    print("Type 'exit' to quit.")
    print("=" * 70)


def interactive_loop(chatbot: AutoFixChatBot) -> None:
    print_banner()
    while True:
        issue = input("\nDescribe the issue: ").strip()
        if issue.lower() in {"exit", "quit"}:
            print("Goodbye.")
            return
        if not issue:
            print("Please type a short problem description.")
            continue

        rule = chatbot.route_issue(issue)
        if not rule:
            response = "I could not map this issue to a known flow/script. Please escalate or add a new rule."
        else:
            execution_result = chatbot.execute_rule(rule)
            response = (
                f"Match: {rule.name}\n"
                f"Action Type: {rule.action_type}\n"
                f"Action: {rule.action_path}\n"
                f"Notes: {rule.notes}\n"
                f"Result:\n{execution_result}"
            )

        log_file = chatbot.log_interaction(issue, response.replace("\n", " | "))
        print("\n" + response)
        print(f"Log saved to: {log_file}")


def main() -> None:
    allow_execute = os.getenv("AUTOFIX_ALLOW_EXECUTE", "0") == "1"
    interactive_loop(AutoFixChatBot(allow_execute=allow_execute))


if __name__ == "__main__":
    main()
