import os
import json
import librosa
import soundfile as sf

def preprocess_audio(rate=48000, length=3, filetype='wav', convert_mono=False, json_path='raw/data.json'):
    # Read the data.json file from the specified path
    with open(json_path, 'r') as f:
        data = json.load(f)

        # Retrieve speciesID and recordings, with fallbacks for alternate key names
    recordings = data.get('recordings', data.get('downloaded', []))
    speciesID = data.get('speciesID', data.get('species', []))

    new_recordings = []

    # Create the processed directory if it doesn't exist
    if not os.path.exists('processed'):
        os.makedirs('processed')

    # Process each recording
    for rec in recordings:
        species = rec['species']
        XCID = rec['id']
        path = rec['path']

        # Full path to the mp3 file
        audio_path = path

        # Load the audio file using librosa
        audio, sr = librosa.load(audio_path, sr=rate, mono=convert_mono)

        # Calculate the number of samples per segment
        segment_samples = int(length * rate)

        # Calculate the number of segments
        num_segments = len(audio) // segment_samples

        for i in range(num_segments):
            start_sample = i * segment_samples
            end_sample = min(start_sample + segment_samples, len(audio))

            # Extract the segment
            segment = audio[start_sample:end_sample]

            # Generate new filename
            species_dir = os.path.join('processed', str(species))
            if not os.path.exists(species_dir):
                os.makedirs(species_dir)

            segment_filename = f"{XCID}_{i}.{filetype}"
            segment_path = os.path.join(species_dir, segment_filename)

            # Save the segment using soundfile
            sf.write(segment_path, segment, rate, format=filetype.upper())

            # Update the new_recordings list
            new_rec = {
                'species': species,
                'XCID': f"{XCID}_{i}",
                'path': os.path.relpath(segment_path, 'processed')
            }
            new_recordings.append(new_rec)

    # Update the data.json file
    new_data = {
        'numRecordings': len(new_recordings),
        'speciesID': speciesID,
        'recordings': new_recordings
    }

    # Save the new data.json file into 'processed' directory
    output_json_path = os.path.join('processed', 'data_processed.json')
    with open(output_json_path, 'w') as f:
        json.dump(new_data, f, indent=4)


preprocess_audio()
