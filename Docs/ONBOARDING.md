# NEXAPod Alpha: Contributor Onboarding

Welcome! This guide explains how to join the NEXAPod compute mesh by running a client "pod" on your local machine.

## Prerequisites

- **Docker:** You must have Docker installed and running.
- **A shell environment:** (e.g., Bash, Zsh, PowerShell with Git Bash).

## Step 1: Install the `nexapod` CLI

The `nexapod` script is the simplest way to interact with the network.

**For Linux/macOS:**
```bash
# Download the script (replace with the correct raw URL if needed)
curl -o nexapod https://raw.githubusercontent.com/kunya66/NexaPod/main/nexapod
# Make it executable
chmod +x nexapod
# Move it to a location in your PATH
sudo mv nexapod /usr/local/bin/
```

**For Windows:**
1.  Download the `nexapod` script.
2.  Place it in a directory that is included in your system's `PATH`.
3.  Ensure you run the commands from a shell that supports bash scripts (like Git Bash).

## Step 2: Configure Your Pod

The pod needs to know which coordinator server to connect to.

1.  Create a directory in your home folder named `.nexapod`:
    ```bash
    mkdir -p ~/.nexapod
    ```
2.  Inside that directory, create a file named `config.yaml`:
    ```yaml
    # File: ~/.nexapod/config.yaml
    coordinator_url: "http://YOUR_SERVER_IP:8000" # <-- Replace with the public IP of the coordinator
    poll_interval: 10 # Optional: seconds between polling for new jobs
    ```
This directory is securely mounted into the container as read-only.

## Step 3: Pull the Client Image

Download the official, read-only client image from the GitHub Container Registry:

```bash
nexapod --pull
```

## Step 4: Launch Your Pod

With configuration complete, start your pod to join the network:

```bash
nexapod
```

On startup, your pod will automatically:
1.  Log basic, non-personal system info (OS, CPU, GPU).
2.  Generate a unique identity hash from its own code.
3.  Register with the coordinator.
4.  Begin polling for compute jobs.

The pod runs in a **sandboxed, read-only environment**. To stop it, press `Ctrl+C`.

## Step 5: Monitor the Network

- **Dashboard**: The primary way to see your node and others is through the Streamlit dashboard, typically hosted by the coordinator.
- **Local Logs**: Your terminal will show logs from your running pod.

Congratulations, you are now a contributor to the NEXAPod compute mesh! 🎉
