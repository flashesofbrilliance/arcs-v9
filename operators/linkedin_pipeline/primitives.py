"""
ARCS Derivative Primitives
Production-ready trend detection and wave analysis
"""

import numpy as np
from typing import List
from pydantic import BaseModel


class FirstDerivativeAtom:
    """Velocity Primitive: Rate of change detection"""
    
    def __init__(self, signal_data: np.ndarray, time_window: float = 1.0):
        self.signal = np.array(signal_data)
        self.dt = time_window
    
    def calc(self) -> np.ndarray:
        """Calculate velocity (first derivative)"""
        return np.gradient(self.signal, self.dt)
    
    def threshold_detect(self, threshold: float = 0.1) -> np.ndarray:
        """Detect emerging trends above threshold"""
        velocity = self.calc()
        return velocity > threshold


class SecondDerivativeAtom:
    """Acceleration Primitive: Inflection point detection"""
    
    def __init__(self, signal_data: np.ndarray, time_window: float = 1.0):
        self.signal = np.array(signal_data)
        self.dt = time_window
    
    def calc(self) -> np.ndarray:
        """Calculate acceleration (second derivative)"""
        velocity = np.gradient(self.signal, self.dt)
        acceleration = np.gradient(velocity, self.dt)
        return acceleration
    
    def inflection_points(self) -> np.ndarray:
        """Find zero crossings of acceleration (inflection points)"""
        accel = self.calc()
        return np.where(np.diff(np.sign(accel)))[0]


class ThirdDerivativeAtom:
    """Jerk Primitive: rate of change of acceleration. Detects that the
    curve's acceleration is itself falling — the earliest available
    warning that deceleration is approaching, available before
    acceleration crosses zero (which is what DeceleratorAtom waits for)."""

    def __init__(self, signal_data: np.ndarray, time_window: float = 1.0):
        self.signal = np.array(signal_data)
        self.dt = time_window

    def calc(self) -> np.ndarray:
        """Calculate jerk (third derivative)"""
        velocity = np.gradient(self.signal, self.dt)
        acceleration = np.gradient(velocity, self.dt)
        jerk = np.gradient(acceleration, self.dt)
        return jerk


class DeceleratorAtom:
    """Cooling Detection Primitive: Trend retirement trigger"""
    
    def __init__(self, signal_data: np.ndarray, time_window: float = 1.0):
        self.fd = FirstDerivativeAtom(signal_data, time_window)
        self.sd = SecondDerivativeAtom(signal_data, time_window)
    
    def is_decelerating(self) -> np.ndarray:
        """Detect deceleration (positive velocity, negative acceleration)"""
        velocity = self.fd.calc()
        acceleration = self.sd.calc()
        return (velocity > 0) & (acceleration < 0)
    
    def severity(self) -> np.ndarray:
        """Calculate deceleration severity: -a(t)/v(t)"""
        v = self.fd.calc()
        a = self.sd.calc()
        with np.errstate(divide='ignore', invalid='ignore'):
            sev = -a / v
            sev[~np.isfinite(sev)] = 0
        return sev


class TrendSurfingMolecule:
    """Compound Molecule: Optimal trend entry/exit detection"""

    def __init__(self, signal: np.ndarray, dt: float = 1.0):
        self.fd = FirstDerivativeAtom(signal, dt)
        self.sd = SecondDerivativeAtom(signal, dt)
        self.td = ThirdDerivativeAtom(signal, dt)
        self.dec = DeceleratorAtom(signal, dt)

    def optimal_entry_points(self, v_threshold: float = 0.1,
                            a_threshold: float = 0.01) -> np.ndarray:
        """Detect optimal entry points"""
        v = self.fd.calc()
        a = self.sd.calc()
        return (v > v_threshold) & (a > a_threshold)

    def exit_points(self) -> np.ndarray:
        """Detect optimal exit points (deceleration detected)"""
        return self.dec.is_decelerating()

    def pre_peak_warning(self, j_threshold: float = 0.0) -> np.ndarray:
        """Detect the approach of a peak before deceleration is visible
        in acceleration alone. Fires while still accelerating (a > 0,
        still climbing the curve) but jerk has turned negative (the
        acceleration itself is already falling) — strictly earlier than
        exit_points(), which waits for acceleration to cross zero."""
        a = self.sd.calc()
        j = self.td.calc()
        return (a > 0) & (j < j_threshold)


# Pydantic models for API
class VelocityResponse(BaseModel):
    velocity: List[float]
    emerging_trends: List[bool]
    threshold: float


class AccelerationResponse(BaseModel):
    acceleration: List[float]
    inflection_points: List[int]
    peaks: List[int]
    valleys: List[int]


class DecelerationResponse(BaseModel):
    is_decelerating: List[bool]
    severity: List[float]
    exit_signals: List[int]


class TrendSignalsResponse(BaseModel):
    entry_points: List[int]
    exit_points: List[int]
    confidence: List[float]
    trend_strength: List[float]
