import time
import argparse
import sys
from rich.console import Console
from rich.progress import Progress
from rich.logging import RichHandler
import logging

# Configure logging with RichHandler
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, show_path=False)]
)

log = logging.getLogger("rich")

console = Console()


def setup():
    """
    Download and set up the client Docker container.
    """
    console.print("[bold green]Starting NexaPod client setup...[/bold green]")
    with Progress() as progress:
        task = progress.add_task("[cyan]Downloading client container...", total=100)
        while not progress.finished:
            progress.update(task, advance=1)
            time.sleep(0.05)
    log.info("Client container 'nexapod/client:latest' downloaded.")
    log.info("Setup complete. Client is ready.")


def run(job_id: str):
    """
    Run a specific job in the client container.
    """
    log.info(f"Fetching job '{job_id}' from the server...")
    time.sleep(1)
    log.info(f"Executing job '{job_id}' in the client container...")
    with Progress() as progress:
        task = progress.add_task(f"[cyan]Running job {job_id}...", total=100)
        while not progress.finished:
            progress.update(task, advance=2)
            time.sleep(0.05)
    console.print(f"[bold green]Job '{job_id}' completed successfully.[/bold green]")


def start():
    """
    Start the client to listen for jobs from the server.
    """
    log.info("Starting NexaPod client worker...")
    log.info("Connecting to job server...")
    time.sleep(1)
    log.info("[bold green]Connected![/bold green] Waiting for jobs. Press Ctrl+C to exit.")
    try:
        while True:
            # In a real application, this would poll a server for jobs.
            time.sleep(5)
            log.info("Polling for new jobs...")
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Shutting down NexaPod client worker...[/bold yellow]")
        time.sleep(1)
        console.print("[bold red]Client stopped.[/bold red]")

def print_help():
    """Prints a simple help message for interactive mode."""
    console.print("\n[bold]Available commands:[/bold]")
    console.print("  [cyan]setup[/cyan]         - Download and set up the client Docker container.")
    console.print("  [cyan]run <job_id>[/cyan]  - Run a specific job in the client container.")
    console.print("  [cyan]start[/cyan]         - Start the client to listen for jobs. (Blocks session)")
    console.print("  [cyan]help[/cyan]          - Show this help message.")
    console.print("  [cyan]exit[/cyan]          - Exit the interactive session.\n")


def interactive_session():
    """Starts an interactive command-line session."""
    console.print("[bold cyan]Welcome to the NexaPod interactive CLI.[/bold cyan]")
    print_help()
    while True:
        try:
            command_line = console.input("[bold green]nexapod> [/bold green]").strip()
            if not command_line:
                continue

            parts = command_line.split()
            command = parts[0].lower()
            args = parts[1:]

            if command in ["exit", "quit"]:
                break
            elif command == "help":
                print_help()
            elif command == "setup":
                setup()
            elif command == "run":
                if not args:
                    log.error("The 'run' command requires a job_id. Usage: run <job_id>")
                else:
                    run(args[0])
            elif command == "start":
                start()
            else:
                log.error(f"Unknown command: '{command}'. Type 'help' for a list of commands.")

        except KeyboardInterrupt:
            # Catch Ctrl+C to break out of the loop
            break
        except Exception as e:
            log.error(f"An error occurred: {e}", extra={"markup": True})

    console.print("\n[bold yellow]Exiting NexaPod CLI.[/bold yellow]")


def main():
    # If arguments are passed, use argparse for non-interactive mode.
    # Otherwise, start the interactive session.
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="NexaPod CLI for client operations.")
        subparsers = parser.add_subparsers(dest="command", help="Available commands", required=True)

        # Setup command
        subparsers.add_parser("setup", help="Download and set up the client Docker container.")

        # Run command
        run_parser = subparsers.add_parser("run", help="Run a specific job in the client container.")
        run_parser.add_argument("job_id", type=str, help="The ID of the job to execute.")

        # Start command
        subparsers.add_parser("start", help="Start the client to listen for jobs from the server.")

        args = parser.parse_args()

        if args.command == "setup":
            setup()
        elif args.command == "run":
            run(args.job_id)
        elif args.command == "start":
            start()
    else:
        interactive_session()


if __name__ == "__main__":
    main()
