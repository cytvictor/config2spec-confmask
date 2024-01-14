import os


from config2spec.topology.builder.builder import TopologyBuilder
from config2spec.topology.topology import NetworkTopology
from config2spec.topology.interface import Interface
from config2spec.topology.access_list import AccessList

from config2spec.utils.logger import get_logger


# initialize logging
logger = get_logger('NetHideTopologyGenerator', 'INFO')

class NetHideTopologyBuilder(TopologyBuilder):
    @staticmethod
    def build_topology(scenario_path):

        # interface_path = os.path.join(scenario_path, files["interfaces"])
        # all_interfaces = NetHideTopologyBuilder.parse_interfaces(interface_path)
        ifa1 = Interface('eth1')
        ifa1.set_ip_address('192.168.0.1', '192.168.0.1/24')
        ifb1_1 = Interface('eth1')
        ifb1_1.set_ip_address('192.168.0.2', '192.168.0.2/24')


        ifa2 = Interface('eth2')
        ifa2.set_ip_address('192.168.1.1', '192.168.1.1/24')
        ifb2_1 = Interface('eth1')
        ifb2_1.set_ip_address('192.168.1.2', '192.168.1.2/24')
    
        ifb1_2 = Interface('eth1')
        ifb1_2.set_ip_address('192.168.3.2', '192.168.3.2/24')
        ifc1 = Interface('eth1')
        ifc1.set_ip_address('192.168.3.1', '192.168.3.1/24')

        ifb2_2 = Interface('eth1')
        ifb2_2.set_ip_address('192.168.4.2', '192.168.4.2/24')
        ifc2 = Interface('eth1')
        ifc2.set_ip_address('192.168.4.1', '192.168.4.1/24')
        

        ifa3 = Interface('eth3')
        ifa3.set_ip_address('10.0.1.1', '10.0.1.1/24')

        # a (ifa1:eth1) - (ifb1_1:eth1) b1 (ifb1_2:eth2) - (ifc1:eth1) c
        #   (ifa2:eth2) - (ifb2_1:eth1) b2 (ifb2_2:eth2) - (ifc2:eth2) c
        all_interfaces = {
          'a': { 'eth1': ifa1, 'eth2': ifa2, 'eth3': ifa3 },
          'b1': { 'eth1': ifb1_1, 'eth2': ifb1_2 },
          'b2': { 'eth1': ifb2_1, 'eth2': ifb2_2 },
          'c': { 'eth1': ifc1, 'eth2': ifc2 },
        }

        # acls_path = os.path.join(scenario_path, files["acls"])
        # all_access_lists = NetHideTopologyBuilder.parse_acls(acls_path)
        all_access_lists = {
            'a': {},
            'b1': {},
            'b2': {},
            'c': {},
        }

        # topology_path = os.path.join(scenario_path, files["topology"])
        # routers, edges = NetHideTopologyBuilder.parse_topology(topology_path)
        routers = set(['a', 'b1', 'b2', 'c'])# 'c', 'd', 'e', 'f'])
        edges = set([
            ('a', 'eth1', 'b1', 'eth1'),
            ('a', 'eth2', 'b2', 'eth1'),
            ('b1', 'eth2', 'c', 'eth1'),
            ('b2', 'eth2', 'c', 'eth2'),

            # and vice versa
            ('b1', 'eth1', 'a', 'eth1'),
            ('b2', 'eth1', 'a', 'eth2'),
            ('c', 'eth1', 'b1', 'eth2'),
            ('c', 'eth2', 'b2', 'eth2'),
        ])

        topology = NetworkTopology()
        for i, router in enumerate(routers):
            router_id = "r%d" % i
            interfaces, access_lists = all_interfaces[router], all_access_lists[router]
            topology.add_router(router, router_id, interfaces=interfaces, access_lists=access_lists)

        # LINKS maybe use the edge information
        for r1, r1_intf, r2, r2_intf in edges:
            topology.add_link(r1, r2, 1)
            topology.next_hops[r1][r1_intf] = r2

        return topology

