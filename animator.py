import time
import math

class SmoothAnimator:
    """
    iOS-like smooth spring/cubic-bezier animation helper for Tkinter / CustomTkinter.
    Uses exponential / cubic ease-out curves to interpolate values smoothly.
    """
    
    @staticmethod
    def ease_out_expo(t: float) -> float:
        """iOS standard decelerating spring-like curve."""
        return 1.0 if t >= 1.0 else 1.0 - math.pow(2.0, -10.0 * t)

    @staticmethod
    def ease_out_quint(t: float) -> float:
        return 1.0 - math.pow(1.0 - t, 5.0)

    @classmethod
    def animate(cls, widget, start_val: float, end_val: float, duration_ms: int = 240, steps: int = 20, update_callback=None, finished_callback=None):
        step_delay = max(10, duration_ms // steps)
        step_idx = 0

        def _step():
            nonlocal step_idx
            step_idx += 1
            progress = min(1.0, step_idx / steps)
            eased_progress = cls.ease_out_expo(progress)
            current_val = start_val + (end_val - start_val) * eased_progress

            if update_callback:
                update_callback(current_val)

            if step_idx < steps:
                widget.after(step_delay, _step)
            else:
                if update_callback:
                    update_callback(end_val)
                if finished_callback:
                    finished_callback()

        _step()
