import zmq
import time

def start_zeromq_publisher(bind_address="tcp://127.0.0.1:5556"):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)  # Publisher pattern
    socket.bind(bind_address)
    
    print(f"Publisher luistert op {bind_address}")

    while True:
        message = "auto: Een auto is gedetecteerd!"
        print(f"Versturen: {message}")
        socket.send_string(message)
        time.sleep(1)  # Simuleer periodieke berichten

def start_zeromq_subscriber(server_address="tcp://127.0.0.1:5556"):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)  # Subscriber pattern
    socket.connect(server_address)
    socket.setsockopt_string(zmq.SUBSCRIBE, "auto")  # Abonneer op topic "auto"
    
    print(f"Verbonden met publisher op {server_address}, wacht op berichten...")
    
    while True:
        message = socket.recv_string()
        print(f"Ontvangen: {message}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        start_zeromq_publisher()
    else:
        start_zeromq_subscriber()
