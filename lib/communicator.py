import zmq
import threading

class Communicator:
    pub_address="tcp://0.0.0.0:5555"
    sub_address="tcp://127.0.0.1:5556"
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

    def send(self, topic, message):
        """Verstuurt een bericht met een opgegeven topic."""
        full_message = f"{topic} {message}"
        print(f"Versturen: {full_message}")
        self.pub_socket.send_string(full_message)

    def receive(self, callback):
        """Luistert naar berichten en roept een callback aan per ontvangen bericht."""
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
                        message = self.sub_socket.recv_string()
                        topic, content = message.split(": ", 1)
                        if topic == self.receive_topic:
                            callback(content)
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
