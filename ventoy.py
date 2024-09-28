import os,re,sys
import requests
import json

from colors import *
from constants import *

def load_mirrors(path='./mirrors.json'):
    if os.path.exists(path):
        with open(path,'r') as f:
            return json.load(f)
    else:
        raise FileNotFoundError(path)

def writeback_json(obj,path='./mirrors.json'):
    with open(path,'w') as f:
        json.dump(obj,f,indent=4)

def check_mount(mount_dir=VENTOY_MNT_PATH):
    try:
        files = os.listdir(mount_dir)
        if len(files) > 0:
            return True
        else:
            return False
    except Exception as e:
        print(f'Error: {e}')
    return False

def cleanup():
    # Move files from tmp -> ventoy mount location
    for file in os.listdir(TMP_DIR):
        try:
            old_path = os.path.join(TMP_DIR,file)
            new_path = os.path.join(VENTOY_MNT_PATH,file)
            print(f'Saving: {old_path}->{new_path}')
            os.rename(old_path,new_path)
        except Exception as e:
            print(f'Error: {e}')
            sys.exit(2)
    # Remove tmp directory
    os.rmdir(TMP_DIR)

def download_file(url):
    filename = url.split('/')[-1]
    filepath = os.path.join(TMP_DIR,filename)
    if not os.path.exists(TMP_DIR):
        os.makedirs(TMP_DIR,exist_ok=True)
    resp = requests.get(url,stream=True)
    with open(filepath,'wb') as f:
        for chunk in resp.iter_content(chunk_size=8192):
            if chunk: f.write(chunk)
    print(f'Saved: {filename} to: {filepath}')

def get_latest_index(url,index=-1,fltr=''):
    possible = {}
    req = requests.get(url)
    if req.status_code == 200:
        lines = req.text.split('\n')
        for line in lines:
            try:
                original = line.split('\"')[1]
                formatted = original.replace(fltr,'')
                num = float(formatted.replace('/',''))
                possible[original] = num
            except: continue
    print(f'Found: {possible}')
    if possible:
        nums = sorted(list(possible.values()))
        try:
            key = next((k for k,v in possible.items() if v == nums[index]), None)
        except Exception as e:
            key = next((k for k,v in possible.items() if v == nums[len(nums)-1]), None)
        return f'{url}{key}'

def check_existing(regex,dir=TMP_DIR):
    # print(regex)
    if os.path.exists(dir):
        for file in os.listdir(dir):
            if re.search(regex,file):
                return True
            if regex in file:
                return True
    return False

def get_latest_iso(mirror,regex,parts=None,vals=None):
    # If no regex, then mirror already points to the file
    if regex is None:
        return mirror
    # Else, determine the latest ISO to download
    req = requests.get(mirror)
    if req.status_code == 200:
        if parts:
            for v,part in enumerate(parts):
                # Get latest index from page
                if part and '*' in part:
                    try:
                        filterd = part.replace('*','')
                        if vals[v]:
                            mirror = get_latest_index(mirror,index=vals[v],fltr=filterd)
                        else:
                            mirror = get_latest_index(mirror,fltr=filterd)
                        print(f'{YELLOW}Redirecting{RESET}: {mirror}...')
                    except Exception as e:
                        print(f'{LIGHTRED}Error{RESET}: {e}')
                        sys.exit(4)
                # Navigate to new directory
                else:
                    # Update url with new part (directory)
                    if mirror[-2] == '/' and mirror[-1] == '/':
                        mirror = mirror[:-1]
                    mirror = f'{mirror}/{part}'
                    if v == len(parts) - 1:
                        # Add trailing '/' for incoming file
                        mirror = f'{mirror}/'
                # Send new request and ensure it's valid
                req = requests.get(mirror)
                if not req.status_code == 200:
                    print(f'{LIGHTRED}Error{RESET}: {req.text}')
                    sys.exit(5)
        # Get all ISOs matching regex pattern
        links = re.findall(r'href=[\'"]?([^\'" >]+)', req.text)
        possible = [link for link in links if re.search(regex,link) \
                and link.split('.')[-1] == str(regex).split('.')[-1]]
        if possible:
            print(possible[-1])
            return f'{mirror}{possible[-1]}'
    return None

def main():
    # Ensure ventoy USB is mounted
    if not check_mount():
        sys.exit(1)
    # Iterate over the OS mirrors and get the latest ISO file from each mirror
    os_mirrors = load_mirrors()
    for os_name,mirror_info in os_mirrors.items():
        # Extract fields from object
        mirror = mirror_info['mirror']
        pattern = mirror_info['filename-regex']
        parts = mirror_info['parts']
        vals = mirror_info['parts-values']
        print(f"{LIGHTBLUE}Checking{RESET}: latest {os_name} ({pattern or rf'{re.escape(mirror.split('/')[-1])}'})...")
        # Check if there has been a saved copy not yet uploaded to ventoy
        if not check_existing(pattern or rf'{re.escape(mirror.split('/')[-1])}'):
            download_link = get_latest_iso(mirror,pattern,parts,vals)
            if download_link:
                print(f"{GREEN}Downloading{RESET}: {os_name} from {download_link}...")
                download_file(download_link)
            else:
                print(f"{LIGHTRED}Error{RESET}: no download link found for {os_name}")
    # Cleanup tmp and move to ventoy mount
    cleanup()

if __name__ == '__main__':
    main()
