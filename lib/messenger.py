import json
import zmq
import threading

class Messenger:
    pub_address="tcp://0.0.0.0:5556" # Own IP ( 10.121.17.84 )
    sub_address="tcp://10.121.17.233:5557" # IP of controller
    receive_topic="stoplichten"

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
        # full_message = f"{topic} {json_message}"
        # print(f"Versturen: {json_message}")
        # self.pub_socket.send_string(full_message)
        self.pub_socket.send_multipart([topic.encode('utf-8'), json_message.encode('utf-8')])

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
                        # Ontvang alle frames van het multipart-bericht
                        frames = self.sub_socket.recv_multipart()
                        if len(frames) >= 2:  # Controleer of er minstens twee frames zijn
                            topic = frames[0].decode('utf-8')  # Eerste frame is het topic
                            message = frames[1].decode('utf-8')  # Tweede frame is de JSON-geformatteerde boodschap           
                            if topic == self.receive_topic:
                                self.received_data = json.loads(message)
                                print(f"Ontvangen: {message}")
                        else:
                            print(f"Onverwacht aantal frames ontvangen: {len(frames)}")
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
