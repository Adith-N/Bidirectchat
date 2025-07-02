[BIDIRECT-CHAT]
This python program allows user to connect to another device over shared LAN or VPN Pseudonetwork
User can input IP Address of peer to establish comms between devices - One device acts as client and other as server

🔒Client <->=======================<-> Server🔐 (port: ip) {6000: 127.0.0.1}

ServerA<-------ClientB
ClientA------->ServerB
{Comms work by establishing client and server on both devices}

TCP/IP  -  Transmission control protocol is the protocol used for communications in this project
modules - socket, threading, os
