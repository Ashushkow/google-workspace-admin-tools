#!/usr/bin/env python3
import requests

def check_myteam_api():
    base_url = 'https://sputnik8.ismyteam.ru'
    endpoints = ['/api/v1/', '/api/v2/', '/api/users', '/api/users/', '/docs/', '/swagger/', '/openapi.json']
    
    for endpoint in endpoints:
        try:
            response = requests.get(base_url + endpoint, timeout=5)
            print(f'{endpoint}: {response.status_code}')
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', 'unknown')
                print(f'  Content-Type: {content_type}')
                if 'json' in content_type:
                    try:
                        json_data = response.json()
                        if isinstance(json_data, dict):
                            print(f'  JSON keys: {list(json_data.keys())}')
                        else:
                            print(f'  JSON type: {type(json_data)}')
                    except:
                        print('  JSON parsing failed')
        except Exception as e:
            print(f'{endpoint}: Error - {str(e)[:50]}')

if __name__ == '__main__':
    check_myteam_api()