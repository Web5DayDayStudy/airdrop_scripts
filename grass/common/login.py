import requests
import json
import logging

logging.basicConfig(level=logging.INFO)


class LoginManager:
    def __init__(self, url='https://api.getgrass.io/auth/login'):
        self.log_url = url
        self.uid = None
        self.username = None
        self.password = None

    def do_login(self, username, password):
        body = {
            "user": username,
            "password": password
        }
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Origin': 'https://app.getgrass.io'
        }
        try:
            login_response = requests.post(self.log_url, data=json.dumps(body), headers=headers)
            login_info = login_response.json()
            logging.info(f"login info: {login_info}")
            if login_response.status_code in [200, 201] and login_info["status"] == "success":
                logging.info("login successful")
                self.username = username
                self.uid = login_info["data"]["id"]
            else:
                logging.error("login failed")
        except requests.RequestException as e:
            logging.error(f"An error occurred while trying to login: {e}")


if __name__ == '__main__':
    login = LoginManager()
    login.do_login('', '')
    print(login.uid)
