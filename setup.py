import psutil
import json
import inquirer

# Print prettified json
def jprint(args):
    print(json.dumps(args, indent=4, sort_keys=True))

class MainController:
    
    def __init__(self):
        iface = self.get_iface()
        self.ip_addr = self.get_ip_addr()

    # Get available interfaces
    def get_iface(self):
        return [k for k in psutil.net_if_addrs()]

    # Get ip addres from selected interfaces
    def get_ip_addr(self, iface='lo'):
        return psutil.net_if_addrs()

worker = MainController()

