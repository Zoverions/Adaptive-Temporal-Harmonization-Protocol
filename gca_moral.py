"""
GCA Phase 1: Moral Kernel
-------------------------
A geometric moral calculator for actions.
"""

from enum import Enum
import math

class EntropyClass(Enum):
    REVERSIBLE = 1
    IRREVERSIBLE = 2

class Action:
    def __init__(self, type, description, harm, utility, uncertainty, scale, agents_affected, entropy_class):
        self.type = type
        self.description = description
        self.harm = harm  # 0-1
        self.utility = utility  # 0-1
        self.uncertainty = uncertainty  # 0-1
        self.scale = scale  # 0-1
        self.agents_affected = agents_affected  # int
        self.entropy_class = entropy_class

class MoralCalculator:
    def __init__(self):
        self.threshold = 0.5  # Adjustable moral threshold

    def calculate_moral_vector(self, action):
        # Simple geometric representation (can be expanded)
        magnitude = math.sqrt(action.harm**2 + (1 - action.utility)**2 + action.uncertainty**2)
        scaled_magnitude = magnitude * action.scale * math.log(action.agents_affected + 1)
        if action.entropy_class == EntropyClass.IRREVERSIBLE:
            scaled_magnitude *= 2  # Penalty for irreversibility
        return scaled_magnitude

    def evaluate_plan(self, actions):
        total_moral = sum(self.calculate_moral_vector(a) for a in actions)
        approved = total_moral < self.threshold
        reason = "Moral vector below threshold" if approved else "Moral vector exceeds threshold"
        return approved, reason, total_moral
