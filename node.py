class SimpleNode:
    def __init__(self, node_id):
        self.node_id = node_id
        self.data = {}
        self.active = True
        self.role = 'follower'
        self.term = 0
        self.voted_for = None

    def store(self, key, value):
        if self.active:
            self.data[key] = value
        else:
            print(f"Node {self.node_id} is inactive. Cannot store key '{key}'.")

    def get(self, key):
        if self.active and key in self.data:
            return self.data[key]
        else:
            if not self.active:
                print(f"Node {self.node_id} is inactive. Cannot retrieve key '{key}'.")
            elif key not in self.data:
                print(f"Key '{key}' not found in node {self.node_id}.")
        return None

    def fail(self):
        self.active = False

    def recover(self):
        self.active = True
        print(f"Node {self.node_id} has recovered.")

