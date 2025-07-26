from descriptor import JobDescriptor

def estimate_flops(desc: JobDescriptor) -> float:
    # simple heuristic or user‐provided metadata
    return desc.compute_estimate

def estimate_time(desc: JobDescriptor, hardware_flops: float) -> float:
    """Estimate execution time in seconds given the job descriptor and hardware flops."""
    flops = estimate_flops(desc)
    return flops / hardware_flops  # time in seconds
