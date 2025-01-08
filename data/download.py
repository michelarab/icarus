import os
import json
import time
import requests
import argparse
from tqdm import tqdm


parser = argparse.ArgumentParser(description="CLI to download data from Xeno Canto.")
parser.add_argument('name', help='Name of data gathering run.')
parser.add_argument('-s', '--species', action='extend', nargs="+", type=str, default=[],
                    help='Species to download data for.')
parser.add_argument('-r', '--rate', type=int, default=48000,
                    help='Minimum sampling rate filter (use 0 to allow everything).')
parser.add_argument('-l', '--length', type=int, default=3000,
                    help='Minimum length of recording, in ms (use 0 to allow everything).')
parser.add_argument('-o', '--others', type=int, default=-1,
                    help='Maximum number of other birds allowable in a recording (use -1 for everything).')
parser.add_argument('-q', '--quiet', action='store_true',
                    help='No printout messages.')
parser.add_argument('-t', '--time', type=int, default=200,
                    help='Time to wait between successive calls, in ms.')
parser.add_argument('-c', '--cycles', type=int, default=5,
                    help='Number of cycles to try downloading.')
parser.add_argument('-p', '--preprocess', action='store_true', 
                    help='Run audio preprocessing after data download.')
args = parser.parse_args()

args.keep = ['id', 'url', 'file', 'type', 'sex', 'stage', 'also', 'length', 'smp', 'date', 'time', 'lat', 'lng']
args.jsonpath = f'raw/{args.name}.json'
args.api_url = 'https://www.xeno-canto.org/api/2/recordings?query={}'


def safemake(dir):
    if not os.path.exists(dir):
        os.makedirs(dir, exist_ok=True)

def norm(name):
    name = name.replace(' ', '%20')
    name = name.replace('_', '%20')
    return name

def len2sec(lstr):
    min, sec = lstr.split(':')
    return 60*int(min) + int(sec)

def retrieve_api(species):
    species = norm(species)
    data = requests.get(args.api_url.format(species))
    safemake('tmp')
    with open(f'tmp/{species}_api.json', 'w', encoding='utf-8') as f:
        json.dump(data.json(), f, indent = 4)
    return data.json()

def filter(rec):
    if args.others != -1 and len(rec['also']) > args.others:
        return False
    if int(rec['smp']) < args.rate:
        return False
    if len2sec(rec['length']) < args.length / 1000:
        return False
    return True

def download_file(url, path):
    data = requests.get(url, allow_redirects=True)
    if data.status_code == 200:
        with open(path, 'wb') as f:
            f.write(data.content)
        return True
    else:
        return False

def download_api(species, spid, overwrite=False, verbose=True):
    species = norm(species)

    if verbose:
        print(f'Downloading data for species {species}.')
    
    if overwrite or not os.path.exists(f'tmp/{species}_api.json'):
        data = retrieve_api(species)
    else:
        with open(f'tmp/{species}_api.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    
    with open(args.jsonpath, 'r', encoding='utf-8') as f:
        existing = json.load(f)

    safemake(f'raw/{species}')
    downloaded = existing['downloaded']
    recordings = []

    if verbose:
        iter = tqdm(data['recordings'])
        iter.set_description(f'{species}')
    else:
        iter = data['recordings']
    
    for rec in iter:
        id = rec['id']
        if filter(rec) and id not in downloaded:
            filetype = rec['file-name'].split('.')[-1]
            obj = {k: rec[k] for k in args.keep}
            obj['XCID'] = id
            obj['species'] = spid
            obj['path'] = f'raw/{species}/{id}.{filetype}'

            if not os.path.exists(obj['path']):
                for _ in range(args.cycles):
                    time.sleep(args.time/1000)
                    if download_file(rec['file'], obj['path']):
                        break
            
            if os.path.exists(obj['path']):
                recordings.append(obj)
                downloaded.append(id)
    
    if verbose:
        print(f'Data download for species {species} complete. Updating data.json.')
    
    with open(args.jsonpath, 'w', encoding='utf-8') as f:
        new_write = existing
        new_write['numRecordings'] += len(recordings)
        new_write['downloaded'] = downloaded
        new_write['recordings'].extend(recordings)
        json.dump(new_write, f)

    if verbose:
        print(f'All good for species {species}.\n')


# ------ #

print(f'''Configuration for run: {args.name}
Maximum number of other birds: {args.others}
Minimum sampling rate (Hz): {args.rate}
Minimum length (ms): {args.length}
''')

if len(args.species) == 0:
    print('No species entered. Please use `-s` or `--species` to add species. Use `_` for spaces.')

else:
    if not args.quiet:
        print('Retrieving URLs from API.')
    pbar = tqdm(args.species)
    for sp in pbar:
        pbar.set_description(f'{sp}')
        if not os.path.exists(f'tmp/{norm(sp)}_api.json'):
            retrieve_api(sp)
    if not args.quiet:
        print('API retrieval complete.\n')

    for e, sp in enumerate(args.species):
        safemake('raw')

        if not os.path.exists(args.jsonpath):
            with open(args.jsonpath, 'w', encoding='utf-8') as f:
                json.dump({
                    'numRecordings': 0,
                    'species': args.species,
                    'downloaded': [],
                    'recordings': []
                }, f)
        else:
            with open(args.jsonpath, 'r', encoding='utf-8') as f:
                existing = json.load(f)
                assert existing['species'] == args.species
        
        download_api(sp, e, verbose=not args.quiet)
