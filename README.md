# bilge monitor

Code to monitor bilge pump activity via GPIO Input pin on raspberry Pi

# Circut

I started with this circuit:

![schematic diagram](schematic.png)

which worked for 12.5v but not for 11.5v. putting two R1 resistors
in parallel made the circuit detect the 11.5v condition, need to dial
in the circuit... :-/

# System Dependencies

Your raspberry pi will need a configured mail server listening to
`localhost:25` for this to send notifications.

# Installation

```sh
$ vi monitor_bilge.py # edit CONFIG section
$ sudo install -o root -g root -m 0755 monitor_bilge.py /usr/local/sbin/
$ sudo install -o root -g root -m 0644 monitor_bilge.service /etc/systemd/system/
$ sudo systemctl daemon-reload
$ sudo systemctl enable monitor_bilge.service
$ sudo systemctl start monitor_bilge.service
$ sudo systemctl status monitor_bilge.service
```
