from static_distribution_bandits import BinaryRewardsBandit

class MultiArmedStaticBinaryRewardsBanditEnvironment:

    MAX_REWARD = BinaryRewardsBandit.MAX_REWARD

    def __init__(self, num_arms):
        self.num_bandits = num_arms
        self.bandits = [BinaryRewardsBandit() for _ in range(num_arms)]
        self.history = []

    def act(self, bandit_idx):
        reward = self.bandits[bandit_idx].act()
        self.history.append((bandit_idx, reward))
        return reward

    def get_distributions(self):
        distribution = []
        for bandit_idx in range(self.num_bandits):
            distribution.append(self.bandits[bandit_idx].get_distribution())