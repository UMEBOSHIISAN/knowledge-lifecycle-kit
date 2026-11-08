from __future__ import annotations

import datetime
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from knowledge_lifecycle_gate import (
    KnowledgeTrustWriter,
    PromotionGateError,
    StorageDurabilityError,
)
from knowledge_lifecycle_gate import trust_writer


TODAY = datetime.date(2026, 11, 8)
YESTERDAY = TODAY - datetime.timedelta(days=1)
SOURCE = b"Latest source evidence.\n"
TARGET = "memory/measurement.md"


@pytest.fixture
def writer(tmp_path, monkeypatch):
    class FrozenDate(datetime.date):
        @classmethod
        def today(cls):
            return TODAY

    monkeypatch.setattr(
        trust_writer, "datetime",
        SimpleNamespace(date=FrozenDate, datetime=datetime.datetime, timezone=datetime.timezone),
    )
    return KnowledgeTrustWriter(tmp_path)


def note(state="CONFIRMED", *, verified=TODAY, expires=TODAY, kind="EVIDENCE",
         lineage="fixture/measurement", body="Evidence."):
    return (
        f"---\nasset_type: {kind}\nstate: {state}\nlineage:\n  - {lineage}\n"
        f"last_verified: {verified}\nvalid_until: {expires}\n---\n{body}\n"
    )


def digest(raw):
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def review(old, new, *, target=TARGET, index=0, decision="decision/1"):
    return {
        "target": target,
        "current_audit_index": index,
        "before_hash": digest(old.encode()),
        "after_hash": digest(new.encode()),
        "evidence_ref": "fixture/measurement",
        "evidence_sha256": digest(SOURCE),
        "reviewer": "reviewer",
        "decision_ref": decision,
    }


def snapshot(writer):
    return {
        path.relative_to(writer.base_dir): path.read_bytes()
        for path in writer.base_dir.rglob("*") if path.is_file()
    }


def revalidate(writer, content, approved, *, target=TARGET, evidence=SOURCE):
    return writer.revalidate(target, content, "operator", "Checked current source",
                             evidence=evidence, review=approved)


@pytest.mark.parametrize("state", ["STALE", "CONFIRMED"])
def test_revalidation_preserves_old_version_and_records_review(writer, state):
    old = note(state, verified=YESTERDAY, expires=YESTERDAY)
    new = note()
    first = writer.commit(TARGET, old, "operator", "Initial note")
    approved = review(old, new)

    result = revalidate(writer, new, approved)

    assert result.status == "REVALIDATED"
    assert Path(first.version_path).read_bytes() == old.encode()
    assert Path(result.version_path).read_bytes() == new.encode()
    assert (writer.store_dir / TARGET).read_bytes() == new.encode()
    audit = [json.loads(line) for line in writer.audit_path.read_text().splitlines()]
    assert len(audit) == 2
    assert audit[-1] == result.audit_entry
    assert audit[-1]["action"] == "revalidate"
    assert audit[-1]["operation_date"] == "2026-11-08"
    assert {key: audit[-1][key] for key in approved} == approved
    assert SOURCE not in writer.audit_path.read_bytes()


@pytest.mark.parametrize("change", [
    {"before_hash": "sha256:" + "0" * 64},
    {"after_hash": "sha256:" + "0" * 64},
    {"target": "memory/other.md"},
    {"evidence_ref": "fixture/other"},
    {"evidence_sha256": "sha256:" + "0" * 64},
    {"reviewer": ""},
    {"decision_ref": " decision/1"},
    {"current_audit_index": 1},
])
def test_unbound_review_cannot_change_any_store_bytes(writer, change):
    old, new = note("STALE"), note()
    writer.commit(TARGET, old, "operator", "Initial note")
    before = snapshot(writer)

    with pytest.raises(PromotionGateError):
        revalidate(writer, new, {**review(old, new), **change})

    assert snapshot(writer) == before


@pytest.mark.parametrize("old", [
    note(), note("RETIRED"), note("STALE", kind="CONCEPT"),
])
def test_only_expired_or_stale_evidence_can_be_revalidated(writer, old):
    new = note()
    writer.commit(TARGET, old, "operator", "Initial note")
    before = snapshot(writer)
    with pytest.raises(PromotionGateError):
        revalidate(writer, new, review(old, new))
    assert snapshot(writer) == before


@pytest.mark.parametrize("new", [
    note(verified=YESTERDAY, expires=TODAY),
    note(expires=YESTERDAY),
    note(kind="CONCEPT"),
])
def test_revalidation_requires_evidence_verified_and_fresh_on_operation_date(writer, new):
    old = note("STALE")
    writer.commit(TARGET, old, "operator", "Initial note")
    before = snapshot(writer)
    with pytest.raises(PromotionGateError):
        revalidate(writer, new, review(old, new))
    assert snapshot(writer) == before


def test_review_decision_cannot_be_replayed_on_another_target(writer):
    other = "memory/other.md"
    old, new = note("STALE"), note()
    writer.commit(TARGET, old, "operator", "First note")
    writer.commit(other, old, "operator", "Second note")
    revalidate(writer, new, review(old, new))
    before = snapshot(writer)

    with pytest.raises(PromotionGateError, match="already used"):
        revalidate(writer, new, review(old, new, target=other, index=1), target=other)

    assert snapshot(writer) == before


