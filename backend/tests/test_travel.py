"""Ticket refunds (passengers) through the real pipeline, offline mock mode: S10 bus turned back, S11 airline refund not
passed on, and unscripted complaints from other seeded passengers (no-show, airline not paid, already refunded,
airline paid recently). All data is fictional seed data."""
from __future__ import annotations

import asyncio

import pytest

from munim.db.conn import connect, one, rows
from munim.graph.runner import case_status

from tests.test_e2e import demo_db, run_scenario  # noqa: F401  (fixture re-export)


def run_complaint(merchant_id: str, text: str):
    from munim.graph import runner
    case_id, merchant = runner.create_case(merchant_id, text, "chat", None)
    state = asyncio.run(runner.run_case(case_id, merchant, text, "chat", None))
    return case_id, state, runner.RUNS[case_id].events


def reply_of(events) -> str:
    return [e for e in events if e.type == "message" and e.data["role"] == "munim"][-1].data["text"]


def suspects_of(events) -> dict[str, str]:
    return {e.data["suspect_id"]: e.data["status"] for e in events if e.type == "suspect"}


def refunds(db, merchant_id: str) -> list[dict]:
    with connect(db) as conn:
        return rows(conn, "SELECT amount_paise FROM ledger_entries WHERE merchant_id=? AND entry_type='REFUND_CREDIT'", (merchant_id,))


def test_s10_bus_fare_refunded_and_sweep(demo_db):
    _, state, events = run_scenario("bus_turned_back")
    assert state["verdict"]["culprits"] == ["BUS_TRIP_FAILED"]
    assert set(suspects_of(events)) == {"BUS_TRIP_FAILED", "AIRLINE_REFUND_NOT_PASSED", "TRAVEL_NO_SHOW", "AIRLINE_NOT_PAID",
                                        "ALREADY_REFUNDED"}
    av = {a["proposed"]["action_type"]: a for a in state["firewall"]["actions"]}
    assert av["REFUND_DEBITS"]["decision"] == "ALLOW" and av["REFUND_DEBITS"]["final"]["amount_paise"] == 164000
    assert [r["amount_paise"] for r in refunds(demo_db, "P2001")] == [164000]
    # the refund settles the passenger even though the operator is chased for the cost
    assert case_status(state) == "RESOLVED"
    sweep = [e for e in events if e.type == "sweep"]
    assert sweep and sweep[0].data["merchant_count"] == 18 and sweep[0].data["suspect_id"] == "BUS_TRIP_FAILED"
    text = reply_of(events)
    assert "₹1,640" in text


def test_s11_airline_refund_needs_human_then_executes(demo_db):
    from munim.actions.executor import approve, pending
    from munim.db.conn import tx
    case_id, state, events = run_scenario("flight_refund")
    assert state["verdict"]["culprits"] == ["AIRLINE_REFUND_NOT_PASSED"]
    assert state["firewall"]["decision"] == "NEEDS_HUMAN"
    assert refunds(demo_db, "P2002") == []            # over the auto limit: nothing moves before a human signs off
    sweep = [e for e in events if e.type == "sweep"]
    assert sweep and sweep[0].data["merchant_count"] == 8
    with tx() as conn:
        queue = [p for p in pending(conn) if p["case_id"] == case_id]
    assert len(queue) == 1 and queue[0]["action_type"] == "REFUND_DEBITS"
    with tx() as conn:
        res = approve(conn, queue[0]["action_id"], "ops.lead")
    assert res.status == "EXECUTED" and res.amount_paise == 2186000
    assert [r["amount_paise"] for r in refunds(demo_db, "P2002")] == [2186000]


def test_no_show_is_not_refunded(demo_db):
    _, state, events = run_complaint("P2121", "My Vega Sleeper Lines bus on 9 Nov turned back, where is my refund of the ticket fare?")
    assert state["verdict"]["outcome"] == "NO_FAULT" and state["verdict"]["culprits"] == ["TRAVEL_NO_SHOW"]
    assert suspects_of(events)["BUS_TRIP_FAILED"] == "ELIMINATED"
    assert refunds(demo_db, "P2121") == []
    assert "boarding scan" in reply_of(events)


def test_airline_not_paid_is_escalated_to_travel(demo_db):
    _, state, events = run_complaint("P2210", "Koel Skyways cancelled my flight and I still have not got my refund of ₹4,980.")
    v = state["verdict"]
    assert v["outcome"] == "HOLD_EXPLAINED" and v["culprits"] == ["AIRLINE_NOT_PAID"]
    esc = [e for e in state["executions"] if e["action_type"] == "ESCALATE"]
    assert esc and esc[0]["status"] == "EXECUTED"
    assert refunds(demo_db, "P2210") == []
    assert case_status(state) == "ESCALATED"


def test_airline_paid_recently_is_on_its_way(demo_db):
    _, state, events = run_complaint("P2211", "My Nimbus Air flight got cancelled, refund ₹5,390 not received.")
    v = state["verdict"]
    assert v["outcome"] == "HOLD_EXPLAINED" and v["culprits"] == ["AIRLINE_NOT_PAID"]
    assert v["targets"]["due_by"] == "2026-11-18" and v["headline"].startswith("Refund on its way")
    assert suspects_of(events)["AIRLINE_REFUND_NOT_PASSED"] == "ELIMINATED"   # still inside the 7-day window
    assert refunds(demo_db, "P2211") == []
    text = reply_of(events)
    assert "18 Nov" in text and "authorised" not in text


def test_already_refunded_fare_not_paid_twice(demo_db):
    _, state, events = run_complaint("P2209", "Nimbus Air cancelled my flight, I want my ₹6,120 refund.")
    assert state["verdict"]["culprits"] == ["ALREADY_REFUNDED"]
    with connect(demo_db) as conn:
        n = one(conn, "SELECT COUNT(*) AS n FROM ledger_entries WHERE merchant_id='P2209' AND entry_type='REFUND_CREDIT'")["n"]
    assert n == 1                                      # the seeded refund only
    text = reply_of(events)
    assert "₹6,120" in text and "₹12,240" not in text


def test_another_bus_passenger_gets_the_same_fix(demo_db):
    _, state, events = run_complaint("P2105", "The bus turned back on 9 Nov and I did not get my ticket refund.")
    assert state["verdict"]["culprits"] == ["BUS_TRIP_FAILED"]
    assert [r["amount_paise"] for r in refunds(demo_db, "P2105")] == [179000]
    assert "On 9 Nov" in reply_of(events)


@pytest.mark.parametrize("scenario_id", ["zombie_rent", "kyc_hold"])
def test_shops_keep_the_shop_lineup(demo_db, scenario_id):
    _, _, events = run_scenario(scenario_id)
    ids = set(suspects_of(events))
    assert len(ids) == 8 and not ids & {"BUS_TRIP_FAILED", "AIRLINE_REFUND_NOT_PASSED", "TRAVEL_NO_SHOW", "AIRLINE_NOT_PAID"}


def test_case_status_refund_with_cost_recovery_is_resolved():
    refund = {"status": "EXECUTED", "action_type": "REFUND_DEBITS"}
    esc = {"status": "EXECUTED", "action_type": "ESCALATE"}
    assert case_status({"executions": [refund, esc]}) == "RESOLVED"
    assert case_status({"executions": [esc]}) == "ESCALATED"
