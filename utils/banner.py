from colorama import Fore, Style

BILI_ART = r"""
  ____  _ _ _ ____  _ _ _ 
 | __ )(_) (_) __ )(_) (_)
 |  _ \| | | |  _ \| | | |
 | |_) | | | | |_) | | | |
 |____/|_|_|_|____/|_|_|_|"""

DIVIDER = "  " + "-" * 56

MUSIC_ART = r"""\
  __  __           _      ____  _                     
 |  \/  |_   _ ___(_) ___|  _ \| | __ _ _   _  ___ _ __ 
 | |\/| | | | / __| |/ __| |_) | |/ _` | | | |/ _ \ '__|
 | |  | | |_| \__ \ | (__|  __/ | (_| | |_| |  __/ |   
 |_|  |_|\__,_|___/_|\___|_|   |_|\__,_|\__, |\___|_|   
                                        |___/           """

def print_banner():
    print("\n" + Fore.LIGHTMAGENTA_EX + Style.BRIGHT + BILI_ART)
    print(Fore.WHITE + Style.BRIGHT + DIVIDER)
    print(Fore.LIGHTBLUE_EX + Style.BRIGHT + MUSIC_ART)
    print(Style.RESET_ALL)
    print(f"{Fore.CYAN}  >> BiliBili-MusicPlayer CLI | MTF Edition | 2026-01-03{Style.RESET_ALL}\n")