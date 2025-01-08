# Pre-Processing Specs

## Core Tasks

Vincent will write some code to download recordings according to the structure as laid out in the `raw` folder. Your task is to take those files and construct a new dataset, stored in the `processed` folder.

Your pre-processing pipline should expose the following parameters:

1. `rate: int = 48000` The sampling rate of the output files, in hertz.
2. `length: float = 3` The length of each output file, in seconds.
3. `filetype: str = wav` The desired output filetype of the files.
4. `convert_mono: bool = False` Whether to convert output file to mono.

Your task is then to write a Python script which reads in files from `raw` and:
1. Converts them to the desired sampling rate.
2. Segments them into `length`-second chunks.
3. Optionally converting them into mono.
4. Saves them into an appropriate place in `processed` using the desired filetype.

You should also save an updated `data.json` file into the folder `processed`. Because each recording will now have multiple segments, you should try to update the ID of each recording to reflect that.

## Optional Tasks

- [ ] Filter out recording segments that are mostly silence.
