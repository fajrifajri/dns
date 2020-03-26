import socketserver
import socket
from dnslib import *

# DNS Server Info
IP = "0.0.0.0"
PORT = 53

class UDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        # b'{\x99\x01 \x00\x01\x00\x00\x00\x00\x00\x01\x03www\x05fajri\x03net\x00\x00\x01\x00\x01\x00\x00)\x10\x00\x00\x00\x00\x00\x00\x00'
        data = self.request[0].strip()
        socket = self.request[1]
        response = dnsProcessing(data)
        socket.sendto(response, self.client_address)

def dnsProcessing(rawUdpData):
    dnsRequest = DNSRecord.parse(rawUdpData)
    dnsResponse = DNSRecord(
            DNSHeader(
                id=dnsRequest.header.id,
                qr=1,
                aa=1,
                ra=1),
            q=dnsRequest.q
            )
    #dns_qname = str(dnsRequest.q.qname) + suffix
    dns_qname = dnsRequest.q.qname
    dns_qtype = dnsRequest.q.qtype
    list_qname = str(dns_qname).split(".")
    user_id = list_qname[len(list_qname)-4]
    qname = ".".join(list_qname[:-4])
    print(qname)
    print("user id : ",user_id)
    if user_id == "123":
        addr = "1.2.3.4"
    else:
        addr = socket.gethostbyname(qname)

    dnsResponse.add_answer(
                            RR(
                                rname=dns_qname,
                                rtype=dns_qtype,
                                rclass=1,
                                ttl=60,
                                rdata=A(addr)
                            ))
    return(dnsResponse.pack())


if __name__ == '__main__':
    server =socketserver.UDPServer((IP, PORT), UDPHandler)
    server.serve_forever()
