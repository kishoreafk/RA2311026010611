import os
import json
import requests
import sys
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logging_middleware import Log

DEPOTS_URL = "http://20.207.122.201/evaluation-service/depots"
VEHICLES_URL = "http://20.207.122.201/evaluation-service/vehicles"
CACHE_FILE = Path(__file__).with_name(".scheduler_data_cache.json")
EXPECTED_DEPOT_IDS = {1, 2, 3, 4, 5}

def get_auth_token():
    url = "http://20.207.122.201/evaluation-service/auth"
    payload = {
        "email": "ks8812@srmist.edu.in",
        "name": "Kishore S",
        "rollNo": "RA2311026010611",
        "accessCode": "QkbpxH",
        "clientID": "bfebbdae-8259-43c7-8fc0-405d863efddb",
        "clientSecret": "eJhGAGHPexMnHqKT"
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        token = response.json().get("access_token")
        if not token:
            raise ValueError("Authentication response did not include an access_token")
        os.environ["AUTH_TOKEN"] = token
        Log("backend", "info", "auth", "auth ok: token issued")
        return token
    except Exception as e:
        raise e

def fetch_data(url, token):
    """Fetches JSON data from the provided URL using the Bearer token."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        first_value = next(iter(data.values()), [])
        record_count = len(first_value) if isinstance(first_value, list) else 0
        resource = "depots" if url == DEPOTS_URL else "vehicles"
        Log("backend", "info", "service", f"GET {resource} ok: {record_count} records")
        return data
    except Exception as e:
        resource = "depots" if url == DEPOTS_URL else "vehicles"
        Log("backend", "error", "service", f"GET {resource} failed: {str(e)}")
        raise e


def _cache_enabled():
    return os.environ.get("SCHEDULER_DISABLE_CACHE", "").lower() not in {"1", "true", "yes"}


def _refresh_requested():
    return os.environ.get("SCHEDULER_REFRESH_DATA", "").lower() in {"1", "true", "yes"}


def _depot_ids(depots_data):
    depots = depots_data.get("depots", []) if isinstance(depots_data, dict) else []
    ids = set()
    for depot in depots:
        try:
            ids.add(int(depot.get("ID")))
        except (AttributeError, TypeError, ValueError):
            continue
    return ids


def _has_complete_depot_set(depots_data):
    return _depot_ids(depots_data) == EXPECTED_DEPOT_IDS


def _fetch_attempt_count():
    try:
        return max(1, int(os.environ.get("SCHEDULER_FETCH_ATTEMPTS", "10")))
    except ValueError:
        return 10


def load_cached_scheduler_data():
    if not _cache_enabled() or _refresh_requested() or not CACHE_FILE.exists():
        return None

    try:
        with CACHE_FILE.open("r", encoding="utf-8") as cache_file:
            data = json.load(cache_file)
    except (OSError, json.JSONDecodeError) as e:
        Log("backend", "warn", "cache", f"cache unreadable: {e}")
        return None

    if not isinstance(data, dict) or "depots" not in data or "vehicles" not in data:
        Log("backend", "warn", "cache", "cache invalid shape")
        return None

    if not _has_complete_depot_set(data["depots"]):
        Log("backend", "warn", "cache", "cache incomplete: need depots 1-5")
        return None

    Log("backend", "info", "cache", "cache hit: scheduler snapshot")
    return data["depots"], data["vehicles"]


def save_scheduler_data_cache(depots_data, vehicles_data):
    if not _cache_enabled():
        return

    payload = {
        "depots": depots_data,
        "vehicles": vehicles_data,
    }

    try:
        with CACHE_FILE.open("w", encoding="utf-8") as cache_file:
            json.dump(payload, cache_file, indent=2, sort_keys=True)
    except OSError as e:
        Log("backend", "warn", "cache", f"cache save failed: {e}")
        return

    Log("backend", "info", "cache", "cache saved: scheduler snapshot")


def fetch_scheduler_data(token):
    cached_data = load_cached_scheduler_data()
    if cached_data is not None:
        return cached_data

    last_depots_data = None
    last_vehicles_data = None

    for attempt in range(1, _fetch_attempt_count() + 1):
        Log("backend", "info", "service", f"fetch attempt {attempt}: depots vehicles")
        depots_data = fetch_data(DEPOTS_URL, token)
        vehicles_data = fetch_data(VEHICLES_URL, token)

        last_depots_data = depots_data
        last_vehicles_data = vehicles_data

        if _has_complete_depot_set(depots_data):
            save_scheduler_data_cache(depots_data, vehicles_data)
            return depots_data, vehicles_data

        found_ids = sorted(_depot_ids(depots_data))
        Log("backend", "warn", "service", f"depots incomplete: ids {found_ids}")

    Log("backend", "warn", "service", "using latest incomplete depot snapshot")
    save_scheduler_data_cache(last_depots_data, last_vehicles_data)
    return last_depots_data, last_vehicles_data
