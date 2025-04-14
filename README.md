# **PeerLink**

**PeerLink** is a secure peer-to-peer (P2P) messaging application that enables real-time communication between users over encrypted SSL connections. The application allows users to register, discover other peers, and exchange messages securely in a decentralized environment.

## **Features**

- **Peer Registration**: Register your peer to be discovered by others in the network  
- **Peer Discovery**: Discover active peers in the network and initiate secure connections  
- **Secure Communication**: Messages are sent over SSL-encrypted channels to ensure privacy and data integrity  
- **Deregistration**: Remove yourself from the network when you disconnect  
- **Real-Time Messaging**: Send and receive messages in real-time, with no reliance on central servers

## **Technologies Used**

- **Python**: Main programming language for both server and client  
- **SSL/TLS**: Ensures secure communication between peers  
- **Threading**: Enables concurrent handling of client connections

## **How It Works**

### Server (`server.py`)
- Listens for incoming peer connections  
- Registers peers and maintains a registry with timestamps  
- Handles peer discovery requests by sharing the list of active peers  
- Supports peer deregistration when a client disconnects

### Client (`client.py`)
- Registers itself with the server upon launch  
- Discovers available peers from the server  
- Connects to selected peers using SSL-encrypted channels  
- Enables secure real-time messaging between peers

## **Usage**

1. **Register a Peer**: Launch the client to register with the server  
2. **Discover Peers**: Query the server for active peers  
3. **Connect to Peers**: Select a peer to start a secure session  
4. **Send Messages**: Chat in real-time over an encrypted SSL connection  
5. **Deregister**: Gracefully exit and deregister from the network

## **Security Note**

SSL certificate and key files are not included in this repository. You need to generate your own using tools like OpenSSL.

## **Contributing**

Contributions are welcome. Feel free to fork the repository, create a branch, and open a pull request with any improvements or bug fixes.
