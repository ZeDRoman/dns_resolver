from flask import Flask, request, jsonify
import dns
import dns.name
import dns.query
import time


app = Flask(__name__)

TRACE_DISABLE_CACHE = True


ROOT_SERVER = '193.0.14.129'
CACHE = {}
TTL = {}

def get_dns_row(domain, nameserver, row_type=dns.rdatatype.A):
    query = dns.message.make_query(domain, row_type)
    response = dns.query.udp(query, nameserver)

    rcode = response.rcode()
    if rcode != dns.rcode.NOERROR:
        if rcode == dns.rcode.NXDOMAIN:
            raise Exception('%s does not exist.' % domain)
        else:
            raise Exception('Error %s' % dns.rcode.to_text(rcode))

    done = False
    name = ""
    if len(response.answer) > 0:
        rrset = response.answer[0]
        name = rrset.name.to_text()
        done = True
    elif len(response.additional) > 0:
        rrset = response.additional[0]
        name = response.authority[0].name.to_text()
    else:
        rrset = response.authority[0]
        name = rrset.name.to_text()

    rr = rrset[0]
    if rr.rdtype == dns.rdatatype.A:
        result = rr.to_text()
    elif rr.rdtype == dns.rdatatype.SOA:
        result = nameserver
    elif rr.rdtype == dns.rdatatype.AAAA:
        result = rr.address
    else:
        authority = rr.target
        result = get_authoritative_nameserver(authority.to_text(), trace=False)[0]
    CACHE[name] = result
    TTL[name] = time.time() + rrset.ttl
    return result, done

def find_in_cache(domain, trace):
    for depth in range(domain.count('.')):
        part = '.'.join(domain.split('.')[depth:])
        if (not trace or not TRACE_DISABLE_CACHE) and part in CACHE and time.time() < TTL[part]:
            return CACHE[part], part == domain
    return ROOT_SERVER, False

def get_authoritative_nameserver(domain, trace=False):
    if domain[-1] != '.':
        domain += '.'
    nameserver, last = find_in_cache(domain, trace)
    depth = 0
    trace_path = []
    while not last:
        if trace is not None:
            trace_path.append(nameserver)
        nameserver, last = get_dns_row(domain, nameserver)
        depth += 1
    return nameserver, trace_path


@app.route('/get-a-records', methods=['GET'])
def resolve():
    domain = request.args.get('domain', "")
    trace = request.args.get('trace', "false") == 'true'
    try:
        address, trace_path = get_authoritative_nameserver(domain, trace)
        ans = {"domain": domain,
               "address": address}
        if trace:
            ans["trace"] = trace_path

    except Exception as e:
        ans = {"Exception": str(e)}

    return jsonify(ans)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)