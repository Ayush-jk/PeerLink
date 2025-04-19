# PeerLink

**PeerLink** is a secure peer-to-peer (P2P) messaging application that enables real-time communication between users over encrypted SSL connections. The application allows users to discover peers on the same network and securely exchange messages without relying on a central server.

## Features

- Peer discovery using local network broadcasts  
- Secure SSL/TLS-encrypted real-time messaging  
- Lightweight command-line interface  
- Multithreaded server for concurrent peer connections  
- Clean disconnection and peer session handling  

## Technologies Used

- Python  
- SSL/TLS  
- UDP broadcast and TCP sockets  
- Threading  

## How It Works

Each instance acts as both a server and client. On startup, it broadcasts its presence and listens for other peers. Discovered peers can be connected to securely using SSL, enabling direct, encrypted chat sessions.

## Usage

1. Generate your own `cert.pem` and `key.pem` files (these are not included in the repo).  
2. Run the script to launch your peer.  
3. Use commands like `broadcast`, `list`, and `connect <IP>` to interact with peers.  

## Security Note

SSL certificate and key files are intentionally excluded from the repository. Generate your own using tools like OpenSSL before running the application.

## Contributing

Contributions are welcome. Fork the repo, make your changes, and open a pull request.
