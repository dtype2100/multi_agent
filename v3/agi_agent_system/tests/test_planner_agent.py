import unittest
# Try to make imports robust for different execution contexts
try:
    from v3.agi_agent_system.agents.planner import SubTask, TaskPlan
except ImportError:
    # Path for running tests from within tests directory or similar
    from ..agents.planner import SubTask, TaskPlan 
from pydantic import ValidationError

class TestPlannerModels(unittest.TestCase):
    def test_subtask_validation_success(self):
        data = {"task_id": 1, "description": "Test task", "priority": 3, "dependencies": [0]}
        try:
            SubTask(**data)
        except ValidationError as e:
            self.fail(f"SubTask validation failed unexpectedly: {e}")

    def test_subtask_validation_failure(self):
        data = {"task_id": 1, "priority": 3, "dependencies": [0]} # Missing 'description'
        with self.assertRaises(ValidationError):
            SubTask(**data)

    def test_taskplan_with_subtasks(self):
        subtask_data = {"task_id": 1, "description": "Test task", "priority": 3, "dependencies": []}
        plan_data = {"tasks": [subtask_data]}
        try:
            task_plan = TaskPlan(**plan_data)
            self.assertEqual(len(task_plan.tasks), 1)
            self.assertIsInstance(task_plan.tasks[0], SubTask)
        except ValidationError as e:
            self.fail(f"TaskPlan validation failed unexpectedly: {e}")

if __name__ == '__main__':
    # This allows running the test file directly
    unittest.main()
