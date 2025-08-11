# Initialize NexaPod core package

def descriptor():
    """
    Module for job descriptors.
    """
    from .descriptor import JobDescriptor
    return JobDescriptor


def cli():
    """
    Runs the CLI application.
    """
    from .main import main
    main()
