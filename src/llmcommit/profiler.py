"""Simple profiler for performance analysis."""

import time
from typing import Dict, List


class SimpleProfiler:
    """Simple profiler to track execution times."""
    
    def __init__(self):
        self.timings: Dict[str, List[float]] = {}
        self.start_times: Dict[str, float] = {}
    
    def start(self, name: str):
        """Start timing a section."""
        self.start_times[name] = time.time()
    
    def end(self, name: str):
        """End timing a section."""
        if name in self.start_times:
            elapsed = time.time() - self.start_times[name]
            if name not in self.timings:
                self.timings[name] = []
            self.timings[name].append(elapsed)
            del self.start_times[name]
            return elapsed
        return 0.0
    
    def report(self) -> str:
        """Generate timing report."""
        lines = ["Performance Report:"]
        lines.append("-" * 40)
        
        total_time = sum(sum(times) for times in self.timings.values())
        
        for name, times in sorted(self.timings.items(), key=lambda x: sum(x[1]), reverse=True):
            avg_time = sum(times) / len(times)
            pct = (sum(times) / total_time * 100) if total_time > 0 else 0
            lines.append(f"{name:25} {avg_time:6.2f}s ({pct:5.1f}%)")
        
        lines.append("-" * 40)
        lines.append(f"{'Total':25} {total_time:6.2f}s")
        
        return "\n".join(lines)