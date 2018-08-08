# coding: utf-8

import sys
import re

if len(sys.argv) != 3:
    print('Usage: python patch_version <filename> <version>')
    exit()

filename = sys.argv[1]
version = sys.argv[2]
pattern = re.compile(r"""^\s*(__)?version(__)?\s*=\s*['"](?P<version>.*?)['"][,]?$""")

with open(filename, 'r', encoding='utf-8') as f:
    content = f.readlines()

found = False
result = []
for line in content:
    m = pattern.match(line)
    if m:
        start = m.start('version')
        end = m.end('version')
        line = line[:start] + version + line[end:]
        found = True
    result.append(line)

if found:
    with(open(filename, 'w', encoding='utf-8')) as f:
        f.writelines(result)
