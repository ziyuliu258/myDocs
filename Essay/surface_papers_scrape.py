import urllib.request, re, json, time, os

def fetch(url, timeout=30):
    req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8', errors='replace')

def clean(s):
    return re.sub(r'\s+',' ', re.sub(r'<[^>]+>',' ', s)).strip()

def parse_authors(html):
    # New style ltx_authors
    start=html.find('<div class="ltx_authors">')
    if start!=-1:
        candidates=[]
        for tag in ['<div id="abstract','<div class="ltx_abstract"','<section class="ltx_title','<div class="ltx_date"']:
            i=html.find(tag, start)
            if i!=-1: candidates.append(i)
        end=min(candidates) if candidates else start+30000
        block=html[start:end]
        blocks=re.split(r'<span class="ltx_creator ltx_role_author">', block)[1:]
        authors=[]
        for b in blocks:
            pm=re.search(r'<span class="ltx_personname">(.*?)</span>', b, re.S)
            if not pm: continue
            name=clean(pm.group(1))
            # remove email and superscript remnants
            name=re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b','',name)
            name=re.sub(r'[*†‡§¶#0-9,;]+','',name).strip()
            if not name: continue
            affs=[]
            for am in re.finditer(r'<span class="ltx_contact ltx_role_affiliation">(.*?)</span>', b, re.S):
                txt=clean(am.group(1)).replace('Affiliation:','').strip()
                if txt: affs.append(txt)
            authors.append({'name':name,'affiliations':affs})
        return authors
    # Old style centered paragraphs
    # find author paragraph and affiliation paragraph after title
    # crude: capture all centered p before first section
    title_idx=html.find('<h1 class="ltx_title')
    sec_idx=html.find('<section', title_idx if title_idx!=-1 else 0)
    seg=html[title_idx:sec_idx] if title_idx!=-1 and sec_idx!=-1 else html[:50000]
    # all ltx_align_center paragraphs
    paras=re.findall(r'<p[^>]*ltx_align_center[^>]*>(.*?)</p>', seg, re.S)
    return []  # too complex, handle manually

# list of papers to scrape (arxiv, title, year)
papers = [
    ("2311.17050", "Surf-D: High-Quality Surface Generation for Arbitrary Topologies using Diffusion Models", 2024),
    ("2410.03417", "Img2CAD: Conditioned 3D CAD Model Generation from Single Image with Structured Visual Geometry", 2024),
    ("2409.17106", "Text2CAD: Generating Sequential CAD Models from Beginner-to-Expert Level Text Prompts", 2024),
    ("2502.20732", "CADDreamer: CAD Object Generation from Single-View Images", 2025),
    ("2504.14257", "HoLa: B-Rep Generation using a Holistic Latent Representation", 2025),
    ("2503.13110", "DTGBrepGen: A Novel B-Rep Generative Model through Decoupling Topology and Geometry", 2025),
    ("2511.22171", "BrepGPT: Autoregressive B-Rep Generation with Voronoi Half-Patch", 2025),
    ("2512.03018", "AutoBrep: Autoregressive B-Rep Generation with Unified Topology and Geometry", 2025),
    ("2509.21150", "CAD-Tokenizer: Towards Text-based CAD Prototyping via Modality-Specific Tokenization", 2025),
    ("2603.11831", "Towards High-Fidelity CAD Generation via LLM-Driven Program Generation and Text-Based B-Rep Primitive Grounding", 2026),
    ("2602.21105", "BrepGaussian: CAD reconstruction from Multi-View Images with Gaussian Splatting", 2026),
    ("2604.24479", "Zero-to-CAD: Agentic Synthesis of Interpretable CAD Programs at Million-Scale Without Real Data", 2026),
]

out_file='/home/ziyu/Documents/MyDocs/Essay/surface_papers_meta.json'
if os.path.exists(out_file):
    out=json.load(open(out_file))
else:
    out=[]
done={d['arxiv'] for d in out}

for arxiv,title,year in papers:
    if arxiv in done:
        continue
    rec={'arxiv':arxiv,'title':title,'year':year,'authors':[], 'source':''}
    for base in ['https://arxiv.org/html/'+arxiv, 'https://ar5iv.labs.arxiv.org/html/'+arxiv]:
        try:
            html=fetch(base)
            authors=parse_authors(html)
            if authors:
                rec['authors']=authors
                rec['source']=base
                break
        except Exception as e:
            rec.setdefault('errors',[]).append(f'{base}: {type(e).__name__}: {e}')
        time.sleep(0.2)
    out.append(rec)
    with open(out_file,'w') as f:
        json.dump(out,f,indent=2,ensure_ascii=False)
    print(arxiv, 'authors', len(rec['authors']), 'src', rec['source'], flush=True)
    time.sleep(0.3)
print('done')
