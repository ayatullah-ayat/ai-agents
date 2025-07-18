import time
import traceback

import json
from typing import List, Dict, Any
from action import Action

class Environment:
    def execute_action(self, action: Action, args: dict) -> dict:
        """Execute an action and return the result."""
        try:
            result = action.execute(**(args or {}))
            return self.format_result(result)
        except Exception as e:
            return {
                "tool_executed": False,
                "error": str(e),
                "traceback": traceback.format_exc()
            }

    def format_result(self, result: Any) -> dict:
        """Format the result with metadata."""
        return {
            "tool_executed": True,
            "result": result,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z")
        }
