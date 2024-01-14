import os
import pickle
import ipaddress

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
        data = pickle.load(open(os.path.join(scenario_path, "data.pkl"), "rb"))
        # print(data)

        # interface_path = os.path.join(scenario_path, files["interfaces"])
        # all_interfaces = NetHideTopologyBuilder.parse_interfaces(interface_path)
        # ifa1 = Interface('eth1')
        # ifa1.set_ip_address('192.168.0.1', '192.168.0.1/24')
        # ifb1_1 = Interface('eth1')
        # ifb1_1.set_ip_address('192.168.0.2', '192.168.0.2/24')


        # ifa2 = Interface('eth2')
        # ifa2.set_ip_address('192.168.1.1', '192.168.1.1/24')
        # ifb2_1 = Interface('eth1')
        # ifb2_1.set_ip_address('192.168.1.2', '192.168.1.2/24')
    
        # ifb1_2 = Interface('eth1')
        # ifb1_2.set_ip_address('192.168.3.2', '192.168.3.2/24')
        # ifc1 = Interface('eth1')
        # ifc1.set_ip_address('192.168.3.1', '192.168.3.1/24')

        # ifb2_2 = Interface('eth1')
        # ifb2_2.set_ip_address('192.168.4.2', '192.168.4.2/24')
        # ifc2 = Interface('eth1')
        # ifc2.set_ip_address('192.168.4.1', '192.168.4.1/24')
        

        # ifa3 = Interface('eth3')
        # ifa3.set_ip_address('10.0.1.1', '10.0.1.1/24')

        # a (ifa1:eth1) - (ifb1_1:eth1) b1 (ifb1_2:eth2) - (ifc1:eth1) c
        #   (ifa2:eth2) - (ifb2_1:eth1) b2 (ifb2_2:eth2) - (ifc2:eth2) c
        all_interfaces = {
        #   'a': { 'eth1': ifa1, 'eth2': ifa2, 'eth3': ifa3 },
        #   'b1': { 'eth1': ifb1_1, 'eth2': ifb1_2 },
        #   'b2': { 'eth1': ifb2_1, 'eth2': ifb2_2 },
        #   'c': { 'eth1': ifc1, 'eth2': ifc2 },
        }

        # acls_path = os.path.join(scenario_path, files["acls"])
        # all_access_lists = NetHideTopologyBuilder.parse_acls(acls_path)
        all_access_lists = {
            # 'a': {},
            # 'b1': {},
            # 'b2': {},
            # 'c': {},
        }

        # topology_path = os.path.join(scenario_path, files["topology"])
        # routers, edges = NetHideTopologyBuilder.parse_topology(topology_path)
        # routers = set(['a', 'b1', 'b2', 'c'])# 'c', 'd', 'e', 'f'])
        edges = set([
            # ('a', 'eth1', 'b1', 'eth1'),
            # ('a', 'eth2', 'b2', 'eth1'),
            # ('b1', 'eth2', 'c', 'eth1'),
            # ('b2', 'eth2', 'c', 'eth2'),

            # # and vice versa
            # ('b1', 'eth1', 'a', 'eth1'),
            # ('b2', 'eth1', 'a', 'eth2'),
            # ('c', 'eth1', 'b1', 'eth2'),
            # ('c', 'eth2', 'b2', 'eth2'),
        ])
        
        for src_node in data['node_neighbors']:
            for neighbor_node in data['node_neighbors'][src_node]:
                src_node_to_neighbor_interface = data['node_neighbors'][src_node][neighbor_node]
                if src_node not in all_interfaces:
                    all_interfaces[src_node] = {}
                
                intf = Interface(src_node_to_neighbor_interface[0])
                intf.set_ip_address(src_node_to_neighbor_interface[1], src_node_to_neighbor_interface[2])
                all_interfaces[src_node][src_node_to_neighbor_interface[0]] = intf

                # edge
                edge = (src_node, src_node_to_neighbor_interface[0], neighbor_node, data['node_neighbors'][neighbor_node][src_node][0])
                edges.add(edge)
            if src_node not in all_access_lists:
                all_access_lists[src_node] = {}
        
        for origin_node in data['node_networks']:
            network_interface = data['node_networks'][origin_node]
            intf = Interface(network_interface[0])
            intf.set_ip_address(list(ipaddress.ip_network(network_interface[1]).hosts())[0], network_interface[1])
            all_interfaces[origin_node][network_interface[0]] = intf

        routers = set(data['node_neighbors'].keys())
        # print(all_interfaces)
        # print(all_access_lists)
        # print(routers)
        # print(edges)
        # exit()

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

