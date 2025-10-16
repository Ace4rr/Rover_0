class Navigator:
    def __init__(self, motors):
        self.motors=motors
    
    def set_route(self, route):
        pass
    
    def get_status(self):
        return {'state': 'idle', 'distance_remaining': 0}
    
    def stop(self):
        pass
    
    def start(self):
        pass