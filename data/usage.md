# Example Usage
`cd` into this directory, and run:
```sh
python download.py data -s northern_flicker dickcissel fish_crow american_bittern piping_plover black-capped_chickadee
```

# Features
* Robust code. If the data gathering run is interrupted, it can be resumed at any point by running the same script.
* No repeated downloads. Multiple data gathering runs can re-use the same downloaded files.

# Docstring

```
usage: download.py [-h] [-s SPECIES [SPECIES ...]] [-r RATE] [-l LENGTH] [-o OTHERS] [-q] [-t TIME] [-c CYCLES] name

CLI to download data from Xeno Canto.

positional arguments:
  name                  Name of data gathering run.

options:
  -h, --help            show this help message and exit
  -s SPECIES [SPECIES ...], --species SPECIES [SPECIES ...]
                        Species to download data for.
  -r RATE, --rate RATE  Minimum sampling rate filter (use 0 to allow everything).
  -l LENGTH, --length LENGTH
                        Minimum length of recording, in ms (use 0 to allow everything).
  -o OTHERS, --others OTHERS
                        Maximum number of other birds allowable in a recording (use -1 for everything).
  -q, --quiet           No printout messages.
  -t TIME, --time TIME  Time to wait between successive calls, in ms.
  -c CYCLES, --cycles CYCLES
                        Number of cycles to try downloading.
```