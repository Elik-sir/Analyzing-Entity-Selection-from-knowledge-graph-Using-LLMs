"""Convert the active paper to readable Markdown; do not edit scientific text."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[5]
PAPER = ROOT / 'paper/manuscript'
aux = (PAPER/'main.aux').read_text(encoding='utf-8')
labels = dict(re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}', aux))
citations = dict(re.findall(r'\\bibcite\{([^}]+)\}\{\{([^}]*)\}', aux))
main = (PAPER/'main.tex').read_text(encoding='utf-8')


def arg(text, start):
    start = text.index('{', start)
    depth, i = 1, start + 1
    while depth:
        if text[i] in '{}' and (i == 0 or text[i-1] != '\\'):
            depth += 1 if text[i] == '{' else -1
        i += 1
    return text[start+1:i-1], i


def replace_macro(text, name, function):
    pattern = re.compile(r'\\' + name + r'\b')
    while match := pattern.search(text):
        value, end = arg(text, match.end())
        text = text[:match.start()] + function(value) + text[end:]
    return text


def expand(text):
    return re.sub(r'\\input\{([^}]+)\}',
                  lambda m: expand((PAPER/(m.group(1) if Path(m.group(1)).suffix else m.group(1)+'.tex')).read_text(encoding='utf-8')), text)


full = expand(main)
body = full.split(r'\maketitle', 1)[1].split(r'\end{document}', 1)[0]
abstract = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', main, re.S).group(1).strip()
title = re.search(r'\\title(?:\[[^]]*\])?\{([^\n]+)\}', main).group(1)
code_blocks = []
def listing(match):
    text = (PAPER/match.group(1)).read_text(encoding='utf-8')
    code_blocks.append('```cypher\n'+text.rstrip()+'\n```')
    return '@@CODE'+str(len(code_blocks)-1)+'@@'
body = re.sub(r'\\lstinputlisting(?:\[[^]]*\])?\{([^}]+)\}', listing, body)


def plain(text):
    text = replace_macro(text, 'ref', lambda s: labels[s])
    text = replace_macro(text, 'eqref', lambda s: '('+labels[s]+')')
    text = replace_macro(text, 'cite', lambda s: ''.join('[^'+citations[k.strip()]+']' for k in s.split(',')))
    text = replace_macro(text, 'textbf', lambda s: '**'+s+'**')
    text = replace_macro(text, 'emph', lambda s: '*'+s+'*')
    text = replace_macro(text, 'texttt', lambda s: '`'+s+'`')
    text = text.replace('~', ' ').replace(r'\&', '&').replace(r'\%', '%')
    text = re.sub(r'(?<=[0-9a-z])--(?=[0-9a-z])', '–', text)
    return text


images = {
    'motifs_and_raw_recall_bars_v1.pdf': ROOT/'paper/figures/motif_raw_recall_bars_v1/motifs_and_raw_recall_bars.png',
    **{name+'.pdf': ROOT/('paper/figures/recall_manuscript_v1/'+name+'.png') for name in
       ['recall_sizes','recall_motifs','precision_motifs','precision_sizes']}}


def figure(match):
    text = match.group(0)
    image = re.search(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}', text).group(1)
    caption, _ = arg(text, text.index(r'\caption'))
    label = re.search(r'\\label\{([^}]+)\}', text).group(1)
    png = images[Path(image).name]
    assert png.is_file()
    return '\n![Figure '+labels[label]+']('+png.as_posix()+')\n\n**Figure '+labels[label]+'.** '+plain(caption)+'\n'


body = re.sub(r'\\begin\{figure\*?\}.*?\\end\{figure\*?\}', figure, body, flags=re.S)


def table(match):
    text = match.group(0)
    caption, _ = arg(text, text.index(r'\caption'))
    label = re.search(r'\\label\{([^}]+)\}', text).group(1)
    tabular = re.search(r'\\begin\{tabular\}\{[^}]+\}(.*?)\\end\{tabular\}', text, re.S).group(1)
    tabular = replace_macro(tabular, 'shortstack', lambda s: s.replace(r'\\',' '))
    tabular = re.sub(r'\\(?:toprule|midrule|bottomrule)\b', '', tabular)
    rows = [[plain(c.strip()) for c in row.split('&')] for row in tabular.split(r'\\') if '&' in row]
    assert len({len(r) for r in rows}) == 1
    rendered = ['| '+' | '.join(rows[0])+' |', '| '+' | '.join(['---']*len(rows[0]))+' |']
    rendered += ['| '+' | '.join(row)+' |' for row in rows[1:]]
    return '\n**Table '+labels[label]+'.** '+plain(caption)+'\n\n'+'\n'.join(rendered)+'\n'


body = re.sub(r'\\begin\{table\*?\}.*?\\end\{table\*?\}', table, body, flags=re.S)
body = re.sub(r'\\begin\{equation\}(.*?)\\end\{equation\}', lambda m:'\n$$\n'+m.group(1).strip()+'\n$$\n', body, flags=re.S)
body = re.sub(r'\\label\{[^}]+\}', '', body)
body = re.sub(r'\\bibliographystyle\{[^}]+\}', '', body)
body = re.sub(r'\\bibliography\{[^}]+\}', '@@REFERENCES@@', body)
body = body.replace(r'\clearpage', '')
section, subsection, appendix = 0, 0, False
heading = re.compile(r'\\appendix\b|\\(section|subsection|paragraph)\{')
pos = 0; parts = []
while match := heading.search(body, pos):
    parts.append(body[pos:match.start()])
    if match.group(0).startswith(r'\appendix'):
        appendix, section, subsection = True, 0, 0
        parts.append('\n## Appendices\n')
        pos = match.end(); continue
    title_text, end = arg(body, match.start())
    if match.group(1) == 'section':
        section += 1; subsection = 0
        number = chr(64+section) if appendix else str(section)
        prefix = '## '+number+' '
    elif match.group(1) == 'subsection':
        subsection += 1
        number = (chr(64+section) if appendix else str(section))+'.'+str(subsection)
        prefix = '### '+number+' '
    else:
        prefix = '#### '
    parts.append('\n'+prefix+title_text.rstrip('.')+'\n')
    pos = end
parts.append(body[pos:]); body = plain(''.join(parts))
body = body.replace('We ask three questions. **RQ1:**','We ask three questions.\n\n- **RQ1:**').replace(' **RQ2:**','\n- **RQ2:**').replace(' **RQ3:**','\n- **RQ3:**')
body = re.sub(r'(?m)(?<!\\)%.*$', '', body)

# Footnote references use the exact bibliography fields already in the paper.
bib = (PAPER/'references.bib').read_text(encoding='utf-8')
entries = {}
for match in re.finditer(r'@\w+\s*\{\s*([^,\s]+),', bib):
    raw, _ = arg(bib, match.start())
    fields = {}
    for field in re.finditer(r'(\w+)\s*=\s*\{', raw):
        value, _ = arg(raw, field.start())
        fields[field.group(1)] = value.replace('{','').replace('}','')
    entries[match.group(1)] = fields
references = []
for key, number in sorted(citations.items(), key=lambda kv:int(kv[1])):
    f = entries[key]
    author = f.get('author', '').replace(' and ', '; ')
    title_text = f['title']; year = f.get('year','n.d.')
    url = f.get('url')
    source = ' [Source]('+url+').' if url else ''
    references.append('[^'+number+']: '+author+'. ('+year+'). *'+title_text+'*.'+source)
body = body.replace('@@REFERENCES@@', '\n## References\n\n'+'\n\n'.join(references)+'\n')
for i, block in enumerate(code_blocks): body = body.replace('@@CODE'+str(i)+'@@', block)
assert not re.search(r'\\(?:input|label|ref|cite|section|subsection|paragraph|Description|caption|includegraphics)\b', body)
assert 'anonymousToolGraph' not in body and 'Tool-to-KG' not in body
output = '# '+title+'\n\n_Anonymous manuscript._\n\n## Abstract\n\n'+plain(abstract)+'\n\n'+body.strip()+'\n'
(PAPER/'article.md').write_text(output,encoding='utf-8')
print(str(PAPER/'article.md'))
