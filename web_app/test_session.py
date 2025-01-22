# File 1: test_session.py
import time
import json
from threading import Thread, Lock
from datetime import datetime

class TestSession:
    _lock = Lock()
    _current_session = None
    
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.start_time = datetime.now()
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_latency': 0,
            'requests_per_second': 0,
            'latency_history': [],
            'throughput_history': []
        }
        self._stop = False
        self.responses = []
        
    @classmethod
    def get_current_session(cls):
        with cls._lock:
            return cls._current_session
        
    @classmethod
    def start_session(cls, name, config):
        with cls._lock:
            if cls._current_session is not None:
                return False
            cls._current_session = cls(name, config)
            thread = Thread(target=cls._current_session.run)
            thread.start()
            return True
            
    @classmethod
    def stop_session(cls):
        with cls._lock:
            if cls._current_session:
                cls._current_session._stop = True
                cls._current_session = None
                return True
            return False
            
    def run(self):
        # Implement your actual load test logic here
        # This is a simulated version
        start = time.time()
        while not self._stop and (time.time() - start) < self.config.get('duration', 60):
            # Simulate metrics update
            self.metrics['total_requests'] += 10
            self.metrics['successful_requests'] += 9
            self.metrics['failed_requests'] += 1
            self.metrics['average_latency'] = (self.metrics['average_latency'] + 0.1) % 2
            self.metrics['requests_per_second'] = self.metrics['total_requests'] / (time.time() - start)
            
            self.metrics['latency_history'].append(self.metrics['average_latency'])
            self.metrics['throughput_history'].append(self.metrics['requests_per_second'])
            
            time.sleep(1)  # Simulate work
        
        self.save()
        TestSession._current_session = None
        
    def get_state(self):
        return {
            'name': self.name,
            'running': not self._stop,
            'duration': time.time() - self.start_time.timestamp(),
            'metrics': self.metrics
        }
        
    def save(self):
        data = {
            'name': self.name,
            'config': self.config,
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'metrics': self.metrics,
            'responses': self.responses
        }
        with open(f'sessions/{self.name}.json', 'w') as f:
            json.dump(data, f)