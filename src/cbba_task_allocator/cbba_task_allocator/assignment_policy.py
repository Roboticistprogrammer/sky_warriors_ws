from typing import Iterable, List, Sequence

from skyw_interfaces.msg import Task

from cbba_task_allocator.constants import TASK_REMOVE_MEMBER


class DeterministicAssignmentPolicy:
    """Select assignees using fixed rules instead of bid scoring."""

    def __init__(self, leader_agent_id: int, follower_agent_ids: Sequence[int]):
        self.leader_agent_id = int(leader_agent_id)
        self.follower_agent_ids = [int(a) for a in follower_agent_ids if int(a) != int(leader_agent_id)]
        self._remove_rr_index = 0

    def choose_agents(self, task: Task, available_agent_ids: Iterable[int]) -> List[int]:
        available = set(int(a) for a in available_agent_ids)
        followers = [a for a in self.follower_agent_ids if a in available]

        if not followers:
            return []

        if int(task.task_type) == TASK_REMOVE_MEMBER:
            # Keep remove actions deterministic and evenly distributed over followers.
            idx = self._remove_rr_index % len(followers)
            self._remove_rr_index += 1
            return [followers[idx]]

        required = max(1, int(task.required_agents))
        return followers[:required]