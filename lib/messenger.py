import json
import zmq
import threading

class Messenger:
    pub_address="tcp://0.0.0.0:5555"
    sub_address="tcp://10.6.0.4:5556"
    receive_topic="auto"

    def __init__(self):
        """
        ZeroMQ Messenger voor zowel publisher als subscriber.
        """
        self.context = zmq.Context()
        self.pub_socket = self.context.socket(zmq.PUB)
        self.sub_socket = self.context.socket(zmq.SUB)

        self.pub_socket.bind(self.pub_address)
        self.sub_socket.connect(self.sub_address)
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, self.receive_topic)

        self.running = False
        self.listener_thread = None
        self.received_data = None

    def send(self, topic, message):
        """Verstuurt een bericht met een opgegeven topic."""
        json_message = json.dumps(message)  
        full_message = f"{topic} {json_message}"
        # print(f"Versturen: {full_message}")
        self.pub_socket.send_string(full_message)

    def receive(self):
        """Start met luisteren naar berichten."""
        if self.running:
            print("Listener is al actief!")
            return

        self.running = True
        def listen():
            poller = zmq.Poller()
            poller.register(self.sub_socket, zmq.POLLIN)

            try:
                while self.running:
                    events = dict(poller.poll(timeout=500))
                    if self.sub_socket in events:
                        topic = self.sub_socket.recv_string()
                        message = self.sub_socket.recv_string()
                        if topic == self.receive_topic:
                            self.received_data = json.loads(message)
                            print(f"Ontvangen: {message}")
            except Exception as e:
                print(f"Fout in listener: {e}")
            finally:
                print("Listener gestopt.")

        self.listener_thread = threading.Thread(target=listen, daemon=True)
        self.listener_thread.start()

    def stop(self):
        """Stopt de listener."""
        self.running = False
        if self.listener_thread:
            self.listener_thread.join()
        self.sub_socket.close()
        self.pub_socket.close()
        self.context.term()
