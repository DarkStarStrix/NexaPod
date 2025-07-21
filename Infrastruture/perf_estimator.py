from descriptor import JobDescriptor

def estimate_flops(desc: JobDescriptor) -> float:
    # simple heuristic or user‐provided metadata
    return desc.compute_estimate

