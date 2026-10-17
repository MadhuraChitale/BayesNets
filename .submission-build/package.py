"""Build the two submission artifacts using only the Python standard library."""
from pathlib import Path
import textwrap
import zipfile

root = Path(__file__).resolve().parents[1]
paragraphs = [
    'Project 03: Bayes Nets - Implementation Report',
    'Q1: Bayes Net Structure',
    'Constructed Pacman, Ghost0, Ghost1, Observation0, and Observation1. Each observation has Pacman and its corresponding ghost as parents. Position domains include every grid cell, including walls. Observation domains range from zero through width + height - 2 + MAX_NOISE, inclusive. The supplied 4-by-3 grid test passes, including the expected observation range 0 through 12.',
    'Q2: Join Factors',
    'The result uses the union of unconditioned variables and the union of conditioned variables minus any unconditioned variables. Each result entry multiplies the matching input entries without normalizing. The full domain dictionary is preserved. The supplied Badge/Alarm test passes. An additional test joins unnormalized factors sharing a conditioned variable: constant entries 2 and 3 produce entries 6.',
    'Q3: Eliminate',
    'Created a new factor without the eliminated unconditioned variable. For each retained assignment, summed input probabilities over the eliminated variable domain. Conditioned variables and the complete domain dictionary are preserved. The supplied Zone/Badge/Alarm test passes. The additional unnormalized test sums two entries of 6 to obtain 12.',
    'Q4: Variable Elimination',
    'Restricted CPTs using evidence, then joined factors containing each hidden variable in the requested order and immediately eliminated that variable. As required, a joined factor with only one unconditioned variable is discarded. Joined the remaining factors and used the supplied normalize function. The supplied Fuel posterior test passes: P(full | lit) = 111/202 and P(low | lit) = 91/202.',
    'Validation',
    'Commands: python test_q1to4.py and python test_additional.py. All four supplied examples pass. Additional tests use ten reproducible randomized A -> C <- B, C -> D networks and compare 150 query/evidence/elimination-order combinations with enumeration. They also check default orders, join/eliminate interleaving, the independent-root discard case, unnormalized factors, retained domain dictionaries, and None for zero-mass results. The supplied example script was preserved. No TA grading suite was available, and the graphical demo was not used as a correctness test.',
    'Critical Analysis of Variable Elimination',
    'All 150 comparisons agree with enumeration to absolute tolerance 1e-12, supporting equivalence on these small models. Enumeration builds a full joint before marginalizing; variable elimination sums out hidden variables earlier and can avoid that full table. Order affects intermediate factor size: when querying A given D, eliminating B first joins scopes {B} and {A,B,C}, producing a three-variable table, then {A,C,D}. Eliminating C first joins {A,B,C} with {C,D}, producing a four-variable table. For this binary example these peak tables have 8 versus 16 rows before evidence restriction; restricting D to one value reduces the latter to 8. Evidence and order therefore both affect work. Dense networks can still require exponentially large intermediate factors. These tests establish neither a runtime speedup nor scalability, because no timing or large-network benchmark was performed. The implementation honors the supplied order rather than selecting an optimized one.'
]
lines = []
for paragraph in paragraphs:
    lines.extend(textwrap.wrap(paragraph, width=96))
    lines.append('')
pages = [lines[i:i+57] for i in range(0, len(lines), 57)]
objects = [b'<< /Type /Catalog /Pages 2 0 R >>', b'',
           b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>']
kids = []
for page in pages:
    page_id = len(objects) + 1
    stream_id = page_id + 1
    kids.append(f'{page_id} 0 R')
    objects.append(f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents {stream_id} 0 R >>'.encode())
    commands = ['BT /F1 10 Tf 13 TL 42 750 Td']
    for line in page:
        escaped = line.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
        commands.append(f'({escaped}) Tj T*')
    commands.append('ET')
    stream = '\n'.join(commands).encode('ascii')
    objects.append(f'<< /Length {len(stream)} >>\nstream\n'.encode() + stream + b'\nendstream')
objects[1] = f'<< /Type /Pages /Kids [{" ".join(kids)}] /Count {len(kids)} >>'.encode()
data = bytearray(b'%PDF-1.4\n')
offsets = [0]
for index, obj in enumerate(objects, 1):
    offsets.append(len(data))
    data.extend(f'{index} 0 obj\n'.encode() + obj + b'\nendobj\n')
xref = len(data)
data.extend(f'xref\n0 {len(objects)+1}\n0000000000 65535 f \n'.encode())
for offset in offsets[1:]:
    data.extend(f'{offset:010d} 00000 n \n'.encode())
data.extend(f'trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode())
(root / 'submission' / 'Project3_Report.pdf').write_bytes(data)
with zipfile.ZipFile(root / 'submission' / 'Project3_BayesNets.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root)
        if any(part.startswith('.') or part in {'__pycache__', 'submission'} for part in relative.parts):
            continue
        if path.is_file() and path.suffix != '.pyc':
            archive.write(path, Path('bayesnets') / relative)
print(f'Created {len(pages)}-page report and project ZIP.')
