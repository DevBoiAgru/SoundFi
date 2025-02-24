import numpy as np
import sounddevice as sd
import datetime as dt
import time

# Constants
SAMPLERATE: int = 44100

BEEP_FREQUENCIES = {
    6800: 0,  # False
    7000: 1,  # True
    7300: 2,  # Start beep
    7500: 3,  # End beep
}

BIT_SAMPLES_SIZE = int(
    0.02 * SAMPLERATE
)  # Number of samples per bit "beep", (beep length * sample rate)
INPUT_DEVICE = sd.query_devices(  # Get default input device, could be a microphone or a virtual device
    None, "input"
)


# Global state variables
data = ""
running = True
started = False
start_time = 0


# Utility functions
def bits_to_bytes(bits: str):
    """
    Returns a generator that converts a string of 0s and 1s to a list of bytes.
    ### Warning: This function assumes that the input string length is a multiple of 8, make sure to verify before calling.
    """

    for i in range(0, len(bits), 8):
        byte = bits[i : i + 8]  # Get the next 8 bits as a string of 0s and 1s
        yield int(byte, 2)  # Convert the string of 0s and 1s to an integer


# Callback and data processing
def process_bit(bit: int) -> None:
    global data, running, started, start_time

    if bit < 2:  # Print the bits as they are received
        print(bit, end="", flush=True)

    if bit == 0:
        data += "0"
    elif bit == 1:
        data += "1"

    elif bit == 2:  # Start bit
        data = ""
        started = True
        print("Detected start bit, Recieving data...")
        start_time = time.time()

    elif bit == 3:  # End bit
        started = False
        print()
        print("Detected end bit, Stopping reading data...")
        print("-" * 10, "Stats:", "-" * 10)
        print("Data length:".ljust(20), len(data), "bits.")

        # Write data to file

        # Generate a unique filename since we dont know the filename
        now = dt.datetime.now()
        filename = f"out-{now:%Y-%m-%d-%H-%M-%S}"

        assert len(data) % 8 == 0, (
            f"Error: Data is not a multiple of 8 bits. Got {len(data)} bits."
        )

        with open(filename, "wb") as f:
            for byte in bits_to_bytes(data):
                f.write(bytes([byte]))

        print("Filename:".ljust(20), filename)

        time_taken = time.time() - start_time
        print("Time taken:".ljust(20), time_taken, "seconds.")
        print(
            "Average speed[b/s]:".ljust(20),
            (len(data) / 8) / time_taken,
            "bytes per second.",
        )
        print(
            "Average speed[kb/s]:".ljust(20),
            ((len(data) / 8) / time_taken) / 1000,
            "kilobytes per second.\n\n",
        )

        running = False


def callback(indata: np.ndarray, frames: int, time, status) -> None:
    global BEEP_FREQUENCIES, started

    # Perform FFT and get dominant frequency
    fft_result = np.fft.fft(indata[:, 0])
    frequencies = np.fft.fftfreq(frames, 1 / SAMPLERATE)
    magnitude = np.abs(fft_result)
    dominant_frequency = frequencies[np.argmax(magnitude)]

    # Detect what bit it is
    detected: int | None = None
    for freq, bit_type in BEEP_FREQUENCIES.items():
        if abs(dominant_frequency - freq) < 100:
            detected = bit_type
            break

    if detected is not None:
        if detected == 2 and not started:  # Start bit
            started = True
        if started:
            process_bit(detected)


if __name__ == "__main__":
    with sd.InputStream(
        device=INPUT_DEVICE.get("index"),
        samplerate=SAMPLERATE,
        callback=callback,
        blocksize=BIT_SAMPLES_SIZE,
    ) as stream:
        print("Stream started. Waiting for data.")
        while running:
            try:
                response = input()
                if response in ("", "q", "Q"):
                    break
            except KeyboardInterrupt:
                print("Exiting...")
                break
