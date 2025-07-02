import argparse
from comms import CoordinatorClient
from profiles import get_node_profile
from executor import execute_job
from logger import log_result
import yaml
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.yaml')

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description='NEXAPod Client Node')
    parser.add_argument('command', choices=['join', 'run'], help='join: register node, run: poll and execute jobs')
    args = parser.parse_args()

    config = load_config()
    client = CoordinatorClient(config)

    if args.command == 'join':
        profile = get_node_profile()
        client.register_node(profile)
        print('Node registered with coordinator.')
    elif args.command == 'run':
        while True:
            job = client.poll_job()
            if job:
                result = execute_job(job)
                log_result(result, config)
                client.submit_result(result)

if __name__ == '__main__':
    main()

