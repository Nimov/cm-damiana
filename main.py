import json
import requests
from datetime import datetime
import time
import os

time_between_requests = 30


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Load config file
    with open('config.json') as file:
        config = json.load(file)

    # Login
    while True:
        url = 'https://patientportal-login-cmd.damian.pl/connect/token'
        data = {
            'client_id': 'pp',
            'grant_type': 'password-realm',
            'realm': 'cis',
            'username': config['username'],
            'password': config['password'],
            'device_code': '03942ae1-bad0-4a77-becb-67196b128331',
            'method': 'full_access'
        }
        resp = requests.post(url, data=data)
        if resp.status_code != 200:
            print(resp)

        # Impersonation
        url = 'https://patientportal-login-cmd.damian.pl/connect/token'
        data = {
            'client_id': 'pp',
            'grant_type': 'impersonation',
            'token': resp.json()['access_token'],
            'mrn': '1234935'
        }
        resp = requests.post(url, data=data)
        if resp.status_code != 200:
            print(resp)

        # Prepare header to get appointments
        auth_token = f"Bearer {resp.json()['access_token']}"
        expires_in = resp.json()['expires_in']
        repeats = int((expires_in - time_between_requests) / time_between_requests)
        headers = {"authorization": auth_token, "host": "patientportal-api-gateway-cmd.damian.pl"}

        for repeat in range(repeats):
            url_get = 'https://patientportal-api-gateway-cmd.damian.pl/appointments/api/search-appointments'\
                      '/slots?Page=1&PageSize=5000&RegionIds=102100&SpecialtyIds=28514&StartTime=2024-03-11'
            resp = requests.get(url_get, headers=headers)
            if resp.status_code != 200:
                print(resp)

            appointments = resp.json()['items']
            appointments = [app for app in appointments if datetime.strptime(app['appointmentDate'], '%Y-%m-%dT%H:%M:%S').date() == datetime.today().date()]
            os.system("clear")
            print(f"Internista NFZ (today, last checked: {datetime.now()}):")
            for appointment in appointments:
                print("........")
                print(f"Date: {appointment['appointmentDate']}")
                print(f"Clinic: {appointment['clinic']['name']}")
                print(f"Doctor: {appointment['doctor']['name']}")
            time.sleep(time_between_requests)



