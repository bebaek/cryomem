class Mock():
    """Mock instrument for debugging"""
    def __init__(self):
        self.nw = 0
        self.nr = 0
        print("Mock instrument created.")

    def write(self, msg):
        self.nw += 1
        return msg

    def read(self):
        self.nr += 1
        return str(self.nr + self.nw)

    def query(self, msg):
        self.write(msg)
        return self.read()
