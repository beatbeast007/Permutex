# Permutex
A context-aware multi-threaded atomic password profiling engine with deep recursion, smart stretching, and high-performance sharding featuring atomic mutations, resumable sessions, and binary merging. Designed for precision profiling and advanced penetration testing and Red Teaming.

<img width="1264" height="234" alt="image" src="https://github.com/user-attachments/assets/ac996534-97c7-4645-9073-f3b9c6c055e1" />

## Features

- **Performance Profiles**: Select between Max, Balanced, Power Saver, or custom CPU profiles.
- **Deep Recursion Engine**: Token explosion and mutation at atomic levels (case, leet, reversal, and years).
- **Resumable Sessions**: Automatically skips completed shards for efficient re-runs.
- **Auto-Merge & Compression**: GZIP support and intelligent file merging.
- **Progress Bar & Rich UI**: Colorful CLI with heavy borders, live metrics, and estimation logic.
- **Cross-Platform Timeout Handling**: Works on both Windows and Linux.
- **Context-Aware Profiling:** Generates candidates based on intelligent combinations of Personal Identifiable Information (PII) like names, DOBs, and phone numbers.
- **Chaos Mode (Atomic Permutations):** Breaks inputs down to the character level to bruteforce every mathematical combination of the target's specific alphabet.
- **Smart Stretching:** Automatically detects and generates "lazy" patterns (e.g., `aaaaaa`, `admin111`, `passssss`) to meet minimum length requirements.
- **High-Performance Sharding:** Uses a multi-process architecture with customizable performance profiles (**Max**, **Balanced**, **Power Saver**).
- **Smart Resume:** Automatically detects interrupted sessions and resumes generation exactly where it left off, skipping completed shards.
- **Tactical UI:** Features a clean, professional CLI with heavy borders and precise progress tracking.
---

## Roadmap: Upcoming Major Features
These are planned for the next major release:

### 1. OSINT-Based Assisted Generation
Automatic enrichment of the wordlist with real-world data gathered from public sources (e.g., usernames, social media handles, breached data leaks) to better align with actual human behavior and targets.

### 2. Sub-Atomic (Self Recursive) Generation
An ultra-deep recursive generation engine that produces permutations from the tiniest character substrings and self-refined patterns-pushing password generation to its theoretical limits.

---

## Installation

Permutex requires **Python 3.8+**.

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/yourusername/permutex.git](https://github.com/yourusername/permutex.git)
    cd Permutex/permutex
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## Usage

Run the tool as a module from the root directory (Permutex/):

```bash
python -m permutex.cli
```

You'll be guided through:

1. System diagnostics

2. Target profiling (first name, last name, dob, email, nicknames, etc.)

3. Custom categories

4. Engine and mutation configuration

5. Estimated candidate count

6. Generation using multiple CPU threads

7. Optional auto-merge and cleanup

---

## Output
- Outputs .txt or .json wordlists

- Optional compression via .gz

- Files are timestamped for organization

- Intermediate shards saved in /shards/ directory

---

## Legal & Ethical Disclaimer
- Do not use this tool against systems or targets for which you do not have explicit, written permission.
- This tool is intended for educational and authorized penetration testing purposes only. Misuse of this tool is prohibited.
- The developers assume no liability for any misuse or damage caused by this program.
- Please refer to SECURITY.md for our full security policy and vulnerability reporting guidelines.
- maintained by Abhishek Bhagat (beatbeast007)

---

## Contributing
Pull requests are welcome! Feel free to fork the repo and submit changes.

---

## Credits
Built with ❤️ by BEAST (beatbeast007)
