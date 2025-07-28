"""
Performance estimation utilities.
"""
from nexapod.descriptor import JobDescriptor

def estimate_flops(desc: JobDescriptor) -> float:
    """Return the compute estimate from job descriptor."""
    return desc.compute_estimate

def estimate_time(desc: JobDescriptor, hardware_flops: float) -> float:
    """Estimate execution time in seconds given hardware performance."""
    flops = estimate_flops(desc)
    return flops / hardware_flops
