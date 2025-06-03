import argparse
import os
import yaml
import pretty_midi
import json

def load_phonemes(config_path):
    """
    Läser dsconfig.yaml för att hitta phonemes-fil och returnerar en lista med phonem.
    """
    base_dir = os.path.dirname(config_path)
    cfg = yaml.safe_load(open(config_path, 'r', encoding='utf-8'))
    phoneme_file = cfg['phonemes']
    phoneme_path = os.path.join(base_dir, phoneme_file)
    with open(phoneme_path, 'r', encoding='utf-8') as f:
        phonemes = [line.strip() for line in f if line.strip()]
    return phonemes

def midi_to_json(midi_path, lyrics, item_name, spk_name, rest_token='SP'):
    """
    Konverterar MIDI + lyrics till DiffSinger JSON, tar med rest-token (default SP).
    Lyrics bör redan innehålla phonem- eller text-token i rätt ordning.
    """
    pm = pretty_midi.PrettyMIDI(midi_path)
    if not pm.instruments:
        raise ValueError("Ingen instrumentdata i MIDI-filen.")
    
    notes = sorted(pm.instruments[0].notes, key=lambda n: n.start)
    durations = [round(n.end - n.start, 4) for n in notes]
    
    note_tokens = [pretty_midi.note_number_to_name(n.pitch) for n in notes]
    text_chars = list(lyrics)
    
    # Om lyrics innehåller rest_token (t.ex. SP eller AP) så låt den vara i text_chars
    
    # Bygg JSON
    return {
        "text": "|".join(text_chars),
        "item_name": item_name,
        "spk_name": spk_name,
        "notes": "|".join(note_tokens),
        "notes_duration": "|".join(str(d) for d in durations)
    }

def main():
    parser = argparse.ArgumentParser(
        description="Generisk MIDI→JSON för DiffSinger-modeller"
    )
    parser.add_argument("--midi",      required=True, help="Sökväg till MIDI-fil")
    parser.add_argument("--lyrics",    required=True, help="Lyrics som inline-text (inkl SP/AP)")
    parser.add_argument("--item_name", required=True, help="Namn för ljudklippet")
    parser.add_argument("--spk_name",  required=True, help="Speaker/modellnamn")
    parser.add_argument("--config",    required=True, help="Sökväg till dsconfig.yaml")
    
    args = parser.parse_args()
    
    phonemes = load_phonemes(args.config)
    # Välj SP om funnen, annars första phonem som ej är PAD och ej bokstavlig phonem
    rest_token = 'SP' if 'SP' in phonemes else (phonemes[1] if len(phonemes)>1 else phonemes[0])
    
    result = midi_to_json(
        args.midi,
        args.lyrics,
        args.item_name,
        args.spk_name,
        rest_token=rest_token
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
