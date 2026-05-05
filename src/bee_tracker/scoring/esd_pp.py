from __future__ import annotations
import pandas as pd
from ..config import Scorecard
from .base import ElementResult, ElementScorer
from .procurement import total_measured_procurement_spend, recognised_spend_for_supplier


def _supplier_lookup(suppliers: pd.DataFrame) -> pd.DataFrame:
    if suppliers.empty:
        return suppliers
    return suppliers.set_index("supplier_id")


def _recognised_total(
    procurement: pd.DataFrame, suppliers_idx: pd.DataFrame, scorecard: Scorecard,
    *,
    predicate=lambda s: True,
    row_predicate=lambda row: True,
) -> float:
    """Sum recognised spend across procurement rows whose supplier matches predicate."""
    if procurement.empty or suppliers_idx.empty:
        return 0.0
    total = 0.0
    for _, row in procurement.iterrows():
        if not row_predicate(row):
            continue
        sid = row.get("supplier_id")
        if sid not in suppliers_idx.index:
            continue
        supplier = suppliers_idx.loc[sid]
        if not predicate(supplier):
            continue
        measured = float(row.get("period_spend_ex_vat") or 0) - float(row.get("period_excluded_spend") or 0)
        total += recognised_spend_for_supplier(
            measured_spend=measured,
            cert_level=supplier.get("cert_level"),
            scorecard=scorecard,
        )
    return total


def score_esd_pp(
    *,
    suppliers: pd.DataFrame,
    procurement: pd.DataFrame,
    esd_contributions: pd.DataFrame,
    settings: dict,
    scorecard: Scorecard,
) -> ElementResult:
    cfg = scorecard.elements["enterprise_supplier_dev"]
    npat = settings.get("npat_current") or 0
    tmps = total_measured_procurement_spend(procurement)
    suppliers_idx = _supplier_lookup(suppliers)

    total_recognised = _recognised_total(procurement, suppliers_idx, scorecard)
    spend_51pct = _recognised_total(
        procurement, suppliers_idx, scorecard,
        predicate=lambda s: bool(s.get("is_51pct_black_owned")),
    )
    spend_emes = _recognised_total(
        procurement, suppliers_idx, scorecard,
        predicate=lambda s: str(s.get("cert_type")) in ("EME-affidavit", "QSE"),
    )
    spend_30day = _recognised_total(
        procurement, suppliers_idx, scorecard,
        predicate=lambda s: bool(s.get("is_51pct_black_owned")),
        row_predicate=lambda row: float(row.get("avg_payment_terms_days") or 999) <= 30,
    )

    ed_spend = 0.0
    sd_spend = 0.0
    if not esd_contributions.empty and "type" in esd_contributions.columns:
        for _, row in esd_contributions.iterrows():
            cash = float(row.get("cash_value") or 0)
            in_kind = float(row.get("in_kind_value") or 0)
            multiplier = float(row.get("recognition_multiplier") or 1.0)
            value = (cash + in_kind) * multiplier
            t = str(row.get("type") or "")
            if t == "Enterprise Development":
                ed_spend += value
            elif t == "Supplier Development":
                sd_spend += value

    indicator_actuals = {
        "total_b_bbee_pp_pct": (total_recognised / tmps * 100) if tmps else 0.0,
        "spend_with_51pct_black": (spend_51pct / tmps * 100) if tmps else 0.0,
        "spend_with_emes_qses": (spend_emes / tmps * 100) if tmps else 0.0,
        "ed_spend_npat_pct": (ed_spend / npat * 100) if npat else 0.0,
        "sd_spend_npat_pct": (sd_spend / npat * 100) if npat else 0.0,
        "payment_terms_30_day_bonus": (spend_30day / tmps * 100) if tmps else 0.0,
    }
    indicator_points: dict[str, float] = {}
    for indicator, target in cfg.indicators.items():
        actual = indicator_actuals.get(indicator, 0.0)
        ratio = 0.0 if target.target_pct == 0 else actual / target.target_pct
        ratio = min(ratio, 1.0)
        indicator_points[indicator] = round(ratio * target.weighting, 4)

    subtotal = round(sum(indicator_points.values()), 4)
    sub_min_pct = cfg.sub_minimum_pct or 40
    sub_minimum_breach = (subtotal / cfg.total_points * 100.0) < sub_min_pct

    return ElementResult(
        element="enterprise_supplier_dev",
        indicator_points=indicator_points,
        subtotal=subtotal,
        max_points=cfg.total_points,
        sub_minimum_breach=sub_minimum_breach,
    )


class ESDPPScorer(ElementScorer):
    element_name = "enterprise_supplier_dev"

    def score(self, inputs: dict, scorecard: Scorecard) -> ElementResult:
        return score_esd_pp(
            suppliers=inputs["suppliers"],
            procurement=inputs["procurement"],
            esd_contributions=inputs["esd_contributions"],
            settings=inputs["settings"],
            scorecard=scorecard,
        )
