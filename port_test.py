import socket

HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 5000       # Same port you use for Flask

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    print(f"Test server running on {HOST}:{PORT}...")
    print("Waiting for connection...")

    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        conn.sendall(b"Hello! You reached the test server.\n")