def test_identical_restored_bytes_do_not_reinstate_an_old_review(writer):
    old, new = note("STALE"), note()
    first = writer.commit(TARGET, old, "operator", "Initial note")
    writer.commit(TARGET, note("STALE", body="Intermediate change."), "operator", "Edit")
    writer.rollback(TARGET, Path(first.version_path).name, "operator", "Restore stale bytes")
    before = snapshot(writer)

    with pytest.raises(PromotionGateError, match="current"):
        revalidate(writer, new, review(old, new))

    assert snapshot(writer) == before


@pytest.mark.parametrize("kind", ["EVIDENCE", "CONCEPT"])
def test_expired_evidence_cannot_be_refreshed_or_relabeled_by_commit(writer, kind):
    old = note(verified=YESTERDAY, expires=YESTERDAY)
    writer.commit(TARGET, old, "operator", "Initial note")
    before = snapshot(writer)
    assert writer.commit(TARGET, old, "operator", "No change").status == "NO_CHANGE"

    with pytest.raises(PromotionGateError, match="revalidat"):
        writer.commit(TARGET, note(verified=YESTERDAY, kind=kind), "operator", "Refresh dates",
                      as_of=YESTERDAY)

    assert snapshot(writer) == before


def test_rollback_cannot_restore_expired_evidence_after_revalidation(writer):
    old = note(verified=YESTERDAY, expires=YESTERDAY)
    new = note()
    first = writer.commit(TARGET, old, "operator", "Initial note")
    revalidate(writer, new, review(old, new))
    before = snapshot(writer)

    with pytest.raises(PromotionGateError, match="expired"):
        writer.rollback(TARGET, Path(first.version_path).name, "operator", "Undo")

    assert snapshot(writer) == before


def test_same_state_rollback_rejects_expired_version_without_revalidation(writer, monkeypatch):
    tomorrow = TODAY + datetime.timedelta(days=1)
    first = writer.commit(TARGET, note(), "operator", "Initial note")
    writer.commit(TARGET, note(expires=tomorrow), "operator", "Update while fresh")
    monkeypatch.setattr(trust_writer.datetime.date, "today", classmethod(lambda cls: tomorrow))
    before = snapshot(writer)

    with pytest.raises(PromotionGateError, match="expired"):
        writer.rollback(TARGET, Path(first.version_path).name, "operator", "Undo")

    assert snapshot(writer) == before


def test_rollback_cannot_replace_expired_current_with_fresh_confirmed_version(writer, monkeypatch):
    tomorrow = TODAY + datetime.timedelta(days=1)
    first = writer.commit(TARGET, note(expires=tomorrow), "operator", "Initial note")
    writer.commit(TARGET, note(), "operator", "Shorten validity while fresh")
    monkeypatch.setattr(trust_writer.datetime.date, "today", classmethod(lambda cls: tomorrow))
    before = snapshot(writer)

    with pytest.raises(PromotionGateError, match="revalidat"):
        writer.rollback(TARGET, Path(first.version_path).name, "operator", "Undo")

    assert snapshot(writer) == before


def test_concept_rollback_and_evidence_expiry_day_still_work(writer):
    for kind in ("CONCEPT", "EVIDENCE"):
        target = f"memory/{kind}.md"
        expiry = YESTERDAY if kind == "CONCEPT" else TODAY
        old = note(verified=YESTERDAY, expires=expiry, kind=kind)
        first = writer.commit(target, old, "operator", "Initial note")
        writer.commit(target, note(kind=kind), "operator", "Update")
        assert writer.rollback(target, Path(first.version_path).name, "operator", "Restore").status == "ROLLED_BACK"
        assert (writer.store_dir / target).read_bytes() == old.encode()


def test_revalidation_compensates_after_audit_append_failure(writer, monkeypatch):
    old, new = note("STALE"), note()
    writer.commit(TARGET, old, "operator", "Initial note")
    before = snapshot(writer)
    fsync = os.fsync

    def fail_audit_fsync(fd):
        if os.fstat(fd).st_ino == writer.audit_path.stat().st_ino:
            raise OSError("fixture audit fsync failure")
        fsync(fd)

    monkeypatch.setattr(os, "fsync", fail_audit_fsync)
    with pytest.raises(StorageDurabilityError, match="prior bytes restored"):
        revalidate(writer, new, review(old, new))
    assert snapshot(writer) == before


def test_contending_writer_fails_without_publishing(writer):
    import fcntl

    old, new = note("STALE"), note()
    writer.commit(TARGET, old, "operator", "Initial note")
    before = snapshot(writer)
    descriptor = os.open(writer.base_dir, os.O_RDONLY | os.O_DIRECTORY)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with pytest.raises(StorageDurabilityError, match="busy"):
            revalidate(writer, new, review(old, new))
        with pytest.raises(StorageDurabilityError, match="busy"):
            writer.commit(TARGET, old, "operator", "Contending commit")
    finally:
        os.close(descriptor)

    assert snapshot(writer) == before
