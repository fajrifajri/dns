import socketserver
import socket
from dnslib import *

# DNS Server Info
IP = "0.0.0.0"
PORT = 53
suffix = "123.pg.io"



class UDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
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
    str_qname = str(dns_qname) + suffix

    addr = socket.gethostbyname(str_qname)
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