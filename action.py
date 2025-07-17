from typing import Callable, Dict, Any, List

class Action:
    def __init__(self,
                 name: str,
                 function: Callable,
                 description: str,
                 parameters: Dict,
                 terminal: bool = False):
        self.name = name
        self.function = function
        self.description = description
        self.terminal = terminal
        self.parameters = parameters

    def execute(self, **args) -> Any:
        """Execute the action's function"""
        return self.function(**args)

class ActionRegistry:
    def __init__(self):
        self.actions = {}

    def register(self, action: Action):
        self.actions[action.name] = action

    def get_action(self, name: str) -> Any:
        return self.actions.get(name, None)

    def get_actions(self) -> List[Action]:
        """Get all registered actions"""
        return list(self.actions.values())