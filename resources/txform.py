import torch

def _fast_cross(a, b):
    return torch.cat([
        a[...,1:2]*b[...,2:3] - a[...,2:3]*b[...,1:2],
        a[...,2:3]*b[...,0:1] - a[...,0:1]*b[...,2:3],
        a[...,0:1]*b[...,1:2] - a[...,1:2]*b[...,0:1]], dim=-1)

def mul(x, y):
    return torch.matmul(x, y)
    
def mul_vec(x, v):
    return torch.matmul(x, v[...,None])[...,0]

def from_xy(x):

    r2 = _fast_cross(x[...,0], x[...,1])
    r2 = r2 / torch.sqrt(torch.sum(torch.square(r2), dim=-1))[...,None]
    r1 = _fast_cross(r2, x[...,0])
    r1 = r1 / torch.sqrt(torch.sum(torch.square(r1), dim=-1))[...,None]
    
    return torch.cat([
        x[...,0:1], 
        r1[...,None], 
        r2[...,None]], dim=-1)

def fk_vel(lrot, lpos, lvel, lang, parents):
    
    gp, gr, gv, ga = [lpos[...,:1,:]], [lrot[...,:1,:,:]], [lvel[...,:1,:]], [lang[...,:1,:]]
    for i in range(1, len(parents)):
        gp.append(mul_vec(gr[parents[i]], lpos[...,i:i+1,:]) + gp[parents[i]])
        gr.append(mul    (gr[parents[i]], lrot[...,i:i+1,:,:]))
        gv.append(mul_vec(gr[parents[i]], lvel[...,i:i+1,:]) + 
            torch.cross(ga[parents[i]], mul_vec(gr[parents[i]], lpos[...,i:i+1,:]), dim=-1) +
            gv[parents[i]])
        ga.append(mul_vec(gr[parents[i]], lang[...,i:i+1,:]) + ga[parents[i]])
        
    return (
        torch.cat(gr, dim=-3), 
        torch.cat(gp, dim=-2),
        torch.cat(gv, dim=-2),
        torch.cat(ga, dim=-2))
        