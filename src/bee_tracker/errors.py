from __future__ import annotations


class BeeTrackerError(Exception):
    """Base exception for the package."""


class ConfigError(BeeTrackerError):
    """Raised when a YAML config file is missing or malformed."""


class GraphError(BeeTrackerError):
    """Raised for Microsoft Graph API failures."""


class ConcurrencyError(GraphError):
    """Raised when a workbook was modified remotely during a local run."""


class WorkbookError(BeeTrackerError):
    """Raised for workbook read/write failures."""
