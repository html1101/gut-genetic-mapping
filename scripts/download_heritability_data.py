"""Download reference results and optionally raw reads; Python standard library only."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'data/external'
FIELDS = 'run_accession,sample_accession,sample_alias,experiment_title,library_strategy,library_source,library_layout,read_count,base_count,fastq_ftp,fastq_md5,fastq_bytes'
SOURCES = {
    'elife-75419-supp1-v1.xlsx': 'https://cdn.elifesciences.org/articles/75419/elife-75419-supp1-v1.xlsx',
    'PRJNA759194_runs.tsv': 'https://www.ebi.ac.uk/ena/portal/api/filereport?accession=PRJNA759194&result=read_run&fields='+FIELDS+'&format=tsv',
    'published_figure1.jpg': 'https://iiif.elifesciences.org/lax/75419%2Felife-75419-fig1-v1.tif/full/1500,/0/default.jpg',
}

def digest(path, algorithm):
    h = hashlib.new(algorithm)
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()

def download(url, path, md5=None, size=None):
    if path.exists():
        if md5 and digest(path, 'md5') == md5 and (size is None or path.stat().st_size == size): return
        if not md5: return  # preserve the downloaded snapshot
    temporary = path.with_suffix(path.suffix+'.part')
    print('Downloading', path.name, flush=True)
    with urlopen(url, timeout=120) as response, temporary.open('wb') as out:
        while block := response.read(1024*1024): out.write(block)
    if size is not None and temporary.stat().st_size != size: raise ValueError('Size mismatch: '+str(path))
    if md5 and digest(temporary,'md5') != md5: raise ValueError('MD5 mismatch: '+str(path))
    temporary.replace(path)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-all', action='store_true', help='Download all ~8.26 GB of manifest FASTQs')
    parser.add_argument('--run', action='append', help='Download selected run(s), including every listed FASTQ')
    parser.add_argument('--record-only', action='store_true', help='Record provenance of existing files, no network')
    args=parser.parse_args()
    DEST.mkdir(parents=True, exist_ok=True)
    if not args.record_only:
        for name,url in SOURCES.items(): download(url, DEST/name)
    with (DEST/'PRJNA759194_runs.tsv').open() as f: runs=list(csv.DictReader(f,delimiter='\t'))
    requested = set(args.run or ['SRR15677983'])
    unknown = requested - {r['run_accession'] for r in runs}
    if unknown: raise ValueError(f'Runs absent from manifest: {unknown}')
    raw_sources={}
    for r in runs:
        urls=r['fastq_ftp'].split(';'); checks=r['fastq_md5'].split(';'); sizes=r['fastq_bytes'].split(';')
        assert len(urls)==len(checks)==len(sizes)
        for url,md5,size in zip(urls,checks,sizes):
            if not url: continue
            path=DEST/url.rsplit('/',1)[-1]
            if not args.record_only and (args.raw_all or r['run_accession'] in requested):
                download('https://'+url,path,md5,int(size))
            if path.exists():
                assert digest(path,'md5')==md5 and path.stat().st_size==int(size)
                raw_sources[path.name]='https://'+url
    version=subprocess.check_output(['git','-C',str(ROOT/'reference_code'),'rev-parse','HEAD'],text=True).strip()
    files=[]
    for path in sorted((ROOT/'reference_code/Data').rglob('*')):
        if path.is_file(): files.append({'path':str(path.relative_to(ROOT)), 'bytes':path.stat().st_size,'sha256':digest(path,'sha256')})
    for name,url in {**SOURCES,**raw_sources}.items():
        path=DEST/name
        if path.exists(): files.append({'path':str(path.relative_to(ROOT)),'url':url,'bytes':path.stat().st_size,'sha256':digest(path,'sha256')})
    (DEST/'provenance.json').write_text(json.dumps({'retrieved_date':'2026-11-09','reference_repository':'https://github.com/sdoms/mapping_scripts','reference_commit':version,'files':files},indent=2)+'\n')
    print('Recorded',len(files),'files. Raw archive download is optional for the processed-data analysis.')
if __name__=='__main__': main()
