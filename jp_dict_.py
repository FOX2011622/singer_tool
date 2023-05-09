vs = ['a', 'i', 'u', 'e', 'o']
cs = ['k', 's', 't', 'n', 'h', 'f', 'm', 'y', 'v', 'r', 'v', 'g', 'z', 'd', 'b', 'p', 'w',
      'ky', 'sh', 'j', 'ch', 'ny', 'hy', 'by', 'py', 'my', 'ry',
      'wh', 'qy', 'qw', 'sy', 'sw', 'ts', 'th', 'tw', 'dy', 'dh', 'dw', 'fy', 'fw', 'vy', 'ty', 'gy']
with open('jp_mfa_ext_dict.txt', 'w', encoding='utf-8') as f:
    f.write("n\tN\n")
    for v in vs:
        f.write(f"{v}\t{v}\n")
    for c in cs:
        for v in vs:
            f.write(f"{c}{v}\t{c} {v}\n")
    for c in cs:
        for v in vs:
            f.write(f"{c[0]}{c}{v}\tcl {c} {v}\n")
