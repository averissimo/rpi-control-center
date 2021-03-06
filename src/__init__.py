import subprocess
import os.path
import os
import time
from pathlib import Path
from flask import Flask, render_template, redirect, request
import re

app = Flask(__name__)

file_path = '/home/pi/sht31-rpi/screen_on.txt'

@app.route('/')
def index(message = ""):
  wifi = subprocess.run(['iwgetid', 'wlan1', '-r'], text = True, capture_output = True).stdout.strip()
  bitrate = ''
  with open('/proc/net/wireless', 'r') as f:
    for line in f.readlines():
        if 'wlan1' in line:
            bitrate = line.split()[2:4]
            bitrate = 'quality: ' + bitrate[0] + ' signal: ' + bitrate[1] + 'dBm'
  ap = subprocess.run(['iwgetid', '-a', '-r', 'wlan1'], text = True, capture_output = True).stdout.strip()
  return render_template('template.html', message = message, screen = os.path.isfile(file_path), wifi = wifi, ap = ap, bitrate = bitrate)

@app.route('/restart_dns/')
def restart_dns():
    subprocess.run(['sudo', '-u', 'pi', '/usr/local/bin/docker-compose', '--file', '/home/pi/pihole/docker-compose.yml', 'restart'], capture_output=True)
    return redirect('/restarted_dns')

@app.route('/restarted_dns/')
def restarted_dns():
    message = 'dns restarted, wait a minute...'
    return index(message = message)

@app.route('/wifi/')
def my_wifi():
  subprocess.run(['wpa_cli', '-i', 'wlan1', 'disconnect'])
  time.sleep(3)
  subprocess.run(['wpa_cli', '-i', 'wlan1', 'reconnect'])
  subprocess.run(['sudo', '-u', 'pi', '/usr/local/bin/docker-compose', '--file', '/home/pi/pihole/docker-compose.yml', 'restart'], capture_output=True)
  return redirect('/wifi_done')

@app.route('/wifi_done/')
def wifi_done():
  message = 'O wifi foi reiniciado!'
  return index(message = message)

@app.route('/reboot/')
def my_reboot():
  subprocess.run(['sudo', 'shutdown', '-r', 'now'])
  return redirect('/bye')

@app.route('/shutdown_20/')
def my_shutdown_20():
  subprocess.run(['sudo', 'shutdown', '-h', '+20'])
  return redirect('/bye')

@app.route('/shutdown_120/')
def my_shutdown_120():
  subprocess.run(['sudo', 'shutdown', '-h', '+120'])
  return redirect('/bye')

@app.route('/shutdown/')
def my_shutdown():
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
