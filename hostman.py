#!/usr/bin/python

import sys
import os
import socket
import ipaddress
import re
import argparse


def add_to_hosts_file(hostname, ip=None):
    # Check if the user has elevated privileges
    if os.geteuid() != 0:
        print("You need to have root privileges to modify the hosts file.")
        sys.exit(1)

    if ip is None:
        try:
            ip = resolve_ip(hostname)
        except socket.gaierror:
            print(f"Error: could not resolve {hostname}")
            sys.exit(1)

    # Validate the IP address
    if ip is not None:
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            print(f"{ip} is not a valid IP address.")
            sys.exit(1)

    # Open the hosts file in read mode
    with open('/etc/hosts', 'r') as f:
        # Read the contents of the file
        content = f.read()

    # Check if the hostname is already in the file
    if hostname in content:
        # Replace the entire line with the new one
        pattern = re.compile(f"^(.*\\s)?{re.escape(hostname)}(\\s.*)?$", re.MULTILINE)
        content = pattern.sub(f"{ip} {hostname}\n", content)
        if ip == "127.0.0.1": ip = "sinkhole"
        print(hostname + " updated to " + str(ip))
    else:
        # Add the new entry to the end of the file
        content += f"{ip} {hostname}\n"
        if ip == "127.0.0.1":
            print(hostname + " added to sinkhole")
        else:
            print(hostname + " added to hosts with IP " + str(ip))

    # Open the hosts file in write mode
    with open('/etc/hosts', 'w') as f:
        # Move the file pointer to the beginning of the file
        f.seek(0)

        # Write the modified content back to the file
        f.write(content)


def remove_from_hosts_file(hostname):
    # Check if the user has elevated privileges
    if os.geteuid() != 0:
        print("You need to have root privileges to modify the hosts file.")
        sys.exit(1)

    try:
        # Open the hosts file in read-write mode
        with open('/etc/hosts', 'r+') as f:
            # Read the contents of the file
            content = f.read()

            # Create a regular expression pattern to match the hostname
            pattern = re.compile(f"^(.*\\s)?{re.escape(hostname)}(\\s.*)?$", re.MULTILINE)

            # Use the pattern to remove the matching line from the file
            content = pattern.sub("", content)

            # Move the file pointer to the beginning of the file
            f.seek(0)

            # Write the modified content back to the file
            f.write(content)

            # Truncate any remaining content (in case the new content is shorter than the old content)
            f.truncate()

            print(hostname + " removed from hosts file.")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


def resolve_ip(hostname):
    import dns.resolver

    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = [name_server]
    resolver.raise_on_no_answer = True

    try:
        answers = resolver.resolve(hostname, "A")
        return answers[0].address
    except:
        print("The hostname {} could not be resolved.".format(hostname))
        sys.exit(1)


if __name__ == '__main__':
    # Define command line arguments
    parser = argparse.ArgumentParser(description='Add or remove a hostname to/from the hosts file. By default, hostnames will be resolved from the Google namesever (8.8.8.8)')
    parser.add_argument('hostname', type=str, help='The hostname to add, update or remove.')
    parser.add_argument('-i', '--ip', type=str, help='To set a specific IP address to associate with the hostname.')
    parser.add_argument('-r', '--remove', action='store_true', help='Remove the specified hostname from the hosts file')
    parser.add_argument('-s', '--sinkhole', action='store_true', help='Add the hostname to a sinkhole; or rather, prevent traffic to the specified hostname. This is great for blocking access for parental control, or for blocking connections to ad servers.')
    parser.add_argument('-n', '--nameserver', type=str, help='To specify a nameserver IP address to use, if the IP is invalid then 8.8.8.8 will be used.')

    # Parse the command line arguments
    args = parser.parse_args()

    # Set the nameserver
    global name_server
    name_server = args.nameserver

    # Declaring the IP variable in case changes are made, such as to
    # add the host to the sinkhole address
    ip = args.ip

    # If adding to sinkhole, set the IP to loopback address
    if args.sinkhole:
        ip = '127.0.0.1'

    # Check to see if a nameserver was passed as an argument.
    # If not, use default. If so, verify it as valid IP format
    if name_server is None:
        name_server = "8.8.8.8"
    else:
        try:
            ipaddress.ip_address(name_server)
        except ValueError:
            print(f"{name_server} is not a valid IP address format.")
            sys.exit(1)

    # Add or remove the hostname from the hosts file
    if args.remove:
        remove_from_hosts_file(args.hostname)
    else:
        add_to_hosts_file(args.hostname, ip)
