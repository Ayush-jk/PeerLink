# **PeerLink**

**PeerLink** is a secure peer-to-peer (P2P) messaging application that enables real-time communication between users over encrypted SSL connections. The application allows users to register, discover other peers, and exchange messages securely in a decentralized environment.

## **Features**

- **Peer Registration**: Register your peer to be discovered by others in the network.
- **Peer Discovery**: Discover active peers in the network and initiate secure connections.
- **Secure Communication**: Messages are sent over SSL-encrypted channels to ensure privacy and data integrity.
- **Deregistration**: Remove yourself from the network when you disconnect.
- **Real-Time Messaging**: Send and receive messages in real-time, with no reliance on central servers.

## **Technologies Used**

- **Python**: The main programming language used for both server and client implementations.
- **SSL/TLS**: For secure communication between peers.
- **Threading**: To handle multiple client connections concurrently.

## **How It Works**

1. **Server**:
   - Listens for incoming connections from peers.
   - Registers peers, facilitates peer discovery, and allows deregistration.
   - Maintains a registry of active peers with timestamps to manage peer expiration.
   - Provides discovery services by sending a list of active peers when requested.

2. **Client**:
   - Registers itself with the server, making it discoverable to other peers.
   - Discovers active peers by querying the server for the list of available peers.
   - Connects to selected peers and establishes SSL-encrypted communication channels.
   - Allows sending and receiving messages securely over the established peer-to-peer connection.

## **Usage**

1. **Register a Peer**: When you start the client, it automatically registers itself with the server, making it discoverable by other peers.
2. **Discover Peers**: Use the client interface to discover active peers available in the network.
3. **Connect to Peers**: Select a discovered peer to initiate a secure messaging session.
4. **Send Messages**: Once connected, you can send messages in real-time over an encrypted SSL channel.
5. **Deregister**: When you're finished, you can deregister your peer from the server, making it no longer discoverable.

## **Contributing**

Feel free to fork the repository, create branches, and submit pull requests if you have any improvements, bug fixes, or new features. Contributions are welcome!
