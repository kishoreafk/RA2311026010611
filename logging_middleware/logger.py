import os
import sys
import requests

#the log url for the company that has been provided.
LOG_URL = "http://20.207.122.201/evaluation-service/logs"

#maximux message limit that has been mentioned.
MAX_MESSAGE_LENGTH = 48

#allowed modules mentioned in the loggin_middleware doc.
VALID_STACKS = {"backend", "frontend"}
VALID_LEVELS = {"debug", "info", "warn", "error", "fatal"}
VALID_PACKAGES = {
    "cache", "controller", "cron_job", "db", "domain", "handler", "repository", "route", "service",
    "api", "component", "hook", "page", "state", "style",
    "auth", "config", "middleware", "utils"
}

#log checker function.
def _local_log_enabled():
    return os.environ.get("LOG_TO_STDERR", "1").lower() not in {"0", "false", "no"}


def _write_local_log(status, stack, level, package, message):
    if not _local_log_enabled():
        return
    print(f"[log:{status}] stack={stack} level={level} package={package} message={message}", file=sys.stderr)

#function to check the msg do dont exceed the given msg limit.
def _normalize_message(message):
    message = str(message)
    if len(message) <= MAX_MESSAGE_LENGTH:
        return message
    return f"{message[:MAX_MESSAGE_LENGTH - 3]}..."


def Log(stack, level, package, message):
    message = _normalize_message(message)
    token = os.environ.get("AUTH_TOKEN")
        
    if not token:
        _write_local_log("skipped-no-token", stack, level, package, message)
        return None

    if stack not in VALID_STACKS:
        _write_local_log("rejected-invalid-stack", stack, level, package, message)
        return None
        
    if level not in VALID_LEVELS:
        _write_local_log("rejected-invalid-level", stack, level, package, message)
        return None
        
    if package not in VALID_PACKAGES:
        _write_local_log("rejected-invalid-package", stack, level, package, message)
        return None

    payload = {
        "stack": stack,
        "level": level,
        "package": package,
        "message": message
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    try:
        _write_local_log("posting", stack, level, package, message)
        response = requests.post(LOG_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        result = response.json()
        _write_local_log("posted", stack, level, package, message)
        return result
    except Exception:
        _write_local_log("failed", stack, level, package, message)
        return None
