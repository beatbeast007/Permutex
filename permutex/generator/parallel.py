"""
Parallel shard-based generation (CPU only) for Permutex.
UPGRADE: Enables Exhaustive Casing in Deep Mode.
"""

from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
import os
import time
from typing import Dict, List, Tuple

from .mutations import generate_mutations, leet_transform
from .expander import expand_token_deep 

def worker_generate_shard(
    worker_id: int,
    shard_pairs: List[Tuple[str, str]],
    categories: Dict[str, List[str]],
    mutations_opts: Dict,
    mask: str,
    shard_path: str,
    buffer_size: int = 5000,
    limit: int = None,
    expand_opts: Dict = None
) -> dict:
    """
    Worker that performs DEEP RECURSIVE expansion and writes to shard.
    """
    expand_opts = expand_opts or {}
    buffer = []
    written_count = 0
    start_time = time.time()
    separators = ["", "@", "_", ".", "#", "123"] 

    # Config for deep recursion
    deep_mode = expand_opts.get('deep_recursion', False)
    min_sub_len = expand_opts.get('subtoken_min_len', 3) 
    
    # NEW: If deep_mode is ON, we enable exhaustive casing
    use_deep_casing = deep_mode 

    os.makedirs(os.path.dirname(shard_path) or ".", exist_ok=True)

    with open(shard_path, 'w', encoding='utf-8') as f:
        
        for cat_a, cat_b in shard_pairs:
            tokens_a = categories.get(cat_a, [])
            tokens_b = categories.get(cat_b, [])
            
            # 1. Expand Atoms (Abhishek -> Abhi, shek...)
            if deep_mode:
                expanded_a = set()
                expanded_b = set()
                
                for t in tokens_a:
                    is_date = (cat_a in ['dob', 'date'] or (len(t)>0 and t[0].isdigit()))
                    expanded_a.update(expand_token_deep(t, is_date=is_date, min_sub_len=min_sub_len))
                
                for t in tokens_b:
                    is_date = (cat_b in ['dob', 'date'] or (len(t)>0 and t[0].isdigit()))
                    expanded_b.update(expand_token_deep(t, is_date=is_date, min_sub_len=min_sub_len))
                
                list_a = list(expanded_a)
                list_b = list(expanded_b)
            else:
                list_a = tokens_a
                list_b = tokens_b

            # 2. Combine & Mutate
            for A in list_a:
                # Apply mutations (Deep Casing happens here!)
                mutants_A = set(generate_mutations(
                    A, 
                    enable_leet=mutations_opts.get('leet'),
                    enable_case_variants=mutations_opts.get('case'),
                    deep_casing=use_deep_casing  # <--- PASSED HERE
                ))

                for B in list_b:
                    # We usually don't deep-case dates (B), but if B is text, we should.
                    # Simple heuristic: if B starts with digit, standard casing; else deep.
                    b_is_text = not (len(B) > 0 and B[0].isdigit())
                    
                    mutants_B = set(generate_mutations(
                        B,
                        enable_leet=False, # Rarely leet second part if date
                        enable_case_variants=mutations_opts.get('case'),
                        deep_casing=(use_deep_casing and b_is_text)
                    ))
                    
                    for ma in mutants_A:
                        for mb in mutants_B:
                            for sep in separators:
                                # AbHi@0806
                                cand1 = f"{ma}{sep}{mb}"
                                # 0806@AbHi
                                cand2 = f"{mb}{sep}{ma}"
                                
                                buffer.append(cand1)
                                buffer.append(cand2)
                                
                                if len(buffer) >= buffer_size:
                                    f.write('\n'.join(buffer) + '\n')
                                    written_count += len(buffer)
                                    buffer = []
                                    if limit and written_count >= limit:
                                        return {'worker_id': worker_id, 'written': written_count}

        if buffer:
            f.write('\n'.join(buffer) + '\n')
            written_count += len(buffer)

    return {
        'worker_id': worker_id, 
        'written': written_count, 
        'elapsed': time.time() - start_time,
        'shard_path': shard_path
    }

def parallel_generate(
    categories, selected_pairs, mutations_opts, mask, threads=None, 
    shard_dir='shards', buffer_size=1000, limit=None, merge_shards=False, 
    final_output='wordlist.txt', expand_opts=None
):
    expand_opts = expand_opts or {}
    os.makedirs(shard_dir, exist_ok=True)
    cpu_count = threads or max(1, multiprocessing.cpu_count() - 1)
    
    groups = [[] for _ in range(cpu_count)]
    for idx, p in enumerate(selected_pairs):
        groups[idx % cpu_count].append(p)

    futures = []
    stats = []
    
    with ProcessPoolExecutor(max_workers=cpu_count) as executor:
        for i, grp in enumerate(groups):
            if not grp: continue
            shard_path = os.path.join(shard_dir, f"shard_{i:03d}.txt")
            futures.append(executor.submit(
                worker_generate_shard, 
                i, grp, categories, mutations_opts, mask, shard_path, 
                buffer_size, limit, expand_opts
            ))
            
        for fut in as_completed(futures):
            try:
                stats.append(fut.result())
            except Exception as e:
                print(f"Worker Error: {e}")

    if merge_shards:
        with open(final_output, "w", encoding="utf-8", errors="ignore") as fout:
            for i in range(cpu_count):
                sp = os.path.join(shard_dir, f"shard_{i:03d}.txt")
                if os.path.exists(sp):
                    with open(sp, "r", encoding="utf-8", errors="ignore") as fin:
                        fout.write(fin.read())

    return stats
