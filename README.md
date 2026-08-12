# PeerLink

PeerLink is a secure peer to peer messaging tool. Each instance runs as both server and client, finds other peers on the local network, and exchanges messages over encrypted TLS connections with no central server involved.

## Features

* Automatic peer discovery on the local network using UDP broadcast
* Encrypted real time messaging over SSL/TLS
* Fully bidirectional chat where either side can send at any time
* One thread per connection so several peers can be handled at once
* Length prefixed message framing so messages of any size arrive intact
* Simple command line interface

## Technologies

* Python standard library only
* TCP and UDP sockets
* SSL/TLS
* Threading

## How It Works

On startup each peer periodically broadcasts its presence over UDP and listens for others, building up a list of peers on the same network. Connecting to a peer opens a TLS wrapped TCP session, and a dedicated thread streams incoming messages so both sides can talk at the same time.

## Setup

Generate your own certificate and key inside the project folder. They are not included in the repository.

```
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/CN=peerlink"
```

## Usage

Start a peer.

```
python3 peer.py
```

Available commands

* `list` shows discovered and connected peers
* `connect <ip>` opens an encrypted session and starts chatting
* `chat <ip>` switches to a peer you are already connected to
* `/back` leaves the current chat and returns to the command prompt
* `exit` quits

Discovery runs on its own, so other peers on the same network show up within a few seconds.

## Security

Traffic is encrypted with TLS. Peers are not authenticated, since certificates are self signed and go unverified, so the tool is intended for trusted local networks. Certificate and key files are kept out of the repository on purpose.