import requests
import json
import os
import re
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from cryptography import x509
from pathlib import Path
from urllib.parse import urljoin

edgerc_path = Path(r'C:\Path\To\.edgerc')
edgerc = EdgeRc(str(edgerc_path))
section = 'default' #Section name in your .edgerc file
baseurl = 'https://%s' % edgerc.get(section, 'host')

session = requests.Session()
session.auth = EdgeGridAuth.from_edgerc(edgerc, section)

path = '/cps/v2/enrollments'
headers = {
    "Accept": "application/vnd.akamai.cps.enrollment-status.v1+json",
    "Content-Type": "application/vnd.akamai.cps.enrollment.v12+json"
}


CONTRACT_ID = "XXXXXXX" #Replace with your actual contract ID





queryString = {
    "contractId": CONTRACT_ID,
    "accountSwitchKey": "XXXXXX" # Replace with your actual switch key
    # "deploy-not-before": "2026-06-20T00:00:00Z",
    # "deploy-not-after": "2026-12-31T23:59:59Z",
}


def parse_plaintext_api_error(message):
    pattern = r"ApiError\(type=(.*?),\s*title=(.*?),\s*detail=(.*?),\s*source=(.*?)\)$"
    match = re.search(pattern, message.strip())
    if not match:
        return None
    return {
        "type": match.group(1).strip(),
        "title": match.group(2).strip(),
        "detail": match.group(3).strip(),
        "source": match.group(4).strip(),
    }


enrollment_data = {
   
    "certificateType": "third-party", #Choose either san, single, wildcard, wildcard-san, or third-party
    "changeManagement": True, #Choose from True or False.If set to True, stops CPS from automatically deploying the certificate to the production edge network. 
    "enableMultiStackedCertificates": False, #Enable Dual-Stacked certificate deployment for this enrollment. The next renewal includes the change. Note that this value is only returned for third-party certificates. Otherwise it's omitted from the response.
    "ra": "third-party", #The registration authority or certificate authority (CA) you want to use to obtain a certificate. A CA is a trusted entity that signs certificates and can vouch for the identity of a website. This is either symantec, lets-encrypt, or third-party.
    "validationType": "third-party",  #CPS supports several types of validation: dv, ev, ov, or third-party
    "thirdParty": { #Specifies that you want to use a third party certificate. This is any certificate that is not issued through CPS.
        "excludeSans": False #If this is true, then the SANs in the enrollment don't appear in the CSR that CPS submits to the CA.
    },
    
    "csr": {
        "cn": "test1.example.com",
        "c": "GB",
        "st": "Hamilton",
        "l": "London",
         "o": "TEST",
        "sans": [
            "test2.example.com"
         ]
    },
    
   
    "signatureAlgorithm": "SHA-256",
    
   
    "certificateChainType": "default",

    "networkConfiguration": {
        "geography": "core",
        "secureNetwork": "enhanced-tls",
        "sniOnly": True,         
        "quicEnabled": False,
        "dnsNameSettings": {     
            "cloneDnsNames": False,
            "dnsNames": [
                "test1.example.com",
                "test2.example.com"
            ]
        }
    },
    
  
    "adminContact": {
        "firstName": "XXXXXX",
        "lastName": "XXXX",
        "title": "XXXXXXX",
        "email": "XXXX@XXXX.com",
        "phone": "XXXXXXX",
        "addressLineOne": "XXXXXX",
        "addressLineTwo": "XXXXXX",
        "organizationName": "XXXXXX",
         "city": "XXXXX",
        "region": "XXX",
         "postalCode": "XXXX",
         "country": "XX"
    },
    
  
    "techContact": {
        "firstName": "XXXXX",
        "lastName": "XXXXX",
        "email": "XXXXXX",
        "phone": "XXXXXX",
         "addressLineOne": "XXXXXXX",
        "city": "XXXXX",
         "region": "XX",
         "postalCode": "XXXXX",
         "country": "XX"
    },
    
   
    "org": {
        "name": "XXXXx",
        "addressLineOne": "XXXXX",
        "country": "XX",
        "city": "XXXX",
        "region": "XXXX",
        "phone": "XXXXX",
        "postalCode": "XXXXX",

    },
    
    # "assignedSlots": [1, 2, 3],
    
 
    # "deploymentSchedule": {
    #     "notBefore": "2026-06-20T00:00:00Z",
    #     "notAfter": "2026-12-31T23:59:59Z"
    # }
}

result = session.post(urljoin(baseurl, path), headers=headers, params=queryString, json=enrollment_data, verify=True)
print("=" * 70)
print("CREATE ENROLLMENT RESPONSE")
print("=" * 70)
print(f"  STATUS: {result.status_code}")
print("=" * 70)
if result.status_code in [200, 201, 202]:
    response = result.json()
    print(json.dumps(response, indent=2))
    print("=" * 70)
    print("Details:")
    if 'enrollment' in response:
        print(f"  Enrollment ID: {response['enrollment']}")
    if 'changes' in response:
        print(f"  Changes: {response['changes']}")
else:
    try:
        error = result.json()
        print(f"  ERROR : {error.get('title', 'Unknown error')}")
        print(f"  DETAIL: {error.get('detail', '')}")
        print(f"  TYPE  : {error.get('type', '')}")
    except Exception:
        parsed_error = parse_plaintext_api_error(result.text)
        if parsed_error:
            print(f"  ERROR : {parsed_error['title']}")
            print(f"  DETAIL: {parsed_error['detail']}")
            print(f"  TYPE  : {parsed_error['type']}")
            print(f"  SOURCE: {parsed_error['source']}")
            if parsed_error['title'].lower() == "invalid contract":
                print("  HINT  : Set AKAMAI_CONTRACT_ID to a contract available to this API client.")
                print("  HINT  : If needed, set AKAMAI_ACCOUNT_SWITCH_KEY for the target account context.")
        else:
            print("  ERROR : Non-JSON error response")
            print(f"  DETAIL: {result.text[:1000]}")
print("=" * 70) 