import logging
import sys

from keyarrange.pipeline import Pipeline



def main(input_path: str, output_dir: str) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s [%(name)s] %(message)s'))
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)

    pipeline = Pipeline(input_path, output_dir)
    arranged_midi_path = pipeline.run()
    print(f"Arranged MIDI saved at: {arranged_midi_path}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])