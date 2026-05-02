# Develop Logging Middleware

The 'Logging Middleware' is a critical component for building robust and observable applications. While error logging is essential, we expect you to implement logging that captures the entire lifecycle of significant events within your application – from successful operations to warnings, informational messages, and debugging details. Think of logs as the narrative of your application's execution! These logs are crucial for understanding application behavior, performance, and for effective debugging.

Note: While you have flexibility in choosing your backend language/framework, the Logging Middleware must be a reusable package. If attempting the Full Stack track, both this middleware and your backend application must be developed in TypeScript/JavaScript to enable the logging package's consumption by the Frontend.

Write a reusable function that makes an API call to the Test Server each time the function is called that matches the below structure:

Log(stack, level, package, message)

Integrate this reusable Log function strategically throughout your codebase. Each Log call should provide specific and descriptive context about what's happening. Instead of generic messages, aim for logs that clearly communicate the state, actions, and any relevant data at that point in the code.

We encourage you to think critically about what information would be most valuable if you were to troubleshoot your application months from now. That's the information you should be logging!

## Examples

```python
# If an error occurs in your application's handler due to a data type mismatch
Log("backend", "error", "handler", "received string, expected bool")

# If an error occurs in your application's db layer
Log("backend", "fatal", "db", "Critical database connection failure.")
```

## Log API (POST)

http://20.207.122.201/evaluation-service/logs

## Constraints

- API is a protected Route  
- Stack, Level and Package Fields accept only the following values (in lower case only)

### Stack
- "backend"
- "frontend"

### Level
- "debug"
- "info"
- "warn"
- "error"
- "fatal"

### Package (Backend)
- "cache"
- "controller"
- "cron_job"
- "db"
- "domain"
- "handler"
- "repository"
- "route"
- "service"

### Package (Frontend)
- "api"
- "component"
- "hook"
- "page"
- "state"
- "style"

### Package (Both)
- "auth"
- "config"
- "middleware"
- "utils"

## Request Body

```json
{
  "stack": "backend",
  "level": "error",
  "package": "handler",
  "message": "received string, expected bool"
}
```

## Response (Status Code: 200)

```json
{
  "logID": "a4aad02e-19d0-4153-86d9-58bf55d7c402",
  "message": "log created successfully"
}
```
