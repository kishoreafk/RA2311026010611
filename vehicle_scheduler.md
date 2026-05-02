# Vehicle Maintenance Scheduler Microservice

You’ve joined a team responsible for planning daily vehicle maintenance at a logistics company. Each depot handles many service requests every day - from quick fixes to longer repairs. Every request (or task) comes with two key details: how long it will take (in hours) and a score that represents how important it is to complete that task soon. The importance score is based on how much the vehicle contributes to operations. For example, a vehicle running frequent delivery routes or handling busy areas may have a higher score compared to a rarely used backup vehicle. So, choosing the right set of tasks directly affects overall efficiency.

However, there’s a strict limit on how many mechanic-hours are available each day. This means you cannot complete all tasks and must carefully decide which ones to include. The challenge is to pick a combination of tasks such that:
- The total time spent does not exceed the available mechanic-hours  
- The total importance score is as high as possible  

Since the number of tasks can be very large, the solution should be efficient enough to handle real-world scale inputs.

Given a list of vehicles requiring maintenance, each with an operational impact score and estimated service duration, and a daily mechanic-hour budget, determine the subset of vehicles to service to maximise the total operational impact score within the available budget. Submit your code along with output screenshots to the “vehicle_scheduling” folder in the GitHub Repository you created while building the logging middleware.

You're provided with the below APIs. You are expected to use these APIs to fetch the depot and task details. You need not store them in a database, nor are you supposed to hard-code or create them yourself.

## Depot API (GET)
http://20.207.122.201/evaluation-service/depots

### Constraints
- API is a protected Route  

### Response (Status Code: 200)
{
  "depots": [
    { "ID": 1, "MechanicHours": 60 },
    { "ID": 2, "MechanicHours": 135 },
    { "ID": 3, "MechanicHours": 188 },
    { "ID": 4, "MechanicHours": 97 },
    { "ID": 5, "MechanicHours": 164 }
  ]
}

## Vehicles API (GET)
http://20.207.122.201/evaluation-service/vehicles

### Constraints
- API is a protected Route  
