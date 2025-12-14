"""Utility to merge shard files into a final wordlist"""
import os
import sys




def merge(shard_dir: str, out_path: str):
shard_files = sorted([os.path.join(shard_dir, f) for f in os.listdir(shard_dir) if f.startswith('shard_')])
with open(out_path, 'w', encoding='utf-8', errors='ignore') as fout:
for s in shard_files:
with open(s, 'r', encoding='utf-8', errors='ignore') as fin:
for line in fin:
fout.write(line)


if __name__ == '__main__':
if len(sys.argv) < 3:
print('Usage: merge_shards.py <shard_dir> <out_path>')
sys.exit(1)
merge(sys.argv[1], sys.argv[2])