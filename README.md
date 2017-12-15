# Netadmin-driver
## What's This?
- A service which send command or script to network device like Juniper or  Cisco ,then  get the results back to you when it's finished
- Proivde HTTP service with [tornado](https://github.com/tornadoweb/tornado)
- Multiple Execute Commands on devices
- It's built for providing driver service to [netadmin](https://github.com/pippozq/netadmin)
## Build  By

Package | Page
---|---
Python3.6|https://www.python.org/downloads/release/python-363/
Junos-eznc | https://github.com/Juniper/py-junos-eznc
Ansible | https://github.com/ansible/ansible
Tornado |https://github.com/tornadoweb/tornado


## Build
Provide Dockerfile, so you can build esaily using
```
docker build -t <your docker repository url>/netadmin-driver:<your version> .

```



## Web Interface

### Juniper
#####  Command

```
define a JSON named "json_data" like
{
 "hosts":["192.168.1.2","192.168.1.3".....],
 "port":22,
 "user": {
    "name":"ssh name",
    "password":"ssh password"
    },
 "command": "show version"
 }
```

```
curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d post_data 'http://netadmin-driver-url/juniper/command'
```
#####  Config

```
define a JSON named "json_data" like
{
 "hosts":["192.168.1.2","192.168.1.3".....],
 "port":22,
 "user": {
    "name":"ssh name",
    "password":"ssh password"
    },
 "file_content": "line1\nline2\n""
 }
```
```
curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d post_data 'http://netadmin-driver-url/juniper/config'
```



### Cisco
##### Command

```
define a JSON named "json_data" like
{
 "hosts":["192.168.1.2","192.168.1.3".....],
 "port":22,
 "user": {
    "name":"ssh name",
    "password":"ssh password"
    },
 "command": "show version"
 }
```

```
curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d post_data 'http://netadmin-driver-url/cisco/command'
```
#### Config

```
define a JSON named "json_data" like
{
 "hosts":["192.168.1.2","192.168.1.3".....],
 "port":22,
 "user": {
    "name":"ssh name",
    "password":"ssh password"
    },
 "file_content": "line1\nline2\n",
 "blob_id":"Forza_Milan"
 }
```
```
curl -X POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d post_data 'http://netadmin-driver-url/cisco/config'
```
"blob_id" is the gitlab file id,it's used for the temporary file name, so you can use any thing to rename it. I prefer "Forza_Milan"

## License
GNU General Public License v3.0