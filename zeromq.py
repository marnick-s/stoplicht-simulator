import json
import zmq
import time

def start_zeromq_publisher(bind_address="tcp://127.0.0.1:5555"):
    context = zmq.Context()
    socket = context.socket(zmq.PUB)  # Publisher pattern
    socket.bind(bind_address)
    
    print(f"Publisher luistert op {bind_address}")

    while True:
        topic = "stoplichten"  # Topic voor de auto
        message = {
            "61.1": "groen",
            "81.1": "groen",
        }
        json_message = json.dumps(message)
        print(f"Versturen: {topic} {json_message}")
        socket.send_multipart([topic.encode('utf-8'), json_message.encode('utf-8')])
        time.sleep(15)  # Simuleer periodieke berichten
        topic = "stoplichten"  # Topic voor de auto
        message = {
            "61.1": "rood",
            "81.1": "groen",
        }
        json_message = json.dumps(message)
        print(f"Versturen: {topic} {json_message}")
        socket.send_multipart([topic.encode('utf-8'), json_message.encode('utf-8')])
        time.sleep(15)  # Simuleer periodieke berichten

def start_zeromq_subscriber(server_address="tcp://10.121.17.233:5557"):
    context = zmq.Context()
    socket = context.socket(zmq.SUB)  # Subscriber pattern
    socket.connect(server_address)
    socket.setsockopt_string(zmq.SUBSCRIBE, "stoplichten")  # Abonneer op topic "auto"
    
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
