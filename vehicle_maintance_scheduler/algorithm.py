import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logging_middleware import Log

DURATION_KEYS = ("Duration", "duration", "ServiceDuration", "service_duration")
IMPACT_KEYS = ("Impact", "impact", "score", "ImpactScore", "impact_score")
TASK_ID_KEYS = ("TaskID", "task_id", "ID", "id", "VehicleID", "vehicle_id")


class VehicleDataError(ValueError):
    """Raised when vehicle task data is missing required scheduling fields."""


def _find_value(vehicle, keys, field_name):
    for key in keys:
        if key in vehicle:
            return vehicle[key]
    task_id = get_vehicle_task_id(vehicle, default="unknown")
    raise VehicleDataError(f"Vehicle task {task_id} is missing required field: {field_name}")


def _coerce_int(value, field_name, vehicle):
    if isinstance(value, bool):
        task_id = get_vehicle_task_id(vehicle, default="unknown")
        raise VehicleDataError(f"Vehicle task {task_id} has invalid {field_name}: {value!r}")

    try:
        return int(value)
    except (TypeError, ValueError):
        task_id = get_vehicle_task_id(vehicle, default="unknown")
        raise VehicleDataError(f"Vehicle task {task_id} has invalid {field_name}: {value!r}")


def get_vehicle_task_id(vehicle, default=None):
    for key in TASK_ID_KEYS:
        if key in vehicle:
            return vehicle[key]
    if default is not None:
        return default
    raise VehicleDataError("Vehicle task is missing required field: TaskID")


def get_vehicle_duration(vehicle):
    duration = _coerce_int(_find_value(vehicle, DURATION_KEYS, "Duration"), "Duration", vehicle)
    if duration <= 0:
        task_id = get_vehicle_task_id(vehicle, default="unknown")
        raise VehicleDataError(f"Vehicle task {task_id} has invalid Duration: {duration!r}")
    return duration


def get_vehicle_impact(vehicle):
    impact = _coerce_int(_find_value(vehicle, IMPACT_KEYS, "Impact"), "Impact", vehicle)
    if impact < 0:
        task_id = get_vehicle_task_id(vehicle, default="unknown")
        raise VehicleDataError(f"Vehicle task {task_id} has invalid Impact: {impact!r}")
    return impact


def _coerce_budget(budget):
    if isinstance(budget, bool):
        raise VehicleDataError(f"Invalid mechanic-hour budget: {budget!r}")

    try:
        budget = int(budget)
    except (TypeError, ValueError):
        raise VehicleDataError(f"Invalid mechanic-hour budget: {budget!r}")

    if budget < 0:
        raise VehicleDataError(f"Invalid mechanic-hour budget: {budget!r}")

    return budget


def schedule_for_depot(budget, vehicles):
    """
    Solves the 0/1 Knapsack problem for a given budget and list of vehicles.
    Budget: available mechanic hours for the depot.
    Vehicles: list of vehicle dictionaries.
    """
    budget = _coerce_budget(budget)

    vehicles_local = list(vehicles)
    n = len(vehicles_local)
    
    Log("backend", "debug", "domain", f"dp start: budget {budget}h tasks {n}")
    
    start_time = time.time()

    tasks = []
    for vehicle in vehicles_local:
        tasks.append({
            "task_id": get_vehicle_task_id(vehicle),
            "duration": get_vehicle_duration(vehicle),
            "impact": get_vehicle_impact(vehicle),
            "vehicle": vehicle,
        })

    tasks.sort(key=lambda task: str(task["task_id"]))

    dp = [[0] * (budget + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        task = tasks[i - 1]
        duration = task["duration"]
        impact = task["impact"]

        for hours in range(0, budget + 1):
            dp[i][hours] = dp[i - 1][hours]

            if duration <= hours:
                candidate_score = dp[i - 1][hours - duration] + impact
                if candidate_score > dp[i][hours]:
                    dp[i][hours] = candidate_score

    selected_tasks = []
    remaining_hours = budget
    for i in range(n, 0, -1):
        if dp[i][remaining_hours] != dp[i - 1][remaining_hours]:
            task = tasks[i - 1]
            selected_tasks.append(task)
            remaining_hours -= task["duration"]

    selected_tasks.sort(key=lambda task: str(task["task_id"]))
    selected_vehicles = [task["vehicle"] for task in selected_tasks]
    
    time_taken_ms = (time.time() - start_time) * 1000
    
    Log("backend", "info", "domain", f"dp done: {len(selected_vehicles)} tasks impact {dp[n][budget]}")
    Log("backend", "debug", "domain", f"dp time: {time_taken_ms:.2f} ms")
    
    return dp[n][budget], selected_vehicles
