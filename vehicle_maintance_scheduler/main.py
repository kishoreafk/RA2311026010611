import os
import json
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logging_middleware import Log

try:
    from .api import fetch_scheduler_data, get_auth_token
    from .algorithm import (
        VehicleDataError,
        get_vehicle_duration,
        get_vehicle_impact,
        get_vehicle_task_id,
        schedule_for_depot,
    )
except ImportError:
    from api import fetch_scheduler_data, get_auth_token
    from algorithm import (
        VehicleDataError,
        get_vehicle_duration,
        get_vehicle_impact,
        get_vehicle_task_id,
        schedule_for_depot,
    )


def _get_depot_id(depot):
    return int(depot.get('ID', depot.get('id', depot.get('DepotID'))))


def _get_depot_budget(depot):
    return int(depot.get('MechanicHours', depot.get('mechanic_hours', depot.get('MechanicHoursBudget'))))

def main():
    token = os.environ.get("AUTH_TOKEN")
    
    if not token:
        try:
            token = get_auth_token()
            os.environ["AUTH_TOKEN"] = token
            Log("backend", "info", "controller", "run init: remote logger ready")
        except Exception as e:
            print(json.dumps({"error": f"Error authenticating: {e}"}))
            return
    else:
        os.environ["AUTH_TOKEN"] = token
        Log("backend", "info", "controller", "run init: existing auth token")
            
    try:
        depots_data, vehicles_data = fetch_scheduler_data(token)
    except Exception as e:
        Log("backend", "fatal", "controller", f"core fetch failed: {e}")
        print(json.dumps({"error": f"Error fetching data: {e}"}))
        return

    depots = depots_data.get('depots', [])
    vehicles = vehicles_data.get('vehicles', [])

    if not isinstance(depots, list) or not isinstance(vehicles, list):
        Log("backend", "error", "controller", "api shape invalid: lists expected")
        print(json.dumps({"error": "Invalid API response shape: depots and vehicles must be lists."}))
        return

    results = []

    try:
        depots = sorted(depots, key=_get_depot_id)
    except (TypeError, ValueError) as e:
        Log("backend", "error", "controller", f"bad depot data: {e}")
        print(json.dumps({"error": f"Invalid depot data received from API: {e}"}))
        return

    Log("backend", "info", "controller", f"run start: {len(depots)} depots {len(vehicles)} vehicles")

    for depot in depots:
        try:
            depot_id = _get_depot_id(depot)
            budget = _get_depot_budget(depot)
        except (TypeError, ValueError) as e:
            Log("backend", "error", "controller", f"bad depot data: {e}")
            print(json.dumps({"error": f"Invalid depot data received from API: {e}"}))
            return
        
        Log("backend", "debug", "controller", f"depot {depot_id}: budget {budget}h")
        
        try:
            max_score, selected = schedule_for_depot(budget, vehicles)
            used_hours = sum(get_vehicle_duration(v) for v in selected)
            total_impact = sum(get_vehicle_impact(v) for v in selected)
            selected_tasks = [get_vehicle_task_id(v) for v in selected]
        except VehicleDataError as e:
            Log("backend", "error", "controller", f"bad vehicle data: {e}")
            print(json.dumps({"error": f"Invalid vehicle task data received from API: {e}"}))
            return

        remaining_hours = budget - used_hours
        Log(
            "backend",
            "info",
            "controller",
            f"depot {depot_id}: {len(selected_tasks)} tasks {used_hours}/{budget}h impact {max_score}",
        )
        if total_impact != max_score:
            Log(
                "backend",
                "warn",
                "controller",
                f"depot {depot_id}: impact mismatch {total_impact}!={max_score}",
            )
        if remaining_hours > 0:
            Log("backend", "debug", "controller", f"depot {depot_id}: unused {remaining_hours}h")
        
        results.append({
            "depot_id": depot_id,
            "budget": budget,
            "used_hours": used_hours,
            "max_impact": max_score,
            "selected_count": len(selected_tasks),
            "selected_tasks": selected_tasks
        })

    output = {
        "results": results
    }
    
    Log("backend", "info", "controller", "run done: schedules computed")
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
