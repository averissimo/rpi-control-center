## Centro controlo da Framboesa

```
$ sudo apt-get install nginx supervisor
$ virtualenv -p python3 env
$ source env/bin/activate
$ pip install -r requirements.txt
$ pip install gunicorn
$ deactivate
$ sudo systemctl restart supervisor.service
```
