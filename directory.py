import os
from pathlib import Path
import shutil
from platformdirs import PlatformDirs

dirs = PlatformDirs(appname="TweakioWhatsApp", appauthor="Rohit")

# 🏠 App root directory (OS-specific)
rootDir = Path(dirs.user_data_dir)

# App subdirectories and files
browser_manager_dir = rootDir / "BrowserManager"
storage_state_file = browser_manager_dir / "StorageState.json"
fingerprint_file = browser_manager_dir / "fingerprint.pkl"
fingerprint_debug_json = browser_manager_dir / "fingerprint.json"
user_dir = rootDir / "user"
cache_dir = Path(dirs.user_cache_dir)
log_dir = Path(dirs.user_log_dir)
MessageTrace_file = cache_dir / "MessageTrace.txt"
ErrorTrace_file = cache_dir / "ErrorTrace.log"

# Ensure folders exist
def makedir( from_: str ,override : bool = True ):
    """Directory Reset"""
    if override: print("====== Overriding =======")
    print(f"---directories creation--- {from_}")
    for d in [browser_manager_dir, user_dir, cache_dir, log_dir]:
        if override: shutil.rmtree(d) if d.exists() else None
        os.makedirs(d, exist_ok=True)
makedir(override=False, from_="From Directory itself")


async def get_all_paths() -> dict:
    """
    Returns a dictionary of all directory and file paths in the app.
    Keys are variable names, values are Path objects.
    """
    current_globals = globals()
    paths_dict = {name: val for name, val in current_globals.items() if isinstance(val, Path)}
    return paths_dict


