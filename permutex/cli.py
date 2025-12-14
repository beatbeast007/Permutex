#!/usr/bin/env python3
"""
Permutex CLI (Full): Performance Profiles, Windows Fix, High-Speed Merge.
"""

from __future__ import annotations

import argparse
import multiprocessing
import os
import sys
import subprocess
import importlib.util
import time
import json
import gzip
import shutil
import random
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import Dict, List, Any, Set, Tuple

# --- SILENT BOOTSTRAPPER ---
def ensure_dependencies_silent():
    required = ["rich", "click", "tqdm", "requests"]
    missing = [p for p in required if importlib.util.find_spec(p) is None]
    if missing:
        print(f"Installing requirements ({', '.join(missing)})...", end=" ", flush=True)
        try:
            for p in missing:
                subprocess.check_call([sys.executable, "-m", "pip", "install", p], 
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("DONE")
        except:
            sys.exit(1)

ensure_dependencies_silent()

# --- IMPORTS ---
import requests
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, FileSizeColumn
from rich.table import Table
from rich.align import Align
from rich import box # Needed for heavy borders
from tqdm import tqdm

try:
    from .ascii_art import print_header
    from .generator.parallel import worker_generate_shard 
    from .ai.predictor import estimate_generation_time
    from .generator.expander import expand_categories, expand_token_deep
    from .generator.mutations import generate_mutations
except ImportError:
    print("\n[!] Error: Run from parent directory: python -m permutex.cli")
    sys.exit(1)

console = Console()

# --- CROSS-PLATFORM INPUT HANDLER ---
def wait_for_user_input(timeout=10):
    """
    Waits for user input with a timeout. Works on both Windows and Linux.
    """
    print(f"\n [*] Auto-merging in {timeout}s... (Press Enter to merge immediately)", end='', flush=True)
    
    if os.name == 'nt':
        import msvcrt
        start_time = time.time()
        while time.time() - start_time < timeout:
            if msvcrt.kbhit():
                msvcrt.getch()
                print("\n [*] Manual merge trigger detected.")
                return
            time.sleep(0.1)
    else:
        import select
        i, o, e = select.select([sys.stdin], [], [], timeout)
        if i:
            sys.stdin.readline()
            print("\n [*] Manual merge trigger detected.")
    
    print()

# --- UI UTILS ---

def format_size(bytes_size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0: return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"

def print_status(text: str, status: str = "OK", delay: float = 0.0):
    if delay > 0: time.sleep(delay)
    if status == "OK": tag = "[bold green][OK][/bold green]"
    elif status == "FAIL": tag = "[bold red][!!][/bold red]"
    elif status == "INFO": tag = "[bold cyan][*][/bold cyan]"
    else: tag = f"[bold yellow][{status}][/bold yellow]"
    console.print(f" {tag} {text}")

def system_diagnostics():
    os.system('cls' if os.name == 'nt' else 'clear')
    print_header()
    
    grid = Table.grid(expand=True)
    grid.add_column(style="dim")
    grid.add_column(justify="right")
    
    # Standard UI with Heavy Blue Border
    console.print(Panel(Align.center("[bold white]SYSTEM DIAGNOSTICS[/bold white]"), box=box.HEAVY, style="blue"))
    
    print_status(f"Python {sys.version_info.major}.{sys.version_info.minor}", delay=0.2)
    print_status(f"OS: {os.name.upper()}", delay=0.2)
    print_status(f"CPU Cores Available: [bold cyan]{multiprocessing.cpu_count()}[/bold cyan]", delay=0.2)
    
    try:
        with open("perm_io_test.tmp", "w") as f: f.write("test")
        os.remove("perm_io_test.tmp")
        print_status("Disk Write Permissions", delay=0.2)
    except:
        print_status("Write Permissions", "FAIL")
        sys.exit(1)

    print_status("Deep Recursion Engine", delay=0.2)
    print_status("Resumable Session Manager", delay=0.2)
    console.print("")
    console.print(Align.center("[blink bold white]PRESS [ENTER] TO START[/blink bold white]"))
    input()
    os.system('cls' if os.name == 'nt' else 'clear')
    print_header()

# --- INPUT HELPERS ---

def prompt(text: str, hint: str = "", allow_empty: bool = False) -> str:
    if hint: console.print(f"[dim]>> {hint}[/dim]", style="dim", justify="right")
    return Prompt.ask(f"[bold cyan]{text}[/bold cyan]", default="" if allow_empty else None, show_default=False)

def prompt_yes_no(text: str, hint: str = "", default: bool = True) -> bool:
    if hint: console.print(f"[dim]>> {hint}[/dim]", style="dim", justify="right")
    return Confirm.ask(f"[bold yellow]{text}[/bold yellow]", default=default)

def add_to_category(categories: Dict[str, List[str]], cat: str, val: str):
    if not val: return
    categories.setdefault(cat, [])
    if val not in categories[cat]: categories[cat].append(val)

def parse_years(years_str: str | None) -> List[str]:
    if not years_str: return []
    return [y.strip() for y in years_str.split(",") if y.strip()]

# --- PERFORMANCE PROFILE SELECTOR ---

def select_performance_profile(args_threads: int | None) -> int:
    """Selects worker count based on performance profile."""
    if args_threads: return args_threads

    total_cores = multiprocessing.cpu_count()
    
    # Define Profiles
    max_mode = total_cores
    balanced_mode = max(1, int(total_cores * 0.5))
    saver_mode = max(1, int(total_cores * 0.25))
    
    # UI FIX: Added Heavy Blue Border Panel here
    console.print("\n")
    console.print(Panel("[bold white]PERFORMANCE PROFILE[/bold white]", box=box.HEAVY, style="blue", expand=False))
    
    grid = Table.grid(expand=True)
    grid.add_column()
    grid.add_row("[bold cyan][1][/bold cyan] Max Performance", f"[dim]({max_mode} Workers - 100% CPU)[/dim]")
    grid.add_row("[bold cyan][2][/bold cyan] Balanced Mode", f"[dim]({balanced_mode} Workers - 50% CPU)[/dim]")
    grid.add_row("[bold cyan][3][/bold cyan] Power Saver", f"[dim]({saver_mode} Workers - 25% CPU)[/dim]")
    grid.add_row("[bold cyan][4][/bold cyan] Manual Entry", f"[dim](Custom)[/dim]")
    
    # Using simple box for the list inside the section
    console.print(Panel(grid, box=box.SIMPLE, style="white"))
    
    choice = Prompt.ask("[bold cyan]Select Profile[/bold cyan]", choices=["1", "2", "3", "4"], default="1", show_choices=False)
    
    if choice == "1": return max_mode
    if choice == "2": return balanced_mode
    if choice == "3": return saver_mode
    if choice == "4":
        while True:
            try:
                # Default to 7 if user just presses enter in manual mode
                val = Prompt.ask("[bold cyan]Enter workers[/bold cyan]", default="7")
                return int(val)
            except ValueError:
                console.print("[bold red]Invalid number[/bold red]")
    
    return 7 # Fallback

# --- EXACT COUNT SIMULATION ---

def simulate_pair_count(token_a: str, token_b: str, cat_a: str, cat_b: str, 
                        mutations_opts: Dict, expand_opts: Dict) -> int:
    separators = ["", "@", "_", ".", "#", "123"]
    
    if expand_opts.get('deep_recursion'):
        is_date_a = (cat_a == 'dob') or (len(token_a) > 0 and token_a[0].isdigit())
        atoms_a = set(expand_token_deep(token_a, is_date=is_date_a, min_sub_len=expand_opts.get('subtoken_min_len', 2)))
        is_date_b = (cat_b == 'dob') or (len(token_b) > 0 and token_b[0].isdigit())
        atoms_b = set(expand_token_deep(token_b, is_date=is_date_b, min_sub_len=expand_opts.get('subtoken_min_len', 2)))
    else:
        atoms_a = {token_a}
        atoms_b = {token_b}
    
    final_muts_a = set()
    for A in atoms_a:
        use_deep_a = expand_opts.get('deep_recursion') and not (len(A)>0 and A[0].isdigit())
        muts = generate_mutations(A,
            enable_leet=mutations_opts.get('leet'),
            enable_case_variants=mutations_opts.get('case'),
            enable_reverse=mutations_opts.get('reverse'),
            append_years=mutations_opts.get('years'), 
            deep_casing=use_deep_a
        )
        final_muts_a.update(muts)

    final_muts_b = set()
    for B in atoms_b:
        use_deep_b = expand_opts.get('deep_recursion') and not (len(B)>0 and B[0].isdigit())
        leet_b = mutations_opts.get('leet') and not (len(B)>0 and B[0].isdigit())
        muts = generate_mutations(B,
            enable_leet=leet_b,
            enable_case_variants=mutations_opts.get('case'),
            enable_reverse=False,
            append_years=mutations_opts.get('years'),
            deep_casing=use_deep_b
        )
        final_muts_b.update(muts)

    combo_count = len(final_muts_a) * len(final_muts_b) * len(separators) * 2
    return combo_count

def calculate_total_candidates(categories: Dict[str, List[str]], selected_pairs: List[Tuple[str, str]], 
                               mutations_opts: Dict, expand_opts: Dict) -> int:
    total_count = 0
    for cat_a, cat_b in selected_pairs:
        tokens_a = categories.get(cat_a, [])
        tokens_b = categories.get(cat_b, [])
        if not tokens_a or not tokens_b: continue
        
        sample_a = sorted(tokens_a, key=len)
        sample_b = sorted(tokens_b, key=len)
        
        samples_a = [sample_a[0], sample_a[-1]]
        if len(sample_a) > 2: samples_a.append(sample_a[len(sample_a)//2])
        
        samples_b = [sample_b[0], sample_b[-1]]
        if len(sample_b) > 2: samples_b.append(sample_b[len(sample_b)//2])
        
        pair_sum = 0
        comparisons = 0
        for ta in samples_a:
            for tb in samples_b:
                c = simulate_pair_count(ta, tb, cat_a, cat_b, mutations_opts, expand_opts)
                pair_sum += c
                comparisons += 1
        
        if comparisons == 0: continue
        avg_per_pair = pair_sum / comparisons
        total_count += int(avg_per_pair * len(tokens_a) * len(tokens_b))
        
    return total_count

# --- MAIN ---

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output")
    parser.add_argument("--deep-recursion", action="store_true")
    parser.add_argument("--threads", type=int)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--max-combinations", type=int, default=100_000_000)
    parser.add_argument("--webhook")
    args, _ = parser.parse_known_args()

    system_diagnostics()

    console.print(Panel("[bold white]TARGET PROFILING[/bold white]", box=box.HEAVY, style="blue", expand=False))
    console.print("[dim italic]Press Enter to skip optional fields.[/dim italic]\n")
    
    categories = {}
    data_points = [
        ("First Name", "Target's primary name", "first_name"),
        ("Last Name", "Family name", "last_name"),
        ("DOB", "DDMMYYYY", "dob"),
        ("Email", "Personal/Work", "email"),
        ("Phone", "Mobile digits", "phone"),
        ("Nicknames", "Comma separated", "nickname")
    ]

    for label, hint, cat_key in data_points:
        val = prompt(label, hint=hint, allow_empty=True)
        if val:
            if cat_key == "nickname":
                for v in val.split(','): add_to_category(categories, "nickname", v.strip())
            else:
                add_to_category(categories, cat_key, val)

    console.print("\n[dim]Custom Categories[/dim]")
    while True:
        cat = prompt("Category Name", hint="Leave empty to finish", allow_empty=True)
        if not cat: break
        vals = prompt(f"Values for '{cat}'", hint="Comma separated")
        for v in vals.split(','): add_to_category(categories, cat, v.strip())

    if not categories:
        print_status("No data provided.", "FAIL")
        return

    # CONFIGURATION
    console.print("\n")
    console.print(Panel("[bold white]ENGINE CONFIGURATION[/bold white]", box=box.HEAVY, style="blue", expand=False))
    
    deep_recursion = args.deep_recursion
    if not deep_recursion:
        deep_recursion = prompt_yes_no("Enable Deep Recursion?", hint="Substrings & Atomic Date parts", default=True)

    with console.status("[bold green]Preprocessing tokens..."):
        categories = expand_categories(categories, expand_subtokens=False, dob_variants=False, max_tokens_per_category=100)
        time.sleep(0.5)

    min_len = int(prompt("Min Length", hint="e.g. 6", allow_empty=True) or "6")
    max_len = int(prompt("Max Length", hint="e.g. 16", allow_empty=True) or "16")
    
    # UI FIX: Added Heavy Blue Border Panel here
    console.print("\n")
    console.print(Panel("[bold white]COMPLEXITY[/bold white]", box=box.HEAVY, style="blue", expand=False))
    
    enable_leet = prompt_yes_no("Leet Speak?", hint="a->@, e->3", default=True)
    enable_case = prompt_yes_no("Case Variants?", hint="Upper/Lower/Title", default=True)
    enable_reverse = prompt_yes_no("Reverse Tokens?", hint="admin -> nimda", default=False)
    
    years = []
    if prompt_yes_no("Append Years?", hint="Current/Birth years", default=True):
        y_str = prompt("Years to append", hint="e.g. 2024,2025")
        years = parse_years(y_str)

    # ESTIMATION
    selected_pairs = []
    cats = list(categories.keys())
    for a in cats:
        for b in cats:
            selected_pairs.append((a, b))

    sim_mut_opts = {
        "leet": enable_leet, "reverse": enable_reverse, "case": enable_case, 
        "years": years, "max_per_token": 15
    }
    sim_exp_std = {"deep_recursion": False, "subtoken_min_len": 2}
    sim_exp_deep = {"deep_recursion": True, "subtoken_min_len": 2}

    with console.status("[bold yellow]Simulating exact counts...[/bold yellow]"):
        std_count = calculate_total_candidates(categories, selected_pairs, sim_mut_opts, sim_exp_std)
        deep_count = calculate_total_candidates(categories, selected_pairs, sim_mut_opts, sim_exp_deep)
        time.sleep(0.5)

    # UI FIX: Added Heavy Blue Border Panel here
    console.print("\n")
    console.print(Panel("[bold white]CANDIDATE ANALYSIS[/bold white]", box=box.HEAVY, style="blue", expand=False))
    
    grid = Table(box=box.SIMPLE, expand=True)
    grid.add_column("Mode", style="bold white")
    grid.add_column("Total Candidates", justify="right", style="cyan")
    grid.add_column("Multiplier", justify="right", style="yellow")
    
    mult = deep_count / std_count if std_count > 0 else 0
    grid.add_row("Standard", f"{std_count:,}", "1x")
    grid.add_row("Deep Recursion", f"{deep_count:,}", f"{mult:.1f}x")
    
    # We remove the panel wrapper around the table itself to avoid double borders, keeping the section cleaner
    console.print(grid)
    
    final_count = deep_count if deep_recursion else std_count
    
    # --- SELECT THREADS / PROFILE ---
    threads = select_performance_profile(args.threads)
    
    # Resume Check
    shard_dir = "shards"
    os.makedirs(shard_dir, exist_ok=True)
    resuming = False
    if [f for f in os.listdir(shard_dir) if f.startswith("shard_")]:
        console.print(f"\n[bold yellow]FOUND EXISTING SHARDS[/bold yellow]")
        if prompt_yes_no("Resume previous session?", default=True): resuming = True

    if final_count > args.max_combinations:
        console.print(f"\n[bold red]WARNING: High candidate count ({final_count:,})[/bold red]")
        if not prompt_yes_no("Continue anyway?", default=False): return
    elif not resuming and not prompt_yes_no("Start Generation?", default=True): return

    # EXECUTION
    timestamp = datetime.now().strftime("%d%m%Y_%H%M%S")
    out_fmt = "json" if prompt_yes_no("Export as JSON?", default=False) else "txt"
    out_name = f"Wordlist_{timestamp}.{out_fmt}"
    out_path = args.output or out_name
    compress_output = prompt_yes_no("Compress Output?", hint="Save as .gz", default=True)
    
    console.print(f"\n[bold green]LAUNCHING {threads} WORKERS -> {out_path}[/bold green]")

    groups = [[] for _ in range(threads)]
    for idx, p in enumerate(selected_pairs): groups[idx % threads].append(p)

    expand_opts = {"deep_recursion": deep_recursion, "subtoken_min_len": 2, "subtoken_max_len": 5}

    total_written = 0
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"), 
        BarColumn(), TextColumn("[progress.percentage]{task.percentage:>3.0f}%"), 
        TimeElapsedColumn(),
    ) as progress:
        
        active_groups = []
        for i, grp in enumerate(groups):
            if resuming and os.path.exists(os.path.join(shard_dir, f"shard_{i:03d}.txt")): continue 
            active_groups.append((i, grp))

        main_task = progress.add_task("[cyan]Overall Progress", total=len(groups))
        progress.advance(main_task, len(groups) - len(active_groups))

        futures = []
        with ProcessPoolExecutor(max_workers=threads) as executor:
            for i, grp in active_groups:
                if not grp: continue
                shard_path = os.path.join(shard_dir, f"shard_{i:03d}.txt")
                futures.append(executor.submit(
                    worker_generate_shard, i, grp, categories, sim_mut_opts, None, 
                    shard_path, 5000, args.limit, expand_opts
                ))
            
            completed = 0
            for fut in as_completed(futures):
                try:
                    res = fut.result()
                    total_written += res.get('written', 0)
                    completed += 1
                    progress.update(main_task, advance=1, description=f"[cyan]Workers Active: {len(futures)-completed} | Candidates: {total_written:,}")
                except Exception as e: 
                    console.print(f"[bold red]Worker Error: {e}[/bold red]")

    print_status(f"Generation Complete. Total: {total_written:,}")
    
    # Auto-Merge
    wait_for_user_input(10)

    final_path = out_path + ".gz" if compress_output else out_path
    print_status(f"Merging to {final_path}...", "INFO")
    
    try:
        shard_files = sorted([f for f in os.listdir(shard_dir) if f.startswith("shard_")])
        if compress_output:
            opener = gzip.open(final_path, "wb")
        else:
            opener = open(final_path, "wb")
            
        with opener as fout:
            if out_fmt == "json": fout.write(b"[\n")
            
            for sf in tqdm(shard_files, desc="Merging...", unit="shard"):
                with open(os.path.join(shard_dir, sf), "rb") as fin:
                    shutil.copyfileobj(fin, fout)
            
            if out_fmt == "json": fout.write(b"\n]")
        
        console.print(f"\n[bold green]FILE SAVED:[/bold green] [underline]{final_path}[/underline]")
        
        actual_size = os.path.getsize(final_path)
        console.print(f"[bold cyan]Final Size: {format_size(actual_size)}[/bold cyan]")
        
        if prompt_yes_no("\nClean up shards?", default=True): shutil.rmtree(shard_dir)
            
    except Exception as e:
        print_status(f"Merge Failed: {e}", "FAIL")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrupted.[/bold red]")
        sys.exit(1)
