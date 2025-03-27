import requests

# Replace these with your actual LoadBalancer URLs from kubectl get svc
BASE_URLS = {
    "agent": "http://a9fa113adae3f4e8db20b22f76d0dc83-429117789.ap-southeast-2.elb.amazonaws.com",
    "integration": "http://a788f173e0d114dddb3e427af433f58c-1008796998.ap-southeast-2.elb.amazonaws.com",
    "notification": "http://a3f3a89b5ff9b4b58976edeee28b450b-375560315.ap-southeast-2.elb.amazonaws.com",
    "aggregator": "http://a2bced08345be48a78cb4697dffc1f83-496351603.ap-southeast-2.elb.amazonaws.com"
}

ENDPOINTS = {
    "agent": "/agents",
    "integration": "/sales",
    "notification": "/",
    "aggregator": "/aggregate"
}

def test_endpoint(name, base_url, endpoint):
    try:
        url = f"{base_url}{endpoint}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        print(f"{name} service responded with {response.status_code}")
    except Exception as e:
        print(f"{name} service test failed: {e}")
        exit(1)  # exit with error to fail GitHub Actions pipeline

if __name__ == "__main__":
    for service, base_url in BASE_URLS.items():
        test_endpoint(service, base_url, ENDPOINTS[service])