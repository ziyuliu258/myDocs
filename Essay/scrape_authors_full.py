import urllib.request, re, json, time
from html.parser import HTMLParser

class AuthorParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_authors=False
        self.depth=0
        self.author_stack=[]
        self.cur_author=None
        self.cur_section=None # 'name','aff','thanks','email'
        self.authors=[]
        self.buf=[]
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        cls=attrs.get('class','')
        if tag=='div' and 'ltx_authors' in cls.split():
            self.in_authors=True
        if not self.in_authors:
            return
        if tag=='span' and 'ltx_creator' in cls.split():
            self.cur_author={'name':'','affs':[],'thanks':[]}
            self.authors.append(self.cur_author)
        if tag=='span' and 'ltx_personname' in cls.split():
            self.cur_section='name'
            self.buf=[]
        elif tag=='span' and 'ltx_role_affiliation' in cls.split():
            self.cur_section='aff'
            self.buf=[]
        elif tag=='span' and 'ltx_role_thanks' in cls.split():
            self.cur_section='thanks'
            self.buf=[]
        elif tag=='span' and 'ltx_role_email' in cls.split():
            self.cur_section='email'
            self.buf=[]
    def handle_endtag(self, tag):
        if not self.in_authors:
            return
        if tag=='div' and self.in_authors and False:
            pass
        if tag=='span':
            if self.cur_section:
                txt=' '.join(''.join(self.buf).split())
                if self.cur_author is not None:
                    if self.cur_section=='name':
                        self.cur_author['name']=txt
                    elif self.cur_section=='aff':
                        self.cur_author['affs'].append(txt)
                    elif self.cur_section=='thanks':
                        self.cur_author['thanks'].append(txt)
                self.cur_section=None
                self.buf=[]
    def handle_data(self, data):
        if self.in_authors and self.cur_section:
            self.buf.append(data)

def fetch(url):
    req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=30).read().decode('utf-8', errors='replace')

def parse(html):
    p=AuthorParser()
    try:
        p.feed(html)
    except Exception:
        pass
    # filter empty
    return [a for a in p.authors if a.get('name')]

papers = [
    ("1703.04079","SurfNet: Generating 3D Shape Surfaces Using Deep Residual Networks",2017),
    ("1901.05103","DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation",2019),
    ("2003.12181","ParSeNet: A Parametric Surface Fitting Network for 3D Point Clouds",2020),
    ("2006.13782","Neural Splines: Fitting 3D Surfaces with Infinitely-Wide Neural Networks",2021),
    ("2104.14547","NURBS-Diff: A Differentiable Programming Module for NURBS",2022),
    ("2201.00112","SurfGen: Adversarial 3D Shape Synthesis with Explicit Surface Discriminators",2022),
    ("2210.14457","ComplexGen: CAD Reconstruction by B-Rep Chain Complex Generation",2022),
    ("2203.13944","SolidGen: An Autoregressive Model for Direct B-Rep Synthesis",2023),
    ("2311.17050","Surf-D: High-Quality Surface Generation for Arbitrary Topologies using Diffusion Models",2024),
    ("2401.15563","BrepGen: A B-Rep Generative Diffusion Model with Structured Latent Geometry",2024),
    ("2411.10848","NeuroNURBS: Learning Efficient Surface Representations for 3D Solids",2024),
    ("2312.04962","Point2CAD: Reverse Engineering CAD Models from 3D Point Clouds",2024),
    ("2409.16294","GenCAD: Image-Conditioned Computer-Aided Design Generation with Transformer-Based Contrastive Representation and Diffusion Priors",2024),
    ("2410.03417","Img2CAD: Conditioned 3D CAD Model Generation from Single Image with Structured Visual Geometry",2024),
    ("2409.17106","Text2CAD: Generating Sequential CAD Models from Beginner-to-Expert Level Text Prompts",2024),
    ("2502.20732","CADDreamer: CAD Object Generation from Single-View Images",2025),
    ("2504.14257","HoLa: B-Rep Generation using a Holistic Latent Representation",2025),
    ("2503.13110","DTGBrepGen: A Novel B-Rep Generative Model through Decoupling Topology and Geometry",2025),
    ("2511.22171","BrepGPT: Autoregressive B-Rep Generation with Voronoi Half-Patch",2025),
    ("2512.03018","AutoBrep: Autoregressive B-Rep Generation with Unified Topology and Geometry",2025),
    ("2509.21150","CAD-Tokenizer: Towards Text-based CAD Prototyping via Modality-Specific Tokenization",2025),
    ("2603.11831","Towards High-Fidelity CAD Generation via LLM-Driven Program Generation and Text-Based B-Rep Primitive Grounding",2026),
    ("2602.21105","BrepGaussian: CAD reconstruction from Multi-View Images with Gaussian Splatting",2026),
    ("2604.24479","Zero-to-CAD: Agentic Synthesis of Interpretable CAD Programs at Million-Scale Without Real Data",2026),
]

out=[]
for arxiv,title,year in papers:
    rec={'arxiv':arxiv,'title':title,'year':year,'authors':[], 'source':''}
    for base in ['https://arxiv.org/html/'+arxiv, 'https://ar5iv.labs.arxiv.org/html/'+arxiv]:
        try:
            html=fetch(base)
            authors=parse(html)
            if authors:
                rec['authors']=authors
                rec['source']=base
                break
        except Exception as e:
            rec.setdefault('errors',[]).append(f'{base}: {type(e).__name__}: {e}')
        time.sleep(0.2)
    out.append(rec)
    with open('/home/ziyu/Documents/MyDocs/Essay/surface_papers_meta_full.json','w') as f:
        json.dump(out,f,indent=2,ensure_ascii=False)
    print(arxiv, 'authors', len(rec['authors']), 'src', rec['source'], flush=True)
    time.sleep(0.3)
print('done')
