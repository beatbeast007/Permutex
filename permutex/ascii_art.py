"""
Permutex Banner Art
Styled using ANSI Shadow in Cyber Cyan
"""

import shutil

LOGO = r"""
░▒▓███████▓▒░░▒▓████████▓▒░▒▓███████▓▒░░▒▓██████████████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓████████▓▒░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░   ░▒▓█▓▒░       ░▒▓██████▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░   ░▒▓█▓▒░        ░▒▓████▓▒░  
░▒▓███████▓▒░░▒▓██████▓▒░ ░▒▓███████▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░   ░▒▓██████▓▒░     ░▒▓██▓▒░   
░▒▓█▓▒░      ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░   ░▒▓█▓▒░        ░▒▓████▓▒░  
░▒▓█▓▒░      ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░   ░▒▓█▓▒░       ░▒▓██████▓▒░ 
░▒▓█▓▒░      ░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░   ░▒▓█▓▒░   ░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░
"""

def print_header():
    """Displays the Permutex header in styled ANSI colors."""
    CYAN_BOLD = "\033[1;36m"
    WHITE_BOLD = "\033[1;37m"
    DIM = "\033[2m"
    RESET = "\033[0m"

    # Determine terminal width for centering
    try:
        term_width, _ = shutil.get_terminal_size()
    except Exception:
        term_width = 100  # fallback width

    print()  # top spacing

    for line in LOGO.strip().splitlines():
        if line.strip():
            pad = " " * max(0, (term_width - len(line)) // 2)
            print(f"{pad}{CYAN_BOLD}{line}{RESET}")

    # Centered tagline
    tagline = "Context-Aware Atomic Password Profiling Engine"
    pad_tag = " " * max(0, (term_width - len(tagline)) // 2)
    print(f"\n{pad_tag}{WHITE_BOLD}{tagline}{RESET}")

    # Decorative separator
    sep_line = "═" * min(60, term_width - 4)
    pad_sep = " " * max(0, (term_width - len(sep_line)) // 2)
    print(f"{pad_sep}{DIM}{sep_line}{RESET}\n")


# Execute if called directly
if __name__ == "__main__":
    print_header()
