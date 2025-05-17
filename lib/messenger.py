import json
import zmq
import threading
from dotenv import load_dotenv
import os

from lib.enums.topics import Topics

class Messenger:
    load_dotenv()

    pub_address = os.getenv("PUB_ADDRESS", "tcp://127.0.0.1:5556")
    sub_address = os.getenv("SUB_ADDRESS", "tcp://127.0.0.1:5555")
    receive_topic = "stoplichten"

    def __init__(self):
        self.context = zmq.Context()
        self.pub_socket = self.context.socket(zmq.PUB)
        self.sub_socket = self.context.socket(zmq.SUB)

        self.pub_socket.bind(self.pub_address)
        self.sub_socket.connect(self.sub_address)
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, self.receive_topic)

        self.running = False
        self.listener_thread = None
        self.traffic_light_data = None
        self.connected = True

    def send(self, topic, message):
        """Sends a message on the specified topic."""
        # if (topic == Topics.BRIDGE_SENSORS_UPDATE.value):
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
                                self.traffic_light_data = json.loads(message)
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
