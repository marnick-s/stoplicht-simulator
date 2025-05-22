import json
import zmq
import threading
import yaml
import os
from lib.enums.topics import Topics

class Messenger:
    def __init__(self):
        self._load_config()
        
        self.context = zmq.Context()
        self.pub_socket = self.context.socket(zmq.PUB)
        self.sub_socket = self.context.socket(zmq.SUB)
        self.pub_socket.bind(f"tcp://{self.pub_address}:5556")
        self.sub_socket.connect(f"tcp://{self.sub_address}:5555")
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, self.receive_topic)
        self.running = False
        self.listener_thread = None
        self.traffic_light_data = None
        self.connected = True

    def _load_config(self):
        """Load configuration from YAML file"""
        config_path = "./ip-config.yaml"
        
        # Default values
        default_config = {
            'pub_address': '127.0.0.1',
            'sub_address': '127.0.0.1'
        }

        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as file:
                    config = yaml.safe_load(file)
                    if config is None:
                        config = {}
            else:
                print(f"Config file {config_path} not found, using defaults")
                config = {}
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file: {e}, using defaults")
            config = {}
        except Exception as e:
            print(f"Error loading config file: {e}, using defaults")
            config = {}
        
        # Set configuration with fallback to defaults
        self.pub_address = config.get('pub_address', default_config['pub_address'])
        self.sub_address = config.get('sub_address', default_config['sub_address'])
        print(f"Publisher address: {self.pub_address}")
        print(f"Subscriber address: {self.sub_address}")
        self.receive_topic = "stoplichten"

    def send(self, topic, message):
        """Sends a message on the specified topic."""
        # if (topic == Topics.PRIORITY_VEHICLE.value):
        #     print(message)
        json_message = json.dumps(message)
        self.pub_socket.send_multipart([topic.encode('utf-8'), json_message.encode('utf-8')])

    def receive(self):
        """Start listening to messages."""
        if self.running:
            print("Listener is al actief!")
            return
        
        self.running = True
        
        def listen():
            poller = zmq.Poller()
            poller.register(self.sub_socket, zmq.POLLIN)
            
            try:
                while self.running:
                    # Poll every 50ms for incoming messages
                    events = dict(poller.poll(timeout=50))
                    if self.sub_socket in events:
                        try:
                            # Use non-blocking receive
                            frames = self.sub_socket.recv_multipart(flags=zmq.NOBLOCK)
                        except zmq.Again:
                            continue  # No message, continue polling
                       
                        if len(frames) >= 2:
                            topic = frames[0].decode('utf-8')
                            message = frames[1].decode('utf-8')
                           
                            if topic == self.receive_topic:
                                # print(f"Ontvangen bericht op topic '{topic}': {message}")
                               
                                # Add validation before parsing JSON
                                try:
                                    # Check if message starts with { to detect potential JSON
                                    if message.strip().startswith('{'):
                                        self.traffic_light_data = json.loads(message)
                                    else:
                                        print(f"Geen geldige JSON ontvangen: {message}")
                                except json.JSONDecodeError as json_err:
                                    print(f"JSON parsing fout: {json_err}")
                        else:
                            print(f"Onverwacht aantal frames ontvangen: {len(frames)}")
            except Exception as e:
                print(f"Fout in listener: {e}")
            finally:
                print("Listener gestopt.")
        
        self.listener_thread = threading.Thread(target=listen, daemon=True)
        self.listener_thread.start()

    def stop(self):
        """Stops the listener."""
        self.running = False
        if self.listener_thread:
            self.listener_thread.join()
        self.sub_socket.close()
        self.pub_socket.close()
        self.context.term()