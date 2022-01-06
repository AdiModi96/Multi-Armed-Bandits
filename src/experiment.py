from environments import MultiArmedStaticBinaryRewardsBanditEnvironment as Environment
from agents import StaticBinaryRewardsAgent as Agent
from utils import clear_terminal
from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec
from prettytable import PrettyTable
from datetime import datetime
import paths
import os


class Experiment:

    def __init__(self, experiment_parameters):
        self.id = experiment_parameters['id']
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

    def save_plots(self, plots_folder_path, stats_history, events_history):
        max_reward_over_time = [Environment.MAX_REWARD] * self.num_turns
        reward_names = [reward.name for reward in Environment.REWARDS]
        all_bandits_reward_over_time = [events_history[t]['reward'].value for t in range(self.num_turns)]
        all_bandits_expected_reward_over_time = []
        all_bandits_value_over_time = []
        all_bandits_estimated_distribution = []
        all_bandits_distributions = []
        all_bandits_num_times_acted = []

        for bandit_idx in range(self.num_arms):
            all_bandits_expected_reward_over_time.append(
                [stats_history[t + 1][bandit_idx]['expected_reward'] for t in range(self.num_turns)]
            )
            all_bandits_value_over_time.append(
                [stats_history[t][bandit_idx]['value'] for t in range(self.num_turns)]
            )

            num_times_acted = stats_history[self.num_turns][bandit_idx]['num_times_acted']
            all_bandits_num_times_acted.append(num_times_acted)
            estimated_distribution = []
            distribution = []

            for reward_name in reward_names:
                estimated_distribution.append(0 if num_times_acted == 0 else stats_history[self.num_turns][bandit_idx][
                                                                                 'num_of_{}'.format(
                                                                                     reward_name)] / num_times_acted)
                distribution.append(self.distributions[bandit_idx][reward_name]['probability'])

            all_bandits_estimated_distribution.append(estimated_distribution)
            all_bandits_distributions.append(distribution)

        figure = plt.figure(num='individual_bandit', figsize=(15, 10), constrained_layout=True)
        plt.rc('axes', axisbelow=True)
        grid_spec = GridSpec(3, 4, figure=figure)

        for bandit_idx in range(self.num_arms):
            figure.suptitle('Bandit {}'.format(bandit_idx))
            expected_reward_over_time_subplot_axes = figure.add_subplot(grid_spec[0:2, :])

            plt.title('Stats Over Time'.format(bandit_idx))
            plt.grid()
            expected_reward_over_time_subplot_axes.plot(
                ['t={}'.format(t) for t in range(self.num_turns)],
                max_reward_over_time,
                label='Max Reward',
                marker='o',
                linewidth=3
            )
            expected_reward_over_time_subplot_axes.plot(
                ['t={}'.format(t) for t in range(self.num_turns)],
                all_bandits_expected_reward_over_time[bandit_idx],
                label='Expected Reward Over Time',
                marker='o',
                linestyle='dashed',
                alpha=0.9,
                linewidth=3
            )
            expected_reward_over_time_subplot_axes.plot(
                ['t={}'.format(t) for t in range(self.num_turns)],
                all_bandits_value_over_time[bandit_idx],
                label='Value Over Time',
                marker='o',
                linestyle='dashed',
                alpha=0.8,
                linewidth=2
            )

            expected_reward_over_time_subplot_axes.set_ylim([-0.1, self.environment.MAX_REWARD * 1.1])
            plt.xlabel('- Time →')
            plt.ylabel('- Expected Reward →')
            expected_reward_over_time_subplot_axes.legend()

            estimated_distribution_subplot_axes = figure.add_subplot(grid_spec[2, 1])
            plt.title('Estimated Distribution'.format(bandit_idx))
            estimated_distribution_subplot_axes.grid()
            estimated_distribution_subplot_axes.bar(reward_names, all_bandits_estimated_distribution[bandit_idx],
                                                    color='orange')
            estimated_distribution_subplot_axes.set_ylim([0, 1.1])
            for i in range(len(reward_names)):
                estimated_distribution_subplot_axes.text(
                    i - 0.1,
                    0.1,
                    round(all_bandits_estimated_distribution[bandit_idx][i], 3),
                    fontweight='bold'
                )
            plt.ylabel('- Probability →')

            distribution_subplot_axes = figure.add_subplot(grid_spec[2, 2])
            plt.title('True Distribution'.format(bandit_idx))
            distribution_subplot_axes.grid()
            distribution_subplot_axes.bar(reward_names, all_bandits_distributions[bandit_idx], color='green')
            distribution_subplot_axes.set_ylim([0, 1.1])
            for i in range(len(reward_names)):
                distribution_subplot_axes.text(
                    i - 0.1,
                    0.1,
                    round(all_bandits_distributions[bandit_idx][i], 3),
                    fontweight='bold'
                )
            plt.ylabel('- Probability →')

            file_name = 'bandit_{}.png'.format(bandit_idx)
            file_path = os.path.join(plots_folder_path, file_name)

            plt.savefig(file_path, dpi=450)
            plt.clf()

        figure = plt.figure(num='expected_reward_all_bandits', figsize=(15, 10), constrained_layout=True)
        grid_spec = GridSpec(3, self.num_arms, figure=figure)

        reward_over_time_subplot_axes = figure.add_subplot(grid_spec[0, :])
        plt.title('Reward Over Time')
        plt.grid()
        plt.xlabel('- Time →')
        plt.ylabel('- Expected Reward →')
        reward_over_time_subplot_axes.plot(
            ['t={}'.format(t) for t in range(self.num_turns)],
            all_bandits_reward_over_time,
            marker='o',
            linestyle='dashed',
            alpha=0.9,
            linewidth=3
        )
        reward_over_time_subplot_axes.set_ylim([-0.1, self.environment.MAX_REWARD * 1.1])

        expected_reward_over_time_subplot_axes = figure.add_subplot(grid_spec[1, :])
        plt.title('Expected Reward Over Time')
        plt.grid()
        plt.xlabel('- Time →')
        plt.ylabel('- Expected Reward →')
        expected_reward_over_time_subplot_axes.set_ylim([-0.1, self.environment.MAX_REWARD * 1.1])

        value_over_time_subplot_axes = figure.add_subplot(grid_spec[2, :])
        plt.title('Value Over Time')
        plt.grid()
        plt.xlabel('- Time →')
        plt.ylabel('- Value →')
        value_over_time_subplot_axes.set_ylim([-0.1, self.environment.MAX_REWARD * 1.1])

        for bandit_idx in range(self.num_arms):

            expected_reward_over_time_subplot_axes.plot(
                ['t={}'.format(t) for t in range(self.num_turns)],
                all_bandits_expected_reward_over_time[bandit_idx],
                label='Bandit {}'.format(bandit_idx),
                marker='o',
                linestyle='dashed',
                alpha=0.9,
                linewidth=3
            )

            value_over_time_subplot_axes.plot(
                ['t={}'.format(t) for t in range(self.num_turns)],
                all_bandits_value_over_time[bandit_idx],
                label='Bandit {}'.format(bandit_idx),
                marker='o',
                linestyle='dashed',
                alpha=0.9,
                linewidth=3
            )

        expected_reward_over_time_subplot_axes.plot(
            ['t={}'.format(t) for t in range(self.num_turns)],
            max_reward_over_time,
            label='Max Reward',
            marker='o',
            linewidth=3
        )

        expected_reward_over_time_subplot_axes.legend()
        value_over_time_subplot_axes.legend()

        file_name = 'all_bandits_expected_reward_over_time.png'
        file_path = os.path.join(plots_folder_path, file_name)

        plt.savefig(file_path, dpi=450)

    def commence(self):
        self.agent.commence()

    def conclude(self):
        clear_terminal()
        print('Concluding the experiment...')

        outputs_folder_path = os.path.join(paths.experiments_folder_path, self.id)
        if not os.path.isdir(outputs_folder_path):
            os.makedirs(outputs_folder_path)

        plots_folder_path = os.path.join(outputs_folder_path, 'plots')
        if not os.path.isdir(plots_folder_path):
            os.makedirs(plots_folder_path)

        stats_history = self.agent.get_stats_history()
        events_history = self.agent.get_events_history()

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

        print('Saving plots ...')
        self.save_plots(plots_folder_path, stats_history, events_history)
        print()

        print('Experiment concluded!')


experiment_parameters = {
    'id': datetime.now().strftime('%Y-%m-%d_%H-%m-%s'),
    'num_turns': 10,
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
