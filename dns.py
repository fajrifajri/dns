import socketserver
from dnslib import *

# DNS Server Info
IP = "0.0.0.0"
PORT = 53
config_dir = "dns_config/"
GLOBAL_TTL = 30

soa_record = SOA( 
        mname="ns1.fajri.net",
        rname="fajri.fajri.net",
        times=(
            300510730,   # serial
            900,   # refresh
            900,     # retry
            1800,   # expire
            60     # min_ttl
       )) 

ns_records = [ 
        NS("ns1.fajri.net"),
        NS("ns1.fajri.io")
       ] 

class UDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        response = dnsResponse(data)
        socket.sendto(response, self.client_address)

def dnsResponse(rawUdpData):
    dnsRequest = DNSRecord.parse(rawUdpData)
    #print(dnsRequest)

    #defining DNS request
    dns_qname = dnsRequest.q.qname
    dns_qtype = dnsRequest.q.qtype

    dns_config_file = config_dir + QTYPE[dns_qtype] + "/" + str(dns_qname)[:-1]

    # constracting DNS Reponse only if the config file exists
    if(dns_config_file):
        #DNS Header
        dnsResponse = DNSRecord(
            DNSHeader(
                id=dnsRequest.header.id,
                qr=1,
                aa=1,
                ra=1),
            q=dnsRequest.q
            )
        #print(dnsResponse)

        # Response Data based on config file
        with open(dns_config_file) as config:
            for a_config in config:
                line_config = a_config.split(",")
                TTL = int(line_config[0])
                RDATA = line_config[1]

                # A response
                if dns_qtype==1:
                    dnsResponse.add_answer(
                            RR(
                                rname=dns_qname, 
                                rtype=dns_qtype, 
                                rclass=1, 
                                ttl=TTL, 
                                rdata=A(RDATA)
                            ))

        # NS Record
        for rdata in ns_records:
            dnsResponse.add_ar(
                RR(
                    rname=dns_qname, 
                    rtype=QTYPE.NS, 
                    rclass=1, 
                    ttl=GLOBAL_TTL, 
                    rdata=rdata
                ))
        
        #print(dnsResponse)
        #SOA record
        dnsResponse.add_auth(RR(
            rname=dns_qname, 
            rtype=QTYPE.SOA, 
            rclass=1, 
            ttl=GLOBAL_TTL, 
            rdata=soa_record
            ))

        print(dnsResponse)
        return(dnsResponse.pack())



if __name__ == '__main__':
    server =socketserver.UDPServer((IP, PORT), UDPHandler)
    server.serve_forever()