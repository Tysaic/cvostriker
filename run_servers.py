import subprocess
import signal
import sys

def run_server(script, port):
    print(f'[+] starting application service "{script[1]}" on port {port}')
    return subprocess.Popen(['python', script[0], '--port', str(port)], shell=True)

# CTRL + C to stop the servers

def signal_handler(sig, frame):
    print('[!] STOPPING SERVERS')
    print("[!] Press ctrl+c to shutdown servers")
    for server in servers:
        server.terminate()
    sys.exit(0)


if __name__ == '__main__':
    applications_names = [
        ('app.py', 'admin')
    ]
    servers = [
        run_server(applications_names[0], 5000),
    ]

    # Signal handler ctrl + c => signal.SIGINT
    signal.signal(signal.SIGINT, signal_handler)

    for server in servers:
        # running on background each server
        server.wait()