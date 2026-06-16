# arcs_kinematics.py
# ARCS v1.3 - The Unified Law of Coherence
# Production Grade Kinematic Manifold (Orders 1-12)
# From Classical Mechanics (1-3) to Quantum Flow (11-12).

import numpy as np
from scipy.special import gamma
from typing import Dict

class KinematicManifold:
    """
    The Engine of Higher-Order Motion.
    Calculates the full 12-dimensional kinematic signature of any signal.
    
    Spectrum:
    [1-3]   Classical:   Velocity, Acceleration, Jerk
    [4-6]   Chaotic:     Snap, Crackle, Pop
    [7-8]   Control:     Lock, Drop
    [9-10]  Ballistic:   Shot, Relevé (Peak Tension)
    [11]    Yielding:    Plié (Lattice / Beta-Derivative)
    [12]    Unified:     Élevé (Superionic / M-Truncated)
    """
    
    def __init__(self, signal: np.ndarray, dt: float = 1.0):
        self.signal = signal
        self.dt = dt
        # Cache to store intermediate derivatives for efficiency
        self._cache: Dict[int, np.ndarray] = {0: signal}

    def _recursive_diff(self, n: int) -> np.ndarray:
        """
        Recursively calculates standard integer-order derivatives (1-10).
        Uses central difference (np.gradient) for numerical stability.
        """
        if n in self._cache:
            return self._cache[n]
        
        # Get (n-1)th derivative
        prev_deriv = self._recursive_diff(n - 1)
        
        # Compute nth derivative
        curr_deriv = np.gradient(prev_deriv, self.dt)
        
        # Cache and return
        self._cache[n] = curr_deriv
        return curr_deriv

    # --- CLASSICAL REGIME (1-3) ---
    def velocity(self) -> np.ndarray: return self._recursive_diff(1)
    def acceleration(self) -> np.ndarray: return self._recursive_diff(2)
    def jerk(self) -> np.ndarray: return self._recursive_diff(3)

    # --- CHAOTIC REGIME (4-6) ---
    def snap(self) -> np.ndarray: return self._recursive_diff(4)
    def crackle(self) -> np.ndarray: return self._recursive_diff(5)
    def pop(self) -> np.ndarray: return self._recursive_diff(6)

    # --- CONTROL REGIME (7-8) ---
    def lock(self) -> np.ndarray: return self._recursive_diff(7)
    def drop(self) -> np.ndarray: return self._recursive_diff(8)

    # --- BALLISTIC REGIME (9-10) ---
    def shot(self) -> np.ndarray: return self._recursive_diff(9)
    
    def releve(self) -> np.ndarray: 
        """
        10th Derivative: Relevé (Peak Tension).
        The maximum static hold of the system.
        """
        return self._recursive_diff(10)

    # --- TRANSCENDENT REGIME (11-12) ---
    def plie(self, beta: float = 0.9) -> np.ndarray:
        """
        11th Derivative: Plié (Lattice / Yield).
        
        Logic: The Beta-Derivative.
        Instead of pushing harder (d/dt), we 'soften' the time coordinate itself.
        This represents the 'Yield' where structure absorbs energy.
        
        Formula: D_beta = d/dt_effective, where dt_effective scales with history.
        """
        # Base force is the 10th derivative (Relevé)
        base_signal = self.releve() 
        
        # Time vector
        t = np.arange(len(self.signal)) * self.dt
        
        # Scaling Factor (The Yield)
        # As beta approaches 1, it behaves Newtonian.
        # As beta decreases, time 'stiffens' or 'yields' (depending on perspective).
        gamma_val = gamma(beta)
        # Avoid division by zero at t=0 by adding epsilon if needed, 
        # but the formula (t + const) is safe.
        scale_factor = (t + 1.0/gamma_val)**(1.0 - beta)
        
        # Effective dt (Softened Time)
        dt_effective = self.dt * scale_factor
        
        # Calculate gradient relative to softened time
        grad = np.gradient(base_signal)
        
        # Result is the Plié: The Yielding Force
        return grad / dt_effective

    def eleve(self, alpha: float = 0.5) -> np.ndarray:
        """
        12th Derivative: Élevé (Superionic / Flow).
        
        Logic: The M-Truncated Derivative.
        It unifies the structure (Relevé/Plié) with flow.
        We model this as a 'Conductive' derivative where the flow is 
        reinforced by the signal's presence (Self-Reinforcing).
        
        Formula: D_M = D_standard * Weight(Signal_Intensity)
        """
        # We start with the raw 11th order change (The flow out of Plié)
        # Note: We use the standard 11th here as the 'potential' flow
        raw_flow = self._recursive_diff(11)
        
        # The Superionic Weight
        # If the signal is strong (High Pressure/Presence), conductivity increases.
        # This is the 'Black Ice' effect.
        conductivity = 1.0 + alpha * np.abs(self.signal)
        
        # Result is the Élevé: The Superionic Flow
        return raw_flow * conductivity

    def analyze(self) -> Dict[str, np.ndarray]:
        """Returns the full 12-dimensional kinematic signature."""
        return {
            "01_Velocity": self.velocity(),
            "02_Acceleration": self.acceleration(),
            "03_Jerk": self.jerk(),
            "04_Snap": self.snap(),
            "05_Crackle": self.crackle(),
            "06_Pop": self.pop(),
            "07_Lock": self.lock(),
            "08_Drop": self.drop(),
            "09_Shot": self.shot(),
            "10_Releve": self.releve(),
            "11_Plie": self.plie(),
            "12_Eleve": self.eleve()
        }
