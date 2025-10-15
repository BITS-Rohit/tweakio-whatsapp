from pathlib import Path
import os
from platformdirs import PlatformDirs

dirs = PlatformDirs(appname="TweakioWhatsApp", appauthor="Rohit")

# 🏠 This is your app's root directory (auto OS-specific)
rootDir = Path(dirs.user_data_dir)

# Create your app subdirectories
browser_manager_dir = rootDir / "BrowserManager"
fingerprint_file = browser_manager_dir / "fingerprint.pkl"
user_dir = rootDir / "user"
cache_dir = Path(dirs.user_cache_dir)
log_dir = Path(dirs.user_log_dir)

# Ensure folders exist
for d in [browser_manager_dir, user_dir, cache_dir, log_dir]:
    os.makedirs(d, exist_ok=True)


print(f"Root Dir: {rootDir}")
print(f"Browser Manager Dir: {browser_manager_dir}")
print(f"User Dir: {user_dir}")
print(f"Cache Dir: {cache_dir}")
print(f"Log Dir: {log_dir}")
