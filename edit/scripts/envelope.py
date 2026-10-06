import soundfile as sf, numpy as np, json
def env10(path):
    x, sr = sf.read(path)
    if x.ndim > 1: x = x.mean(1)
    w = int(0.010*sr); n = len(x)//w
    rms = 20*np.log10(np.sqrt((x[:n*w].reshape(n, w)**2).mean(1)) + 1e-12)
    return rms, sr
def words_from_parakeet(path):
    toks = json.load(open(path)); words=[]; cur=None
    for d in toks:
        if d['tok'].startswith(' ') or cur is None:
            if cur: words.append(cur)
            cur = {'w': d['tok'].strip(), 's': d['t'], 'e': d['t']}
        else:
            cur['w'] += d['tok']; cur['e'] = d['t']
    words.append(cur); return words
