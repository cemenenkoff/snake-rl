from agent import train_dqn
from environment import Snake
from plotting import plot_history
from gif_creator import GifBuilder
from pathlib import Path
from argparse import ArgumentParser
from datetime import datetime
import sys
import json

def parse_args():
    '''defines our CLI options'''
    parser = ArgumentParser(prog='Snake RL',
                            description='teach a neural network to play snake')
    parser.add_argument('-c', '--config', dest='config', required=False,
                        default='config.json',
                        help='path to the configuration file')
    return parser.parse_args()

def get_config(path:str):
    '''
    converts a JSON config file into a python dictionary
    '''
    with open(path) as json_file:
        return json.load(json_file)

def check_config(config:dict):
    '''
    checks a JSON config for required keys and value types
    '''
    req = {
        'project_root_dir':str,
        'human':bool,
        'name':str,
        'save_for_gif':bool,
        'make_gif':bool,
        'params':dict
    }
    req_params = {
        'epsilon':float,
        'gamma':float,
        'batch_size':int,
        'epsilon_min':float,
        'epsilon_decay':float,
        'learning_rate':float,
        'layer_sizes':list,
        'num_episodes':int,
        'max_steps':int,
        'state_definition_type':str
    }
    iterables = [
        (req, config),
        (req_params, config['params'])
    ]
    for codex, subdict in iterables:
        for k,v in codex.items():
            try:
                if not isinstance(subdict[k], v):
                    raise ValueError
            except KeyError:
                print(f'ERROR: missing required key {k}')
                sys.exit(1)
            except ValueError:
                print(f'ERROR: {k} is currently {type(subdict[k])} and should be {v}')
                sys.exit(1)
    return config

def main():
    args = parse_args()
    config = check_config(get_config(path=args.config))
    params = config['params'] # the main parameters for the agent
    project_root_dir = Path(config['project_root_dir'])
    figures_dir = project_root_dir/'figures' # main folder for figures

    # Name a folder to store the output of this run.
    ts = datetime.now().strftime('%a%b%d-%H%M%S')
    num_ep = params['num_episodes']
    bat_sz = params['batch_size']
    state_def = params["state_definition_type"]
    params_str = f'{state_def}-{num_ep}ep-{bat_sz}batch'
    instance_folder = f'{ts}-{params_str}'
    name = config['name']
    if isinstance(name, str) and name:
        instance_folder = f'{name}-{instance_folder}'

    if config['save_for_gif']:
        # If wanted, create folders to store the eps files for gif creation.
        eps_dir = figures_dir/instance_folder/'gif-build'/'eps'
        config['eps_dir'] = eps_dir
        eps_dir.mkdir(exist_ok=True, parents=True)

    env = Snake(config)
    # If we are just playing the game, no folders should be created.
    if config['human']:
        while True:
            env.run_game()

    if not config['human']:
        history = train_dqn(env, params)
        # If an agent plays, create a folder to store our learning curve graph.
        instance_dir = figures_dir/instance_folder
        instance_dir.mkdir(exist_ok=True, parents=True)
        plot_name = f'learning-curve-{params_str}.png'
        plot_history(history, outpath=instance_dir/plot_name, params=params)
    if config['make_gif']:
        png_dir = eps_dir.parent/'png'
        gif_name = f'training-montage-{params_str}.gif'
        bob_the_builder = GifBuilder(config['eps_dir'], png_dir)
        bob_the_builder.convert_eps_files()
        bob_the_builder.make_gif(outpath=figures_dir/instance_folder/gif_name)

if __name__ == '__main__':
    main()