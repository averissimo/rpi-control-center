import subprocess
import os.path
import os
import time
from pathlib import Path
from flask import Flask, render_template, redirect, request
import re

import socket # ip
import fcntl # ip
import struct # ip

def get_ip_address(ifname):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(
                fcntl.ioctl(
                    s.fileno(),
                    0x8915, # SIOCGIFADDR
                    struct.pack('256s'.encode('utf-8'), ifname[:15].encode('utf-8'))
                )[20:24]
        )
    except Exception as e:
        return "Error {}: {}".format(e.__class__, e)


app = Flask(__name__)

file_path = '/home/pi/work/monitor/sensors-sht31/screen_on.txt'

def is_netgear_activated():
  return subprocess.run(['wpa_cli', '-i', 'wlan1', 'get_network', '5', 'disabled'], text = True, capture_output = True).stdout.strip() == "0"


@app.route('/')
def index(message = ""):
  wifi = subprocess.run(['iwgetid', 'wlan1', '-r'], text = True, capture_output = True).stdout.strip()
  ip = get_ip_address('wlan1')
  bitrate = ''
  with open('/proc/net/wireless', 'r') as f:
    for line in f.readlines():
        if 'wlan1' in line:
            bitrate = line.split()[2:4]
            bitrate = 'quality: ' + bitrate[0] + ' signal: ' + bitrate[1] + 'dBm'

  ch = subprocess.run(['iwgetid', 'wlan1', '-c', '-r'], text = True, capture_output = True).stdout.strip()
  ap = subprocess.run(['iwgetid', '-a', '-r', 'wlan1'], text = True, capture_output = True).stdout.strip()
  return render_template(
          'template.html', 
          message = message, 
          screen = os.path.isfile(file_path), 
          wifi = wifi, 
          ap = ap, 
          bitrate = bitrate, 
          channel = ch, 
          netgear = is_netgear_activated(),
          ip = ip
  )

@app.route('/restart_dns/')
def restart_dns():
    subprocess.run(['sudo', '-u', 'pi', '/usr/local/bin/docker-compose', '--file', '/home/pi/work/pihole/docker-compose.yml', 'restart'], capture_output=True)
    return redirect('/restarted_dns')

@app.route('/restarted_dns/')
def restarted_dns():
    message = 'dns restarted, wait a minute...'
    return index(message = message)

@app.route('/select_mlan/')
def select_mlan():
  if is_netgear_activated():
      subprocess.run(['wpa_cli', '-i', 'wlan1', 'select', '7'])
  return redirect('/mlan_selected')

@app.route('/mlan_selected/')
def mlan_selected():
  message = 'mlan was selected'
  return index(message = message)

@app.route('/select_eduroam/')
def select_eduroam():
  subprocess.run(['wpa_cli', '-i', 'wlan1', 'select', '2'])
  return redirect('/eduroam_selected')

@app.route('/eduroam_selected/')
def eduroam_selected():
  message = 'eduroam was selected'
  return index(message = message)

@app.route('/toggle_netgear/')
def toggle_netgear():
  if is_netgear_activated():
      subprocess.run(['wpa_cli', '-i', 'wlan1', 'disable', '5'])
  else:
      subprocess.run(['wpa_cli', '-i', 'wlan1', 'enable', '5'])
  return redirect('/netgear_toggled')

@app.route('/netgear_toggled/')
def netgear_toggled():
  message = 'netgear30 was disabled'
  if is_netgear_activated():
      message = 'netgear30 was enabled! Please wait a few seconds for it to connect and refresh the page.'
  return index(message = message)

@app.route('/wifi_no_dns/')
def my_wifi_no_dns():
  subprocess.run(['sudo', 'rmmod', '8814au'])
  time.sleep(1)  
  subprocess.run(['sudo', 'modprobe', '8814au'])
  time.sleep(1)  
  subprocess.run(['wpa_cli', '-i', 'wlan1', 'reconfigure'])
  time.sleep(2)  
  subprocess.run(['wpa_cli', '-i', 'wlan1', 'reattach'])
  return redirect('/wifi_done')

@app.route('/wifi/')
def my_wifi():
  #subprocess.run(['sudo', 'nmcli', 'connection', 'up', '"Telekom_FON (...A0:C6)"'])
  subprocess.run(['wpa_cli', '-i', 'wlan1', 'reconfigure'])
  time.sleep(3)  
  subprocess.run(['wpa_cli', '-i', 'wlan1', 'reattach'])
  time.sleep(3)  
  subprocess.run(['sudo', '-u', 'pi', '/usr/local/bin/docker-compose', '--file', '/home/pi/work/pihole/docker-compose.yml', 'restart'], capture_output=True)
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
  subprocess.Popen(['sudo', 'shutdown', '-h', 'now'])
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
