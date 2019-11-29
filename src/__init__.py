import subprocess
import os.path
import os
from pathlib import Path
from flask import Flask, render_template, redirect, request

app = Flask(__name__)

file_path = '/home/pi/sht31-rpi/screen_on.txt'

@app.route('/')
def index(message = ""):
  return render_template('template.html', message = message, screen = os.path.isfile(file_path))

@app.route('/shutdown/')
def my_shutdown():
  if os.path.isfile(file_path):
    os.remove(file_path)
  subprocess.run(['sudo', 'shutdown', '-h', 'now'])
  return redirect('/bye')

@app.route('/bye/')
def down():
  message = 'A framboesa está a desligar-se!'
  return index(message = message)

@app.route('/screen/')
def my_screen():
  if os.path.isfile(file_path):
    os.remove(file_path)
    return redirect('/screen_off')
  else:
    Path(file_path).touch()
    return redirect('/screen_on')

@app.route('/screen_off')
def screen_off():
    print(request.headers)
    message = 'Ecrã de temperatura/humidade foi desligado, o que pode demorar cerca de 5s.'
    return index(message);

@app.route('/screen_on')
def screen_on():
    message = 'Ecrã de temperatura/humidade foi ligado, o que pode demorar cerca de 5s.'
    return index(message);

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')