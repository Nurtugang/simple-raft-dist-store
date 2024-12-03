import random
import threading
import time

from colorama import Fore, Style

from node import SimpleNode

class RaftDistributedStore:
    def __init__(self, num_nodes=3):
        self.nodes = [SimpleNode(i) for i in range(num_nodes)]
        self.leader = None

        self.display_debug_info_interval = 10
        self.put_delay = random.uniform(0.1, 0.5)
        self.send_heartbeat_interval = 6
        self.failure_probability=0.5
        self.simulate_failure_interval=5

        self.start_background_processes()
        
        # TO ADD. if heartbeat is bad, node that detected this condition, will start election 
        # TO ADD. save logs about history of failures, leaders

    def start_election(self):
        active_nodes = [node for node in self.nodes if node.active]
        candidate_node = random.choice(active_nodes)
        
        if not active_nodes:
            print(f"{Fore.RED}No active nodes available for election. Election cannot proceed.{Style.RESET_ALL}")
            return

        print(f"Node {candidate_node.node_id} is starting an election. (Current term: {candidate_node.term})")
        
        candidate_node.term += 1
        print(f"Node {candidate_node.node_id} updated term to {candidate_node.term}")
        candidate_node.role = 'candidate'
        candidate_node.voted_for = candidate_node.node_id
        votes = 1

        for node in self.nodes:
            if node.active and node.node_id != candidate_node.node_id:
                if node.voted_for is None or node.term < candidate_node.term:
                    votes += 1
                    node.voted_for = candidate_node.node_id
                    node.term = candidate_node.term
                    print(f"Node {node.node_id} votes for Node {candidate_node.node_id}. Updated term: {node.term}")


        if votes > len(active_nodes) // 2:
            candidate_node.role = 'leader'
            self.leader = candidate_node
            print(f"{Fore.GREEN}Node {candidate_node.node_id} becomes the leader with {votes} votes. (Term: {candidate_node.term}){Style.RESET_ALL}")
            self.send_heartbeat()
        else:
            print(f"Node {candidate_node.node_id} failed to become the leader. (Term: {candidate_node.term})")
        
        self.display_debug_info()


    def send_heartbeat(self):
        if self.leader:
            print(f"Leader {self.leader.node_id} is sending heartbeats to followers...")

            def heartbeat_task():
                while True:
                    if self.leader and self.leader.role == 'leader':
                        for node in self.nodes:
                            if node.active and node.node_id != self.leader.node_id:
                                print(f"Node {self.leader.node_id} sends heartbeat to Node {node.node_id}")
                        time.sleep(self.send_heartbeat_interval)
                    else:
                        break

            heartbeat_thread = threading.Thread(target=heartbeat_task, daemon=True)
            heartbeat_thread.start()
        else:
            pass


    def put(self, key, value):
        def put_task():
            time.sleep(self.put_delay)
            if self.leader and self.leader.active:
                self.leader.store(key, value)
                print(f"Stored key '{key}' in leader Node {self.leader.node_id}")

                for node in self.nodes:
                    if node.active and node.node_id != self.leader.node_id:
                        node.store(key, value)

            else:
                print(f"{Fore.RED}No active leader to store the key. Starting a new election.{Style.RESET_ALL}")
                active_nodes = [node for node in self.nodes if node.active]
                if active_nodes:
                    self.start_election()
                else:
                    print(f"{Fore.RED}No active nodes available. Unable to perform election or store the key.{Style.RESET_ALL}")

        put_thread = threading.Thread(target=put_task)
        put_thread.start()



    def fail_node(self, node_id):
        self.nodes[node_id].fail()
        if self.leader and self.leader.node_id == node_id:
            print(f"{Fore.RED}Leader Node {node_id} has failed. Starting a new election.{Style.RESET_ALL}")

            self.leader = None
            for node in self.nodes:
                if node.role == 'leader':
                    node.role = 'follower'

            active_nodes = [node for node in self.nodes if node.active]
            if active_nodes:
                self.start_election()
            else:
                print(f"{Fore.RED}No active nodes available. Cluster is inactive.{Style.RESET_ALL}")


    def recover_node(self, node_id):
        self.nodes[node_id].recover()
    
    def start_background_processes(self):
        def simulate_random_failures():
            while True:
                time.sleep(self.simulate_failure_interval) 
                if random.random() < self.failure_probability: 
                    active_nodes = [node for node in self.nodes if node.active]
                    if active_nodes: 
                        node_to_fail = random.choice(active_nodes)
                        if node_to_fail.active:
                            self.fail_node(node_to_fail.node_id)
                            print(f"\n{Fore.RED}Simulated failure: Node {node_to_fail.node_id} has failed.{Style.RESET_ALL}")
                            self.display_debug_info()

        failure_thread = threading.Thread(target=simulate_random_failures, daemon=True)
        failure_thread.start()


    def display_debug_info(self):
        print("\n=== Debug Info ===")
        print(f"Total nodes: {len(self.nodes)}")
        for node in self.nodes:
            active_status = f"{Fore.GREEN}Active{Style.RESET_ALL}" if node.active else f"{Fore.RED}Inactive{Style.RESET_ALL}"
            role_color = {
                'leader': Fore.BLUE,
                'candidate': Fore.YELLOW,
                'follower': Fore.WHITE,
            }.get(node.role, Fore.WHITE)
            role_status = f"{role_color}{node.role.capitalize()}{Style.RESET_ALL}"

            print(f"Node {node.node_id} | {active_status} | Role: {role_status} | "
                f"Data Count: {Fore.MAGENTA}{len(node.data)}{Style.RESET_ALL} | " 
                f"Term: {Fore.CYAN}{node.term}{Style.RESET_ALL}")
        if self.leader:
            print(f"{Fore.GREEN}Current Leader: Node {self.leader.node_id} (Term: {self.leader.term}){Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}No current leader.{Style.RESET_ALL}")
        print("==================\n")

        time.sleep(self.display_debug_info_interval)
