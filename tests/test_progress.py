import pytest
from app.services.roadmap_service import RoadmapService


def test_progress_zero_tasks():
    assert RoadmapService.calculate_progress([]) == 0


def test_progress_single_task_zero():
    tasks = [{"progress": 0}]
    assert RoadmapService.calculate_progress(tasks) == 0


def test_progress_single_task_hundred():
    tasks = [{"progress": 100}]
    assert RoadmapService.calculate_progress(tasks) == 100


def test_progress_mixed_tasks():
    # Tasks: 100, 100, 50, 0 => sum 250 / 4 = 62.5 => rounded to 63 or 62
    tasks = [{"progress": 100}, {"progress": 100}, {"progress": 50}, {"progress": 0}]
    progress = RoadmapService.calculate_progress(tasks)
    assert progress in [62, 63]


def test_progress_hundred_percent_completion():
    tasks = [{"progress": 100}, {"progress": 100}, {"progress": 100}]
    assert RoadmapService.calculate_progress(tasks) == 100


def test_progress_boundary_clamping():
    tasks_under = [{"progress": -25}]
    assert RoadmapService.calculate_progress(tasks_under) == 0

    tasks_over = [{"progress": 150}]
    assert RoadmapService.calculate_progress(tasks_over) == 100


def test_status_calculation_rules():
    service = RoadmapService(session=None)

    assert service.calculate_roadmap_status([]) == "Backlog"
    assert service.calculate_roadmap_status([{"progress": 0}, {"progress": 0}]) == "Backlog"
    assert service.calculate_roadmap_status([{"progress": 100}, {"progress": 0}]) == "In Progress"
    assert service.calculate_roadmap_status([{"progress": 100}, {"progress": 100}]) == "Released"
