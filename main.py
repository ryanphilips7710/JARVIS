from startup import listen_claps
import subprocess

choice=input('Do u want to launch predefined? (y/n): ')
if choice.lower()=='y':
    listen_claps()

subprocess.Popen(
    ['cmd', '/k', 'python brain.py'],
    cwd=r'D:\Ryan\projects\JARVIS',  # your exact path
    creationflags=subprocess.CREATE_NEW_CONSOLE)



