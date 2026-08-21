import pytest
from app.services.progress_service import ProgressService


def test_progress_math_scenarios():
    service = ProgressService()

    # 0 tasks -> 0%
    assert service.calculate_progress([]) == 0

    # 1 task at 0 -> 0%
    assert service.calculate_progress([{"progress": 0}]) == 0

    # 1 task at 100 -> 100%
    assert service.calculate_progress([{"progress": 100}]) == 100

    # 2 tasks: 100 + 0 -> 50%
    assert service.calculate_progress([{"progress": 100}, {"progress": 0}]) == 50

    # 3 tasks: 100 + 50 + 0 -> 50%
    assert service.calculate_progress([{"progress": 100}, {"progress": 50}, {"progress": 0}]) == 50

    # 4 tasks: 100 + 100 + 50 + 0 -> 63% (rounded)
    assert service.calculate_progress([{"progress": 100}, {"progress": 100}, {"progress": 50}, {"progress": 0}]) in [62, 63]

    # All 100 -> 100%
    assert service.calculate_progress([{"progress": 100}, {"progress": 100}, {"progress": 100}]) == 100


def test_roadmap_status_rules():
    service = ProgressService()

    # 1. No tasks -> Backlog
    assert service.calculate_roadmap_status([]) == "Backlog"

    # 2. All tasks untouched -> Backlog
    assert service.calculate_roadmap_status([{"progress": 0, "status": "Open"}, {"progress": 0, "status": "Open"}]) == "Backlog"

    # 3. Planned/approved state but 0 progress -> Planned
    assert service.calculate_roadmap_status([{"progress": 0, "status": "Approved"}, {"progress": 0, "status": "Open"}]) == "Planned"

    # 4. Active work -> In Progress
    assert service.calculate_roadmap_status([{"progress": 50, "status": "In Progress"}, {"progress": 0, "status": "Open"}]) == "In Progress"

    # 5. Implementation complete (100%) but testing/approval pending -> Testing
    assert service.calculate_roadmap_status([{"progress": 100, "status": "Approved"}, {"progress": 100, "status": "Approved"}]) == "Testing"

    # 6. All required work complete & resolved -> Released
    assert service.calculate_roadmap_status([{"progress": 100, "status": "Resolved"}, {"progress": 100, "status": "Closed"}]) == "Released"
