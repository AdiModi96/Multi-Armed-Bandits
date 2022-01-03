from enum import Enum
import random
from collections import OrderedDict

class BinaryRewardsBandit:

    class REWARDS(Enum):
        FAILURE = 0
        SUCCESS = 1

    MAX_REWARD = max([reward.value for reward in REWARDS])
    MIN_REWARD = min([reward.value for reward in REWARDS])

    def __init__(self):

        total_weight = 0
        self.distribution = OrderedDict()
        for reward in BinaryRewardsBandit.REWARDS:
            self.distribution[reward.name] = {
                'value': reward.value,
                'weight': random.uniform(0.4, 0.6)
            }
            total_weight += self.distribution[reward.name]['weight']

        for reward in BinaryRewardsBandit.REWARDS:
            self.distribution[reward.name]['probability'] = self.distribution[reward.name]['weight'] / total_weight


        self.history = []

    def get_distribution(self):
        return self.distribution

    def act(self):
        returned_reward = random.choices(
            list(self.distribution.keys()),
            [self.distribution[reward]['weight'] for reward in self.distribution.keys()]
        )[0]
        self.history.append(
            BinaryRewardsBandit.REWARDS[returned_reward]
        )
        return BinaryRewardsBandit.REWARDS[returned_reward]
