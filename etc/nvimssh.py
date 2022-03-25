#!/usr/bin/env python3
'''
Created on 2022/03/24

@author: is2225
'''
import paramiko
import os.path
import subprocess
import concurrent.futures
import time
from getpass import getpass

NVIM_SERVER = "nvim --listen {0}:7777 --headless";
NVIM_CLIENT = "nvim-qt --no-ext-tabline --no-ext-popupmenu --server {0}:7777";

SETTINGS = os.path.join(os.path.expanduser("~"), ".nvimssh")

def exec_sshcommand(server, user, passwd, command):
    with paramiko.SSHClient() as client:
        client.set_missing_host_key_policy(paramiko.WarningPolicy())
        try:
            client.connect(server, username = user, password = passwd)
            client.exec_command(command)
        except:
            pass

def save_params(params):
    if params:
        data = "\n".join(params)
        with open(SETTINGS, mode = "wt") as f:
            f.write(data)

def read_params():
    params = []
    if os.path.isfile(SETTINGS):
        data = None
        with open(SETTINGS, mode = "rt") as f:
            data = f.read()
        if data:
            params = data.split(sep="\n")
    return params

def run():
    
    server = ""
    user = ""
    passwd = ""

    params = read_params()
    if params and len(params) >= 3:
        server = params[0]
        user = params[1]
        passwd = params[2]

    inputed_server = input("Server [{0}]: ".format(server) if server else "Server: ")
    if inputed_server:
        server = inputed_server
    if not server:
        return 
    
    inputed_user = input("User [{0}]: ".format(user) if user else "User: ")
    if inputed_user:
        user = inputed_user
    if not user:
        return 
    
    inputed_passwd = getpass("Password [****]: " if passwd else "Password: ")
    if inputed_passwd:
        passwd = inputed_passwd
    if not passwd:
        return

    svr = None
    lcl = None
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers = 1) as executor:
            svr = executor.submit(exec_sshcommand, server, user, passwd, NVIM_SERVER.format(server))
        time.sleep(1)
        lcl = subprocess.Popen(NVIM_CLIENT.format(server), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass
    
    if svr and lcl:
        while True:
            if svr.done() or lcl.poll():
                break
            time.sleep(0.1)
    
    if svr and not svr.done():
        exec_sshcommand(server, user, passwd, "killall nvim")
    
    if lcl and not lcl.poll():
        lcl.terminate()
    
    save_params([server, user, passwd])
    

if __name__ == '__main__':
    run()
