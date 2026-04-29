from __future__ import annotations
from openpyxl import Workbook
from ..scoring.base import ElementResult


def _clear_sheet(wb: Workbook, sheet: str) -> None:
    ws = wb[sheet]
    # openpyxl doesn't have a clear(); delete all rows then re-append headers
    if ws.max_row > 0:
        ws.delete_rows(1, ws.max_row)


def write_calc_ownership(wb: Workbook, result: ElementResult) -> None:
    """Overwrite Calc_Ownership with the given result. Does not touch any other sheet."""
    _clear_sheet(wb, "Calc_Ownership")
    ws = wb["Calc_Ownership"]
    ws.append(["indicator", "points_earned", "max_points_check"])
    for indicator, points in result.indicator_points.items():
        ws.append([indicator, points, None])
    ws.append([])
    ws.append(["SUBTOTAL", result.subtotal, None])
    ws.append(["MAX_POINTS", result.max_points, None])
    ws.append(["SUB_MINIMUM_BREACH", result.sub_minimum_breach, None])


def write_calc_mgmt_control(wb: Workbook, result: ElementResult) -> None:
    """Overwrite Calc_MgmtControl with the given result."""
    _clear_sheet(wb, "Calc_MgmtControl")
    ws = wb["Calc_MgmtControl"]
    ws.append(["indicator", "points_earned", "max_points_check"])
    for indicator, points in result.indicator_points.items():
        ws.append([indicator, points, None])
    ws.append([])
    ws.append(["SUBTOTAL", result.subtotal, None])
    ws.append(["MAX_POINTS", result.max_points, None])
    ws.append(["SUB_MINIMUM_BREACH", result.sub_minimum_breach, None])


def write_calc_skills_dev(wb: Workbook, result: ElementResult) -> None:
    """Overwrite Calc_SkillsDev with the given result."""
    _clear_sheet(wb, "Calc_SkillsDev")
    ws = wb["Calc_SkillsDev"]
    ws.append(["indicator", "points_earned", "max_points_check"])
    for indicator, points in result.indicator_points.items():
        ws.append([indicator, points, None])
    ws.append([])
    ws.append(["SUBTOTAL", result.subtotal, None])
    ws.append(["MAX_POINTS", result.max_points, None])
    ws.append(["SUB_MINIMUM_BREACH", result.sub_minimum_breach, None])


def write_calc_esd(wb: Workbook, result: ElementResult) -> None:
    """Overwrite Calc_ESD with the given result."""
    _clear_sheet(wb, "Calc_ESD")
    ws = wb["Calc_ESD"]
    ws.append(["indicator", "points_earned", "max_points_check"])
    for indicator, points in result.indicator_points.items():
        ws.append([indicator, points, None])
    ws.append([])
    ws.append(["SUBTOTAL", result.subtotal, None])
    ws.append(["MAX_POINTS", result.max_points, None])
    ws.append(["SUB_MINIMUM_BREACH", result.sub_minimum_breach, None])


def write_calc_sed(wb: Workbook, result: ElementResult) -> None:
    """Overwrite Calc_SED with the given result."""
    _clear_sheet(wb, "Calc_SED")
    ws = wb["Calc_SED"]
    ws.append(["indicator", "points_earned", "max_points_check"])
    for indicator, points in result.indicator_points.items():
        ws.append([indicator, points, None])
    ws.append([])
    ws.append(["SUBTOTAL", result.subtotal, None])
    ws.append(["MAX_POINTS", result.max_points, None])
    ws.append(["SUB_MINIMUM_BREACH", result.sub_minimum_breach, None])
