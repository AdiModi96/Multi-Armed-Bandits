from environments import MultiArmedStaticBinaryRewardsBanditEnvironment as Environment
from prettytable import PrettyTable
from utils import clear_terminal
import time
from enum import Enum


class StaticBinaryRewardsAgent:
    class VALUE_FUNCTION(Enum):
        EXPECTED_REWARD = 0

    class POLICY(Enum):
        USER_DEFINED = 0

    def __init__(self, num_arms, num_turns, value_function, initial_values, policy):
        self.num_arms = num_arms
        self.num_turns = num_turns

        self.environment = Environment(num_arms=num_arms)

        self.value_function = value_function
        self.initial_values = initial_values

        self.policy = policy

        self.stats_history = []
        self.events_history = []

    def get_stats_history(self):
        return self.stats_history

    def get_events_history(self):
        return self.events_history

    def print_stats_at_timestamp(self, timestamp):
        stats = self.stats_history[timestamp]

        table = PrettyTable(['Metrics/Bandits'] + ['Bandit {}'.format(idx) for idx in range(self.num_arms)])
        for metric in stats[0].keys():
            row = [metric]
            for bandit_idx in range(self.num_arms):
                row.append(round(stats[bandit_idx][metric], 5))
            table.add_row(row)
        print(table)

    def print_events_history_till_timestamp(self, timestamp):
        table = PrettyTable(['Timestamp'] + ['Bandit {}'.format(idx) for idx in range(self.num_arms)])
        for t in range(timestamp + 1):
            table.add_row(
                ['t={}'.format(str(t).zfill(3))] + \
                [(self.events_history[t]['reward'] if bandit_idx == self.events_history[t]['choice'] else '---') for
                 bandit_idx in range(self.num_arms)]
            )
        print(table)

    def get_choice(self):
        choice = None
        if self.policy == StaticBinaryRewardsAgent.POLICY.USER_DEFINED:
            print('Bandit options: {}'.format([bandit_idx for bandit_idx in range(self.num_arms)]))
            while True:
                choice = int(input('Enter your choice of bandit: '))
                if choice >= 0 and choice < self.num_arms:
                    break
                else:
                    print('Enter a valid option')
        else:
            print('Enter a valid option')
        return choice

    def commence(self):
        timestamp = 0
        bandit_stats = []
        for bandit_idx in range(self.num_arms):
            bandit_stat = {
                'num_times_acted': 0,
                'expected_reward': 0,
                'value': self.initial_values[bandit_idx]
            }
            for reward in Environment.REWARDS:
                bandit_stat['num_of_{}'.format(reward.name)] = 0

            bandit_stats.append(bandit_stat)
        self.stats_history.append(bandit_stats)

        while timestamp < self.num_turns:
            clear_terminal()

            print('-' * 80)
            print('Timestamp: {} / {}'.format(timestamp, self.num_turns - 1))
            print('-' * 80)

            if timestamp < 0:
                print('Timestamp cannot be negative, moving to timestamp 0 ...')
                timestamp = 0
                time.sleep(1)
                continue
            elif timestamp < len(self.events_history):
                self.print_stats_at_timestamp(timestamp)
                print()
                self.print_events_history_till_timestamp(timestamp)
            elif timestamp == len(self.events_history):
                self.print_stats_at_timestamp(timestamp)
                print()

                choice = self.get_choice()
                reward = self.environment.act(choice)

                new_stats = []

                if self.value_function == StaticBinaryRewardsAgent.VALUE_FUNCTION.EXPECTED_REWARD:
                    for bandit_idx in range(self.num_arms):
                        if bandit_idx == choice:

                            bandit_stats = self.stats_history[-1][choice].copy()
                            bandit_stats['num_times_acted'] += 1
                            bandit_stats['num_of_{}'.format(reward.name)] += 1

                            bandit_stats['expected_reward'] += (reward.value - bandit_stats['expected_reward']) / (
                                bandit_stats['num_times_acted'])
                            bandit_stats['value'] += (reward.value - bandit_stats['value']) / (
                                bandit_stats['num_times_acted'])

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

                self.print_events_history_till_timestamp(timestamp)
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
