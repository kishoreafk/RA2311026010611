# Vehicle Maintenance Scheduler

A Python microservice that optimizes vehicle maintenance scheduling for logistics company depots using dynamic programming to maximize operational impact within mechanic-hour constraints.

## Overview

This project addresses the challenge of selecting which vehicle maintenance tasks to complete when mechanic-hours are limited. Each vehicle has an operational impact score and service duration, and the goal is to maximize total impact while staying within budget.

The solution implements a 0/1 Knapsack algorithm to efficiently solve this optimization problem for real-world scale inputs.

## Features

- **API Integration**: Fetches depot and vehicle data from protected APIs
- **Authentication**: Automatic token management for API access
- **Caching**: Local caching of API responses to reduce network calls
- **Logging Middleware**: Structured logging to remote service with validation
- **Dynamic Programming**: Efficient knapsack algorithm implementation
- **Error Handling**: Comprehensive validation and error reporting
- **Flexible Data Parsing**: Supports multiple key variations in API responses

## Architecture

### Components

- `vehicle_maintance_scheduler/`: Main application module
  - `main.py`: Entry point that orchestrates the scheduling process
  - `algorithm.py`: Dynamic programming implementation for task selection
  - `api.py`: API client with authentication and caching
- `logging_middleware/`: Structured logging utility
  - `logger.py`: Remote logging client with validation
  - `__init__.py`: Module exports

### Algorithm

The core scheduling uses 0/1 Knapsack dynamic programming where:
- **Items**: Vehicle maintenance tasks
- **Weights**: Service duration (hours)
- **Values**: Operational impact scores
- **Capacity**: Available mechanic-hours per depot

Time complexity: O(n × W) where n is number of vehicles and W is budget hours.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/kishoreafk/RA2311026010611.git
cd vehicle-maintance-scheduler
```

2. Install dependencies:
```bash
pip install requests
```

## Usage

### Environment Variables

- `AUTH_TOKEN`: Pre-existing authentication token (optional, will auto-generate if missing)
- `LOG_TO_STDERR`: Enable local logging to stderr (default: 1)
- `SCHEDULER_DISABLE_CACHE`: Disable API response caching (default: 0)
- `SCHEDULER_REFRESH_DATA`: Force refresh cached data (default: 0)
- `SCHEDULER_FETCH_ATTEMPTS`: Maximum API fetch attempts (default: 10)

### Running the Scheduler

```bash
python vehicle_maintance_scheduler/main.py
```

The program will:
1. Authenticate with the evaluation service
2. Fetch depot and vehicle data
3. Compute optimal schedules for each depot
4. Output JSON results with selected tasks and impact scores

### Sample Output

```json
{
  "results": [
    {
      "depot_id": 1,
      "budget": 60,
      "used_hours": 45,
      "max_impact": 150,
      "selected_count": 3,
      "selected_tasks": [101, 203, 305]
    }
  ]
}
```

## APIs Used

### Authentication
- **URL**: `http://20.207.122.201/evaluation-service/auth`
- **Method**: POST
- **Payload**: Student credentials and client secrets

### Depots
- **URL**: `http://20.207.122.201/evaluation-service/depots`
- **Method**: GET
- **Response**: List of depots with IDs and mechanic-hours budgets

### Vehicles
- **URL**: `http://20.207.122.201/evaluation-service/vehicles`
- **Method**: GET
- **Response**: List of vehicles with task IDs, durations, and impact scores

### Logging
- **URL**: `http://20.207.122.201/evaluation-service/logs`
- **Method**: POST
- **Payload**: Structured log entries with stack, level, package, and message

## Logging Middleware

The logging system provides:
- Remote logging to evaluation service
- Local fallback logging to stderr
- Message length limits (48 characters)
- Validation of stack, level, and package categories
- Automatic truncation for long messages

### Valid Categories

**Stacks**: `backend`, `frontend`

**Levels**: `debug`, `info`, `warn`, `error`, `fatal`

**Packages**: `cache`, `controller`, `cron_job`, `db`, `domain`, `handler`, `repository`, `route`, `service`, `api`, `component`, `hook`, `page`, `state`, `style`, `auth`, `config`, `middleware`, `utils`

## Development

### Code Structure

- Modular design with clear separation of concerns
- Robust error handling with custom exceptions
- Type coercion and validation for API data
- Flexible key parsing for varying API response formats
- Comprehensive logging for debugging and monitoring

### Testing

Run the scheduler with sample data or use the provided APIs for integration testing.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is developed as part of an evaluation assignment.