import os
from environments import MultiArmedStaticBinaryRewardsBanditEnvironment as Environment
from static_distribution_bandits import BinaryRewardsBandit as Bandit
from prettytable import PrettyTable
from os import system
import time
from enum import Enum


class StaticBinaryRewardsAgent:

    @staticmethod
    def clear_terminal():
        if os.name == 'nt':
            system('cls')
        elif os.name == 'posix':
            system('clear')
        else:
            print('Unknown operating system')

    class VALUE_FUNCTION(Enum):
        EXPECTED_REWARD = 0

    def __init__(self, num_arms=3, num_turns=10, value_function=VALUE_FUNCTION.EXPECTED_REWARD, initial_values=[0] * 3):
        self.num_arms = num_arms
        self.num_turns = num_turns
        self.environment = Environment(num_arms=num_arms)
        self.value_function = value_function

        self.initial_values = initial_values
        self.stats_history = []
        self.events_history = []

    def print_stats_table(self, timestamp):
        stats = self.stats_history[timestamp]

        table = PrettyTable(['Metrics/Bandits'] + ['Bandit #{}'.format(idx) for idx in range(self.num_arms)])
        for metric in stats[0].keys():
            row = [metric]
            for bandit_idx in range(self.num_arms):
                row.append(stats[bandit_idx][metric])
            table.add_row(row)
        print(table)

    def print_distributions(self):
        table = PrettyTable(['Probability/Bandits'] + ['Bandit #{}'.format(idx) for idx in range(self.num_arms)])

        distributions = self.environment.get_distributions()

        row = ['probability of success']
        for bandit_idx in range(self.num_arms):
            row.append(distributions[bandit_idx][Bandit.REWARDS.SUCCESS.name]['probability'])
        table.add_row(row)
        print(table)

    def print_history_table(self, timestamp):
        table = PrettyTable(['Timestamp'] + ['Bandit #{}'.format(idx) for idx in range(self.num_arms)])
        for t in range(timestamp + 1):
            table.add_row(
                ['t={}'.format(str(t).zfill(3))] + \
                [(self.events_history[t]['reward'] if bandit_idx == self.events_history[t]['choice'] else '---') for
                 bandit_idx in range(self.num_arms)]
            )
        print(table)

    def commence_experiment(self):

        timestamp = 0
        bandit_stats = []
        for bandit_idx in range(self.num_arms):
            bandit_stats.append(
                {
                    'num_times_acted': 0,
                    'num_of_positive_rewards': 0,
                    'num_of_negative_rewards': 0,
                    'expected_reward': 0,
                    'value': self.initial_values[bandit_idx]
                }
            )
        self.stats_history.append(bandit_stats)

        while timestamp < self.num_turns:
            StaticBinaryRewardsAgent.clear_terminal()

            print('-' * 80)
            print('Timestamp: {} / {}'.format(timestamp, self.num_turns))
            print('-' * 80)

            if timestamp < 0:
                print('Timestamp cannot be negative, moving to timestamp 0 ...')
                timestamp = 0
                time.sleep(1)
                continue
            elif timestamp < len(self.events_history):
                self.print_stats_table(timestamp)
                print()
                self.print_history_table(timestamp)
            elif timestamp == len(self.events_history):
                self.print_stats_table(timestamp)
                print()
                print('Bandit options: {}'.format([bandit_idx for bandit_idx in range(self.num_arms)]))
                while True:
                    choice = int(input('Enter your choice of bandit: '))
                    if choice >= 0 and choice < self.num_arms:
                        break
                    else:
                        print('Enter a valid option')
                reward = self.environment.act(choice)

                new_stats = []

                if self.value_function == StaticBinaryRewardsAgent.VALUE_FUNCTION.EXPECTED_REWARD:
                    for bandit_idx in range(self.num_arms):
                        if bandit_idx == choice:

                            bandit_stats = self.stats_history[-1][choice].copy()
                            bandit_stats['num_times_acted'] += 1
                            if reward.value == 0:
                                bandit_stats['num_of_negative_rewards'] += 1
                            elif reward.value == 1:
                                bandit_stats['num_of_positive_rewards'] += 1

                            bandit_stats['expected_reward'] += (reward.value - bandit_stats['expected_reward']) / (bandit_stats['num_times_acted'])
                            bandit_stats['value'] += (reward.value - bandit_stats['value']) / (bandit_stats['num_times_acted'])

                            new_stats.append(bandit_stats)
                        else:
                            new_stats.append(self.stats_history[-1][bandit_idx].copy())
                self.stats_history.append(new_stats)

                self.events_history.append(
                    {
                        'choice': choice,
                        'reward': reward
                    }
                )

                self.print_history_table(timestamp)

            print()

            while True:
                key = input(
                    'Enter "n" key to continue to the next timestamp or enter "p" to revisit the previous timestamp: '
                )
                key = key.lower()
                if key == 'n':
                    timestamp += 1
                    break
                elif key == 'p':
                    timestamp -= 1
                    break
                else:
                    print('Enter a valid option')

    def conclude_experiment(self):
        StaticBinaryRewardsAgent.clear_terminal()

        print('The experiment has concluded ...')
        print()

        print('The following were the true distributions: ')
        self.print_distributions()
        print()

        print('Final stats: ')
        self.print_stats_table(self.num_turns)
        print()

        print('History:')
        self.print_history_table(self.num_turns - 1)
        print()


parameters = {
    'num_arms': 3,
    'num_turns': 5,
    'value_function': StaticBinaryRewardsAgent.VALUE_FUNCTION.EXPECTED_REWARD,
    'initial_values': [0] * 3
}

print('The following are the experiment parameters')

agent = StaticBinaryRewardsAgent(**parameters)
agent.commence_experiment()
agent.conclude_experiment()
