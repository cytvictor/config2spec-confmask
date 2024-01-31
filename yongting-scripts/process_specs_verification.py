from pybatfish.datamodel.flow import PathConstraints
from pybatfish.client.session import Session, HeaderConstraints
import glob
import threading
import sys
import os


if len(sys.argv) != 3:
  print("Usage: python process_specs_verification.py <networks-name> <job-idx>")
  exit()

JOB_IDX = int(sys.argv[2])
NETWORKS_DIR = f"/home/yongting/research/configs/config2spec-confmask/scenarios/confmask/{sys.argv[1]}"

# NETWORKS_DIR = "/home/yongting/research/configs/config2spec-confmask/scenarios/confmask/fattree04-ospf"
networks = glob.glob(NETWORKS_DIR + "/*")
networks.remove(f"{NETWORKS_DIR}/origin")
networks.insert(0, f"{NETWORKS_DIR}/origin")
a = None
bf = None
results = []


def get_trace_accepted_count(traces):
    accepted_count = 0
    # print(traces[0])
    if len(traces) == 0:
        return 0
    for t in traces[0]:
        if t.disposition in ["ACCEPTED", "EXITS_NETWORK"]:
            accepted_count += 1
    return accepted_count

def trace_tasks(nw, bf, specs, idx):
    i = 0
    specs_count = len(specs)
    holds_specs = []
    holds_not_specs = []
    global results
    for spec in specs:
        print(f" - Proc {nw}({idx}): {i}/{specs_count}")
        i += 1
        policy_type = spec.split(",")[0]
        src_name = spec.split(",")[3]
        dst_name = spec.split(",")[-2].split(':')[0][1:]
        dst_pfx = spec.split(",")[1]
        result = bf.q.reachability(pathConstraints=PathConstraints(startLocation = f'{src_name}'), headers=HeaderConstraints(dstIps=dst_pfx, srcIps='0.0.0.0/0'), actions='SUCCESS').answer().frame()

        policy_holds = False

        if policy_type == "PolicyType.Waypoint":
            accepted = get_trace_accepted_count(result.Traces)
            if accepted > 0:
                policy_holds = True
            pass

        if policy_type == "PolicyType.LoadBalancingSimple":
            accepted = get_trace_accepted_count(result.Traces)
            if accepted == int(spec.split(",")[2]):
                policy_holds = True
            pass

        if policy_type == "PolicyType.Reachability":
            accepted = get_trace_accepted_count(result.Traces)
            if accepted > 0:
                policy_holds = True
            pass

        if policy_type == "PolicyType.Isolation":
            accepted = get_trace_accepted_count(result.Traces)
            if accepted == 0:
                policy_holds = True
            pass

        if policy_holds:
            # holds_count += 1
            spec = spec.replace("HOLDSNOT", "HOLDS")
            holds_specs.append(spec)
        else:
            # holds_not_count += 1
            if "HOLDSNOT" not in spec:
                spec = spec.replace("HOLDS", "HOLDSNOT")
            print("NotHolds", spec)
            holds_not_specs.append(spec)
    results.append((holds_specs, holds_not_specs))

for nw in networks[1:]:
    nw_name = nw.split("/")[-1]
    print(nw_name)

    bf = Session("127.0.0.1", 10007 + JOB_IDX * 10, 10006 + JOB_IDX * 10) 
    bf.set_network("test")
    bf.init_snapshot(nw, name="test", overwrite=True)

    # verify specs one by one
    if not os.path.exists(nw + "/policies.csv"):
        continue
    with open(nw + "/policies.csv", 'r') as fp:
        nw_specs_content = fp.read().__str__().splitlines()

    # specs_count = 0
    # holds_count = 0
    # holds_not_count = 0
    holds_specs = [nw_specs_content[0]]
    holds_not_specs = [nw_specs_content[0]]
    # specs_count = len(nw_specs_content) - 1

    thread_count = 10
    i = 0
    # divide specs into `thread_count` parts
    ts = []
    for idx in range(0, len(nw_specs_content[1:]), len(nw_specs_content[1:]) // (thread_count + 1)):
        specs = nw_specs_content[1:][idx:idx+len(nw_specs_content[1:]) // (thread_count + 1) - 1]
        # print(len(specs))
        # print(idx,idx+len(nw_specs_content[1:]) // (thread_count + 1) - 1)
        t = threading.Thread(target=trace_tasks, args=(nw_name, bf, specs, i))
        ts.append(t)
        t.start()
        thread_count += 1
        i += 1
    
    for t in ts:
        t.join()


    for task_result in results:
        holds_specs.extend(task_result[0])
        holds_not_specs.extend(task_result[1])
    
    with open(f"{nw}/policies-holds.csv", "w+") as fp:
        fp.write("\n".join(holds_specs))
    with open(f"{nw}/policies-holds-not.csv", "w+") as fp:
        fp.write("\n".join(holds_not_specs))
