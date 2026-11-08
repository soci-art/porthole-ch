#!/usr/bin/env python3
"""Apply zh translations to a copy of the upstream tree, line-targeted.
Usage: apply_translations.py <src_tree> <i18n_dir> <out_tree>
- Reads batches + translations from <i18n_dir>.
- For each unit, for each recorded line, replaces the literal on that line.
- Writes a report JSON to <out_tree>/../apply-report.json (next to out tree) and prints summary.
Never modifies <src_tree>."""
import json, glob, os, re, shutil, sys, collections

src, i18n, out = sys.argv[1], sys.argv[2], sys.argv[3]
if os.path.exists(out): shutil.rmtree(out)
shutil.copytree(src, out, ignore=shutil.ignore_patterns('.git'))

zhmap={}
for f in glob.glob(os.path.join(i18n,'translations','batch-*.zh.json')):
    for e in json.load(open(f)): zhmap[e['id']]=e['zh']

units=[]
for bf in sorted(glob.glob(os.path.join(i18n,'batches','batch-*.json'))):
    units += json.load(open(bf))['units']

# group units by file
byfile=collections.defaultdict(list)
for u in units:
    if u['id'] in zhmap: byfile[u['file']].append(u)

applied=0; skipped_same=0; failures=[]
changed_lines=collections.defaultdict(set)  # file -> set of line numbers changed
for path, us in byfile.items():
    full=os.path.join(out,path)
    if not os.path.exists(full):
        failures.append((path,None,'file missing')); continue
    lines=open(full,encoding='utf-8').read().split('\n')
    # process per line: units sorted by text length desc to avoid substring shadowing
    perline=collections.defaultdict(list)
    for u in us:
        for ln in u['lines']: perline[ln].append(u)
    for ln, lus in perline.items():
        if ln<1 or ln>len(lines):
            for u in lus: failures.append((path,ln,f"line out of range {u['id']}"))
            continue
        line=lines[ln-1]
        for u in sorted(lus, key=lambda x:-len(x['text'])):
            en=u['text']; zh=zhmap[u['id']]
            if en==zh: skipped_same+=1; continue
            q='"'+en+'"'
            if q in line:
                line=line.replace(q, '"'+zh+'"', 1); applied+=1; changed_lines[path].add(ln); continue
            if en in line:
                line=line.replace(en, zh, 1); applied+=1; changed_lines[path].add(ln); continue
            failures.append((path, ln, f"{u['id']}: literal not found: {en[:70]!r}"))
        lines[ln-1]=line
    content='\n'.join(lines)
    # fallback for multiline literals: whole-file replace
    still=[]
    for (p,ln,msg) in failures:
        if p==path and 'literal not found' in msg:
            uid=msg.split(':')[0]
            u=next((x for x in us if x['id']==uid), None)
            if u and '\n' in u['text'] and u['text'] in content:
                content=content.replace(u['text'], zhmap[uid], 1); applied+=1
                changed_lines[path].add(ln)
                continue
        still.append((p,ln,msg))
    failures=still
    open(full,'w',encoding='utf-8').write(content)

# plist translations
plist=json.load(open(os.path.join(i18n,'translations','plist.zh.json')))
import plistlib
plist_changed=[]
for p in plist:
    full=os.path.join(out,p['file'])
    if p['file'].endswith('.plist'):
        with open(full,'rb') as fh: pl=plistlib.load(fh)
        cur=pl.get(p['key'])
        if cur!=p['text']: failures.append((p['file'],None,f"plist {p['key']} value mismatch: {cur!r}")); continue
        pl[p['key']]=p['zh']
        with open(full,'wb') as fh: plistlib.dump(pl,fh)
        plist_changed.append((p['file'],p['key']))
    elif p['file'].endswith('.yml'):
        txt=open(full,encoding='utf-8').read()
        # project.yml: display name appears as value after the key in settings blocks
        pat=re.compile(r'('+re.escape(p['key'])+r':\s*)'+re.escape(p['text'])+r'(\s*$)', re.M)
        new, n = pat.subn(lambda m: m.group(1)+p['zh']+m.group(2), txt)
        if n==0: failures.append((p['file'],None,f"yml {p['key']}={p['text']} not found"))
        else:
            open(full,'w',encoding='utf-8').write(new); plist_changed.append((p['file'],p['key'],n))

report={'applied':applied,'skipped_same':skipped_same,'failures':failures,
        'plist_changed':plist_changed,
        'changed_files':len(changed_lines),
        'changed_line_count':sum(len(v) for v in changed_lines.values())}
json.dump(report, open(os.path.join(os.path.dirname(out.rstrip('/')),'apply-report.json'),'w'), ensure_ascii=False, indent=1)
print(json.dumps({k:v for k,v in report.items() if k!='failures'}, ensure_ascii=False))
print('failures:', len(failures))
for f in failures[:40]: print('  FAIL', f)
