from __future__ import annotations

"""
ARCS Core Atomic Primitives

Implements the five atomic primitives for signal and decision processing:
- FirstDerivative
- SecondDerivative
- WaveDiffusion
- PhaseCancel
- Decelerator

All classes are typed and validated via Pydantic. These are intentionally
lightweight, composable building blocks suitable for production pipelines.
"""

from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np
from pydantic import BaseModel, Field, validator
from scipy.ndimage import gaussian_filter1d


class FirstDerivative(BaseModel):
    """Numerical first derivative using central differences.

    Attributes
    ----------
    spacing: float
        Sampling interval between points.
    order: int
        Edge order passed to numpy.gradient.
    """

    spacing: float = Field(default=1.0, gt=0)
    order: int = Field(default=2, ge=1, le=2)

    def apply(self, data: Sequence[float]) -> np.ndarray:
        """Compute the first derivative.

        Parameters
        ----------
        data: Sequence[float]
            The input scalar series.

        Returns
        -------
        np.ndarray
            First derivative with same length as input.
        """
        arr = np.asarray(data, dtype=float)
        if arr.ndim != 1:
            raise ValueError("FirstDerivative expects a 1D series")
        return np.gradient(arr, self.spacing, edge_order=self.order)


class SecondDerivative(BaseModel):
    """Numerical second derivative via successive gradients."""

    spacing: float = Field(default=1.0, gt=0)
    order: int = Field(default=2, ge=1, le=2)

    def apply(self, data: Sequence[float]) -> np.ndarray:
        arr = np.asarray(data, dtype=float)
        if arr.ndim != 1:
            raise ValueError("SecondDerivative expects a 1D series")
        first = np.gradient(arr, self.spacing, edge_order=self.order)
        return np.gradient(first, self.spacing, edge_order=self.order)


class WaveDiffusion(BaseModel):
    """Gaussian diffusion (smoothing) to attenuate high-frequency noise.

    Attributes
    ----------
    sigma: float
        Standard deviation for Gaussian kernel, in samples.
    mode: str
        Boundary handling mode.
    """

    sigma: float = Field(default=1.0, gt=0)
    mode: str = Field(default="nearest")

    def apply(self, data: Sequence[float]) -> np.ndarray:
        arr = np.asarray(data, dtype=float)
        if arr.ndim != 1:
            raise ValueError("WaveDiffusion expects a 1D series")
        return gaussian_filter1d(arr, sigma=self.sigma, mode=self.mode)


class PhaseCancel(BaseModel):
    """Phase cancellation by notching targeted frequency bands in FFT domain.

    Attributes
    ----------
    sample_rate: float
        Sampling rate (Hz) for interpreting frequency bins.
    targets: List[float]
        Frequencies (Hz) to attenuate.
    bandwidth: float
        Half-width (Hz) around each target to notch.
    attenuation: float
        Linear attenuation factor in [0, 1], where 0 fully cancels.
    """

    sample_rate: float = Field(default=1.0, gt=0)
    targets: List[float] = Field(default_factory=list)
    bandwidth: float = Field(default=0.0, ge=0)
    attenuation: float = Field(default=0.0, ge=0.0, le=1.0)

    @validator("targets", each_item=True)
    def _non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Target frequencies must be non-negative")
        return v

    def apply(self, data: Sequence[float]) -> np.ndarray:
        arr = np.asarray(data, dtype=float)
        if arr.ndim != 1:
            raise ValueError("PhaseCancel expects a 1D series")
        n = arr.size
        freqs = np.fft.rfftfreq(n, d=1.0 / self.sample_rate)
        spectrum = np.fft.rfft(arr)
        mask = np.ones_like(freqs, dtype=float)

        if self.targets:
            for f0 in self.targets:
                band = (np.abs(freqs - f0) <= self.bandwidth)
                mask[band] *= self.attenuation

        spectrum *= mask
        filtered = np.fft.irfft(spectrum, n=n)
        return filtered


class Decelerator(BaseModel):
    """Decelerate changes via exponential moving average (EMA).

    This primitive reduces the velocity of changes to stabilize downstream
    decision systems without introducing excessive lag when alpha is set
    appropriately.

    Attributes
    ----------
    alpha: float
        Smoothing factor in (0, 1]. Higher is less deceleration.
    warm_start: Optional[float]
        Optional initial value; defaults to the first sample.
    """

    alpha: float = Field(default=0.2, gt=0.0, le=1.0)
    warm_start: Optional[float] = None

    def apply(self, data: Sequence[float]) -> np.ndarray:
        arr = np.asarray(data, dtype=float)
        if arr.ndim != 1:
            raise ValueError("Decelerator expects a 1D series")
        if arr.size == 0:
            return arr
        ema = np.empty_like(arr)
        ema[0] = arr[0] if self.warm_start is None else float(self.warm_start)
        a = self.alpha
        for i in range(1, arr.size):
            ema[i] = a * arr[i] + (1 - a) * ema[i - 1]
        return ema

