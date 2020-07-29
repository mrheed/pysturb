# import psutil
import json
import inquirer
import socket
# import netifaces
import scapy.all as scapy

# Print prettified json
def jprint(args):
    print(json.dumps(args, indent=4, sort_keys=True))

# Print pretiffied instance attributes
def pprint(args):
    jprint(vars(args))

class Pysturb:
    def __init__(self):
        self.iface_list = self.get_iface_list()
        # self.iface = None
        # self.ip_addr = None
        # # self.ipv6_addr = None
        # self.gateway = None
        # # self.gateway_v6 = None
        # self.mac_addr = None
        # self.targets = None

    # Display interface selection menu
    def prompt_select_iface(self):
        if not self.iface_list:
            print("No available network interface found!")
            return

        questions = [
            inquirer.List(
                "iface",
                message="Select network interface",
                choices=self.iface_list
            )
        ]
        iface = inquirer.prompt(questions)['iface']
        self.iface = iface
        self.ip_addr = scapy.get_if_addr(iface)
        self.mac_addr = scapy.get_if_hwaddr(iface)
        self.gateway = scapy.conf.route.route('0.0.0.0')[2]
        self.targets = self.scan_targets()

    # Get available interfaces
    def get_iface_list(self):
        return [i for i in scapy.get_if_list() if i != 'lo']

    def scan_targets(self):
        #sementara:v
        ips=self.ip_addr + '/24'
        request = scapy.Ether(dst='ff:ff:ff:ff:ff:ff')/scapy.ARP(pdst=ips)
        ans, unans = scapy.srp(request, iface=self.iface, timeout=1, verbose=0)
        return [recv[scapy.ARP].psrc for send, recv in ans if recv]

worker = Pysturb()
worker.prompt_select_iface()
pprint(worker)

