cpus = '3900x vs i5-2500s'
cpu_div = [i.strip().lower().replace('amd', '').replace('intel', '') for i in cpus.replace('VS', 'vs').split('vs') if len(i) > 0]

with open('bench_cpu.csv', 'r') as f:
    cpulist = {}
    for ln in f.read().splitlines()[1:]:
        v = ln.split(',')
        name = v[3]
        if v[2].lower() == 'intel':
            name.replace('core', '')
        cpulist[name.lower()] = {'type': v[0], 'partid': v[1], 'brand':v[2], 'proper_name':v[3], 'rank': v[4], 'bench': v[5], 'samples': v[6], 'url': v[7]}

def try_getting(name):
    try:
        return cpulist[name]
    except KeyError:
        return None

cpu_data = []
for cpu_name in cpu_div:
    cpu_name = cpu_name.strip()

    print(f'=== {cpu_name} ===')
    candidates = []
    data = try_getting(cpu_name) or try_getting('core '+cpu_name)
    if data is None:
        candidates = [k for k in cpulist.keys() if (cpu_name.replace(' ', '').replace('-', '') in k.replace(' ', '').replace('-', ''))]
        if len(candidates) == 0:
            print('Unknown.')
            data = None
        elif len(candidates) == 1:
            data = cpulist[candidates[0]]
        else:
            print(f'Candidates: {", ".join([cpulist[k]["proper_name"] for k in candidates])}')
            data = None

    cpu_data.append([data, candidates])