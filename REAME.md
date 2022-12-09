# MITM Attack using ARP poisoning

## Components
- Host
- Gateway
- Attacker
- Broadcast

### Overview 
The purpose of this project is to demonstrate the process and details of how the ARP protocal works and the steps attackers can take to 
hijack a person's connection. <br>
**The Host script** represents the victim. It is capable of sending and receiving ARP packets, and keeps an
ARP table for entries. <br>
**The Gateway script** has the same functionality as the host and serves to send a simple request back when a 
connetion is made.
**The Attack script** responds to ARP requests not meant for it to overwrite entries in the victims ARP tables and hijack their connections
<br> **The Broadcast Script** is a simple switch that serves the purpose of a broadcast address for these sockets. It is used 
for sending out ARP requests.

### Execution
The attack script should be run, then the broadcast, host, and gateway. When the host receives a connetion from a web browser, it will
try to find the default gateway though an ARP request, but the attacker should provide its information. The gateway also get hijacked
trying to find the host. This way the attacker will sit between the two and forward packets while seeing everything. The web browser
will reveal if the packet was changed by the attacker.
