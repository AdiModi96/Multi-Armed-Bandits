from environments import MultiArmedStaticBinaryRewardsBanditEnvironment as Environment
from agents import StaticBinaryRewardsAgent as Agent
from matplotlib import pyplot as plt
from prettytable import PrettyTable


class Experiment:

    def __init__(self, experiment_parameters):
        self.num_turns = experiment_parameters['num_turns']
        self.num_arms = experiment_parameters['num_arms']

        self.environment = Environment(num_arms=self.num_arms)
        self.distributions = self.environment.get_distributions()
        self.max_reward = Environment.MAX_REWARD

        self.agent = experiment_parameters['agent']['type'](
            num_arms=self.num_arms,
            num_turns=self.num_turns,
            value_function=experiment_parameters['agent']['value_function'],
            initial_values=experiment_parameters['agent']['initial_values'],
            policy=experiment_parameters['agent']['policy']
        )

    def print_distributions(self):
        table = PrettyTable(['Probability/Bandits'] + ['Bandit #{}'.format(idx) for idx in range(self.num_arms)])

        for reward in Environment.REWARDS:
            row = ['probability of {}'.format(reward.name)]
            for bandit_idx in range(self.num_arms):
                row.append(round(self.distributions[bandit_idx][reward.name]['probability'], 5))
            table.add_row(row)
        print(table)

    def commence(self):
        self.agent.commence()

    def conclude(self):
        print('=' * 80)
        print('True Distribution:')
        self.print_distributions()
        print('=' * 80)
        print()

        print('=' * 80)
        print('Final Stats:')
        self.agent.print_stats_at_timestamp(self.num_turns)
        print('=' * 80)
        print()

        print('=' * 80)
        print('History:')
        self.agent.print_events_history_till_timestamp(self.num_turns - 1)
        print('=' * 80)
        print()


experiment_parameters = {
    'num_turns': 5,
    'num_arms': 3,
    'environment': Environment,
    'agent': {
        'type': Agent,
        'value_function': Agent.VALUE_FUNCTION.EXPECTED_REWARD,
        'initial_values': [0] * 3,
        'policy': Agent.POLICY.USER_DEFINED
    }
}

experiment = Experiment(experiment_parameters)
experiment.commence()
experiment.conclude()
