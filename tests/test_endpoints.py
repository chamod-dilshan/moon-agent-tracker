import requests

BASE_URLS = {
    "agent": "http://a08af2d1b44534df4a85d6adb8c31606-1181649550.ap-southeast-2.elb.amazonaws.com",
    "integration": "http://ab10bf16c2a2848bdb418c7b841415e8-1707361465.ap-southeast-2.elb.amazonaws.com",
    "notification": "http://a7e041e4dbf364de7bdcc75799ae3815-35664068.ap-southeast-2.elb.amazonaws.com",
    "aggregator": "http://a0c40126922ba44219699d13ba3ef9ab-496998035.ap-southeast-2.elb.amazonaws.com"
}

ENDPOINTS = {
    "agent": "/agents",
    "integration": "/sales",
    "notification": "/notifications",
    "aggregator": "/"
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