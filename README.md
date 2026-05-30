MultiShell

A lightweight and powerful reverse shell payload generator with built-in listener and exploit mode. Designed for penetration testers and red teamers who need stealthy, customizable payloads in multiple languages.

---

## Features

- Multi-language reverse shell generator (Bash, PowerShell, PHP, Java, JS)
- Modes: manual / silent / batch / autorun / exploit
- Obfuscation options (Base64, Hex, Gzip+Base64)
- Stealth mode (fake file names + timestomped dates)
- Interactive listener with live command execution and logging
- Auto-export to EXE (PowerShell payloads only)
- All payloads saved under `output/`

---

## Requirements

- Python 3.6+
- `colorama`, `pyinstaller` (optional for EXE export)
- Linux/Unix or Termux (some payloads are *nix-based)

```bash
pip install colorama
```

To enable `.exe` exports:

```bash
pip install pyinstaller
```

---

* Usage*

```bash
python main.py
```

Then select mode:
```
[1] manual> build a single payload manually
[2] silent> load from config.json
[3] batch> generate all payloads
[4] autorun> use config & generate automatically
[5] exploit> open listener & control target
```

---

*🔧 Example: Manual Mode*

- Choose payload language
- Enter LHOST/LPORT
- Select obfuscation level
- Toggle stealth mode (optional)

All payloads are saved under `output/`.

---

*📡 Exploit Mode (Listener)*

```bash
Select mode: 5
Enter LHOST to listen on (default YOUR-IP):
Enter LPORT to listen on (default 4444):
```

When a reverse shell connects, you'll get:

```
💀 Shell> whoami
target-user
 Shell> ifconfig
...
```

All session logs saved to `sessions.log`.

---

* Legal Disclaimer*

This tool is created for *educational and authorized penetration testing* purposes only. Misuse of this tool may violate local and international laws. Use responsibly and only on systems you are explicitly allowed to test.

---

* File Structure*

```
multi-shell-gen/
├── main.py
├── config.json
├── output/
├── sessions.log
├── payloads/
│   ├── bash.py
│   ├── powershell.py
│   ├── php.py
│   ├── java.py
│   └── js.py
└── session_logger.py
```

*Credits*

Crafted with  by Ahmed Altayeb 