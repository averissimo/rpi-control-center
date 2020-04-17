## Centro controlo da Framboesa

```
$ sudo apt-get install nginx supervisor
$ virtualenv -p python3 env
$ source env/bin/activate
$ pip install --upgrade pip
$ pip install -r requirements.txt
$ deactivate
$ sudo systemctl restart supervisor.service
```
