from .entry_manipulator_orchestrator import EntryManipulatorOrchestrator

__plugins__ = ["entry_manipulation"]


def entry_manipulators(entries, options_map, config_str=""):
    return EntryManipulatorOrchestrator().execute(entries, options_map, config_str)
