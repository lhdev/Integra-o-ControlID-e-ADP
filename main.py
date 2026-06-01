import os
import json
import requests
from dotenv import load_dotenv
import re


load_dotenv()

CONTROLID_URL = os.getenv("CONTROLID_URL")
CONTROLID_USER = os.getenv("CONTROLID_USER")
CONTROLID_PASSWORD = os.getenv("CONTROLID_PASSWORD")


def login_controlid():
    url = f"{CONTROLID_URL}/login.fcgi"

    payload = {
        "login": CONTROLID_USER,
        "password": CONTROLID_PASSWORD
    }

    response = requests.post(url, json=payload, timeout=15)
    response.raise_for_status()

    return response.json()["session"]


def get_users(session):
    url = f"{CONTROLID_URL}/load_objects.fcgi?session={session}"

    payload = {
        "object": "users",
        "fields": [
            "id",
            "name",
            "registration"
        ]
    }

    response = requests.post(url, json=payload, timeout=15)
    response.raise_for_status()

    users = response.json().get("users", [])

    # cria dicionário por id
    users_map = {}

    for user in users:
        user_id = str(user.get("id"))

        users_map[user_id] = {
            "id": user.get("id"),
            "name": user.get("name"),
            "registration": user.get("registration")
        }

    return users_map


def get_afd(session):
    url = f"{CONTROLID_URL}/export_afd.fcgi?session={session}&mode=671"

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    return response.text.splitlines()


def parse_afd_line(line):
    """
    Exemplo:
    0000000232025-12-03T14:52:00+0000000000000000152C2
    """

    if len(line) < 40:
        return None

    try:
        nsr = int(line[0:9])

        timestamp = line[9:28]

        employee_raw = line[28:-3]

        employee_id = str(int(employee_raw))

        crc = line[-3:]

        return {
            "nsr": nsr,
            "timestamp": timestamp,
            "employee_id": employee_id,
            "crc": crc
        }

    except:
        return None


def main():

    print("Fazendo login...")

    session = login_controlid()

    print("Login OK")

    print("Carregando usuários...")

    users = get_users(session)

    print(f"Usuários encontrados: {len(users)}")

    print("Lendo AFD...")

    lines = get_afd(session)

    punches = []

    for line in lines:

        punch = parse_afd_line(line)

        if not punch:
            continue

        employee = users.get(punch["employee_id"])

        punches.append({
            "nsr": punch["nsr"],
            "timestamp": punch["timestamp"],
            "employee": employee
        })

    print(json.dumps(punches, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()