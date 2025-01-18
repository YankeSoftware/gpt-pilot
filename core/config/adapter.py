from enum import Enum

class UIAdapter(str, Enum):
    """UI Adapter types supported by Pythagora."""
    PLAIN = "plain"
    IPC_CLIENT = "ipc_client"
    VIRTUAL = "virtual"