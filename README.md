# Op_portforward
demo of portfoward as a service with OpenStack netns arch ,aio-http service using tornado

### CentOS 7.2  Neutron l3-agent node

pip install tornado==4.4.1

python portfoward.py -log_file_prefix=portforward.log &

sample:

```
python>
>>> import requests
>>> url_add = "http://127.0.0.1:39696/addportforward"
>>> send = {"router_id":"eadb6bac-fb21-477a-8b16-cc4660c9f516","router_port":"222","protocol":"tcp","vm_ip":"10.1.100.14","vm_port":"22"}
>>> r = requests.post( url_add , send )
>>> r.text
u'{\n    "msg": "add portforward rule success", \n    "code": 200\n}'
```
![image](http://123.206.71.64/api_conffile1.png)
![image](http://123.206.71.64/api_res.png)
```
>>> url_del = "http://127.0.0.1:39696/delportforward"
>>> r2 = requests.post( url_del , send )
>>> r2.text
u'{\n    "msg": "del portforward rule success", \n    "code": 200\n}'
```
![image](http://123.206.71.64/api_conffile2.png)

#### warn
this is a demo http service, think twice before applying in production environment

please considerate more about data storage using DB instead

and data consistency , recovery just as Neutron did

---

#### contact me (weixin) :
###### OpenStack与云安全

 ![image](http://123.206.71.64/cloudsec.jpg)

  
