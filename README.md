# Hostman
I've always felt like the hosts file was a neglected gem in networking. I'm sure many people have used it, but what about using it to its full potential? For but one example, it can be used as a DNS sinkhole. If there are hosts or domains that you would rather not connect to, redirect traffic to your loopback address.
    $ python3 hostman.py -s www.adserver.ads

To bypass DNS resolution over the network, you can store an IP address in the hosts file for a slightly faster initial connection. Note that, should the IP address change, you will have connection issues to that host.
     $ python3 hostman.py www.google.com

Another use is a convenient way to name other end-points on a network.
     $ python3 hostman.py -i 192.168.0.12 janeslaptop
     
I recommend changing the filename of hostman.py to 'hostman', adding it to your binary path such as /usr/bin and executing it like so:
    $ hostman www.google.com
