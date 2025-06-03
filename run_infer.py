#!/usr/bin/env python3
import argparse
import yaml
import json
import soundfile as sf
from infer import Infer
from utils.hparams import set_hparams
import infer, inspect
print(">>> infer.py körs från:", inspect.getsourcefile(infer))
print(">>> metoder i Infer:", [m for m in dir(infer.Infer) if not m.startswith("__")])


def main():
    p = argparse.ArgumentParser(description="Generera sång med DiffSinger-ONNX-Infer")
    p.add_argument('-c','--config',  required=True, help='Path to settings.yaml')
    p.add_argument('-i','--input',   help='(valfritt) Path to override input_sequence i settings.yaml')
    p.add_argument('-o','--output',  required=True, help='Output WAV-filename, t.ex. demo.wav')
    args = p.parse_args()

    # Läs in hyperparametrar
    hparams = set_hparams(args.config)

    # Om användaren skickar in en egen JSON-input
    if args.input:
        hparams['input_sequence'] = args.input

    # Ladda indatafilen
    with open(hparams['input_sequence'], 'r', encoding='utf-8') as f:
        inp = json.load(f)

    # Skapa Infer-instans
    infer = Infer(hparams)

    # Kör inferens
    print("▶ Loading model…")
    wav = infer.infer_once(inp)

    # Spara
    sr = hparams.get('audio_sample_rate', 44100)
    sf.write(args.output, wav, sr)
    print(f"✔ Wrote {args.output} @ {sr} Hz")

if __name__ == '__main__':
    main()
