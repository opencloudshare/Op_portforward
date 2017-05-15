# -*- coding:utf-8 -*-
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import logging

import json
import re
import time
import commands
import ConfigParser

from tornado.options import define, options
define("port", default=39696, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/addportforward", AddPortforwardHandler),
                    (r"/delportforward", DelPortforwardHandler)]
     
        tornado.web.Application.__init__(self, handlers, debug=True)
        


class DelPortforwardHandler(tornado.web.RequestHandler):
    def post(self):
        router_id = self.get_body_argument("router_id")
        protocol = self.get_body_argument("protocol")
        vm_ip = self.get_body_argument("vm_ip")
        vm_port = self.get_body_argument("vm_port")
        router_port = self.get_body_argument("router_port")

        find_router_ip = "ip netns exec qrouter-{router_id} ifconfig |grep -A1 qg- | grep inet | awk '{{print $2}}'".format(router_id=router_id)
        (status, output) = commands.getstatusoutput(find_router_ip)
        router_gwip = output.strip()
        reg = '^((25[0-5]|2[0-4]\\d|[01]?\\d\\d?)($|(?!\\.$)\\.)){4}$'
        if not re.match(reg,router_gwip):
            msg = {'code':404,'msg':'no router matched by uuid'}
        else:
            cf = ConfigParser.ConfigParser()
            try:
                cf.read("portforward_conf")
		if cf.has_section(router_id):
			cf.remove_option(router_id,router_port)
		cf.write(open('portforward_conf', 'w'))
            except Exception,e:
                logging.info("file read error"+str(e))
            run_router_dnat = "ip netns exec qrouter-{router_id} iptables -t nat -D PREROUTING -d {router_gwip} -p {protocol} --dport {router_port} -j DNAT --to-destination {vm_ip}:{vm_port}".format(router_id=router_id,router_gwip=router_gwip,protocol=protocol,router_port=router_port,vm_ip=vm_ip,vm_port=vm_port)
            logging.info(run_router_dnat)
            (status, output) = commands.getstatusoutput(run_router_dnat)
            res_status = str(status)
            res_output = str(output)
            if not res_status =='0':
                logging.info(res_output)
                msg = {'code':500,'msg':res_output}
            else:
                msg = {'code':200,'msg':'del portforward rule success'}
        msg_js = json.dumps(msg,indent=4)
        self.write(msg_js)


class AddPortforwardHandler(tornado.web.RequestHandler):
    def post(self):
        router_id = self.get_body_argument("router_id")
        protocol = self.get_body_argument("protocol")
        vm_ip = self.get_body_argument("vm_ip")
        vm_port = self.get_body_argument("vm_port")
        router_port = self.get_body_argument("router_port")
        
        find_router_ip = "ip netns exec qrouter-{router_id} ifconfig |grep -A1 qg- | grep inet | awk '{{print $2}}'".format(router_id=router_id)
        (status, output) = commands.getstatusoutput(find_router_ip)
        router_gwip = output
        logging.info(output)
        reg = '^((25[0-5]|2[0-4]\\d|[01]?\\d\\d?)($|(?!\\.$)\\.)){4}$'
        if not re.match(reg,router_gwip):
            msg = {'code':404,'msg':'no router matched by uuid'}
        else:
            cf = ConfigParser.ConfigParser()
            try:
                cf.read("portforward_conf")
            except Exception,e:
                logging.info("file read error"+str(e)+" ,create new one")
                f=open('portforward_conf','w')
                f.close()
                cf.read("portforward_conf")
            
            if cf.has_section(router_id):
                cf.set(router_id,router_port,protocol+" "+vm_ip+" "+vm_port)
            else:
                cf.add_section(router_id)
                cf.set(router_id,router_port,protocol+" "+vm_ip+" "+vm_port)
            cf.write(open('portforward_conf', 'w'))

            run_router_dnat = "ip netns exec qrouter-{router_id} iptables -t nat -I PREROUTING -d {router_gwip} -p {protocol} --dport {router_port} -j DNAT --to-destination {vm_ip}:{vm_port}".format(router_id=router_id,router_gwip=router_gwip,protocol=protocol,router_port=router_port,vm_ip=vm_ip,vm_port=vm_port)
            logging.info(run_router_dnat)
            (status, output) = commands.getstatusoutput(run_router_dnat)
            res_status = str(status)
            res_output = str(output)
            if not res_status =='0':
                logging.info(res_output)
                msg = {'code':500,'msg':res_output}
            else:
                msg = {'code':200,'msg':'add portforward rule success'}
        msg_js = json.dumps(msg,indent=4)
        self.write(msg_js)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    logging.debug("debug ...")
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()




