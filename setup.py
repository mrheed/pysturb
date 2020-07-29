import psutil
import json
import inquirer
import socket
import scapy

# Print prettified json
def jprint(args):
    print(json.dumps(args, indent=4, sort_keys=True))

# Print pretiffied instance attributes
def pprint(args):
    jprint(vars(args))

class Pysturb:
    def __init__(self):
        self.iface_list = self.get_iface_list()
        self.iface_selected = 'lo'
        self.ip_addr = None
        self.ipv6_addr = None
        self.mac_addr = None

    # Display interface selection menu
    def prompt_select_iface(self):
        questions = [
            inquirer.List(
                "iface",
                message="Select network interface",
                choices=self.iface_list
            )
        ]
        ans = inquirer.prompt(questions)['iface']
        self.iface_selected = ans
        self.ip_addr = self.get_addr(ans)
        self.ipv6_addr = self.get_addr(ans, t_addr='IPv6') 
        self.mac_addr = self.get_addr(ans, t_addr='MAC')

    # Get available interfaces
    def get_iface_list(self):
        return [k for k in psutil.net_if_addrs()]

    # Get ip addres from selected interfaces
    def get_addr(self, iface='lo', t_addr='IPv4'):
        af_map = {socket.AF_INET: 'IPv4', socket.AF_INET6: 'IPv6', psutil.AF_LINK: 'MAC'}
        addrs = dict()
        for addr in psutil.net_if_addrs()[iface]:
            addrs[af_map.get(addr.family)] = addr.address
        return addrs.get(t_addr)

worker = Pysturb()
#worker.prompt_select_iface()

