import argparse
from comms import CoordinatorClient
from profiles import get_node_profile
from executor import execute_job
from logger import log_result
import yaml
import os
import json
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization
from prometheus_client import Counter, start_http_server

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.yaml')

# Prometheus metrics for client
jobs_polled_counter = Counter('nexapod_client_jobs_polled_total', 'Total number of jobs polled from server')
jobs_executed_success_counter = Counter('nexapod_client_job_success_total', 'Total number of successful job executions')
jobs_executed_failure_counter = Counter('nexapod_client_job_failure_total', 'Total number of failed job executions')

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description='NEXAPod Client Node')
    parser.add_argument('command', choices=['join', 'run'], help='join: register node, run: poll and execute jobs')
    args = parser.parse_args()

    config = load_config()
    # Start Prometheus metrics server
    start_http_server(9000)
    client = CoordinatorClient(config)

    if args.command == 'join':
        # Ensure private key exists or generate one
        key_path = os.path.expanduser(config['private_key_path'])
        os.makedirs(os.path.dirname(key_path), exist_ok=True)
        if not os.path.exists(key_path):
            key = Ed25519PrivateKey.generate()
            with open(key_path, 'wb') as f:
                f.write(key.private_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PrivateFormat.Raw,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            print(f"Generated new private key at {key_path}")
        else:
            with open(key_path, 'rb') as f:
                key = Ed25519PrivateKey.from_private_bytes(f.read())
        public_key_hex = key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        ).hex()
        # Prepare and sign node profile
        profile = get_node_profile()
        message = json.dumps(profile, sort_keys=True).encode()
        signature_hex = key.sign(message).hex()
        payload = {**profile, 'public_key': public_key_hex, 'signature': signature_hex}
        client.register_node(payload)
        print('Node registered with coordinator.')
    elif args.command == 'run':
        while True:
            job = client.poll_job()
            if job:
                jobs_polled_counter.inc()
                result = execute_job(job)
                # Metrics for execution outcome
                if result.get('status') == 'completed':
                    jobs_executed_success_counter.inc()
                else:
                    jobs_executed_failure_counter.inc()
                log_result(result, config)
                client.submit_result(result)

if __name__ == '__main__':
    main()
