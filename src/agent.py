import os
from environments import MultiArmedStaticBinaryRewardsBanditEnvironment as Environment
from prettytable import PrettyTable
from os import system
import time

class Experiment:

    @staticmethod
    def clear_terminal():
        if os.name == 'nt':
            system('cls')
        elif os.name == 'posix':
            system('clear')
        else:
            print('Unknown Operating System')

    def __init__(self, num_arms=3, num_turns=10):
        self.num_arms = num_arms
        self.num_turns = num_turns
        self.environment = Environment(num_arms=num_arms)

        self.history = []

    def print_history(self, timestamp):
        table = PrettyTable(['Timestamp'] + ['Bandit #{}'.format(idx) for idx in range(self.num_arms)])
        for t in range(timestamp + 1):
            table.add_row(
                ['t={}'.format(str(t).zfill(3))] + \
                [(self.history[t]['reward'] if bandit_idx == self.history[t]['choice'] else '---') for bandit_idx in range(self.num_arms)]
            )
        print(table)

    def commence(self):

        timestamp = 0
        while timestamp < self.num_turns:
            Experiment.clear_terminal()

            print('-' * 80)
            print('Timestamp: {} / {}'.format(timestamp, self.num_turns))
            print('-' * 80)

            if timestamp < 0:
                print('Timestamp cannot be negative, moving to timestamp 0 ...')
                timestamp = 0
                time.sleep(1)
                continue
            elif timestamp < len(self.history):
                self.print_history(timestamp)
            elif timestamp == len(self.history):
                print('Bandit options: {}'.format([bandit_idx for bandit_idx in range(self.num_arms)]))
                while True:
                    choice = int(input('Enter your choice of bandit: '))
                    if choice >= 0 and choice < self.num_arms:
                        break
                    else:
                        print('Enter a valid option')
                reward = self.environment.act(choice)

                self.history.append(
                    {
                        'choice': choice,
                        'reward': reward
                    }
                )

                self.print_history(timestamp)

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

    def conclude(self):
        pass

experiment = Experiment()
experiment.commence()
experiment.conclude()

