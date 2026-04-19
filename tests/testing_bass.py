import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt

# Load the bass stem
bass, sr = sf.read('../data/output/a_thousand_years/stems/htdemucs/a_thousand_years/bass.wav')

# Check if there's actually audio content
print(f"Sample rate: {sr}")
print(f"Duration: {len(bass) / sr:.2f} seconds")
print(f"Max amplitude: {np.max(np.abs(bass)):.6f}")
print(f"RMS energy: {np.sqrt(np.mean(bass**2)):.6f}")

# Quick playability check
if np.max(np.abs(bass)) < 0.001:
    print("⚠️  Bass stem appears to be silent or very quiet")
else:
    print("✓ Bass stem has content")

plt.figure(figsize=(12, 4))
plt.plot(bass[:sr*10])  # First 10 seconds
plt.title("Bass waveform")
plt.show()