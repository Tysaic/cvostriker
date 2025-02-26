import subprocess
import signal
import sys

def run_server(script, port):
    print(f'[+] starting application server "{script}" on port {port}')
    return subprocess.Popen(['python', script, '--port', str(port)], shell=True)

# CTRL + C to stop the servers

def signal_handler(sig, frame):
    print('[!] STOPPING SERVERS')
    print("[!] Press ctrl+c to shutdown servers")
    for server in servers:
        server.terminate()
    sys.exit(0)


if __name__ == '__main__':
    servers = [
        run_server('main.py', 5000),
        run_server('public/app.py', 5001),
        run_server('admin/app.py', 5002),
    ]

    # Signal handler ctrl + c => signal.SIGINT
    signal.signal(signal.SIGINT, signal_handler)

    for server in servers:
        # running on background each server
        server.wait()