import vapoursynth as vs
core = vs.get_core()

def shiftxy(src,x,y):
    if x >= 0:
        if y >= 0:
            dst = src.std.Crop(right = x,bottom= y).std.AddBorders(left = x,top = y)
        else:
            dst = src.std.Crop(right = x,top=-y).std.AddBorders(left = x,bottom =-y)
    else:
        if y >= 0:
            dst = src.std.Crop(left =-x,bottom= y).std.AddBorders(right =-x,top = y)
        else:
            dst = src.std.Crop(left =-x,top=-y).std.AddBorders(right =-x,bottom =-y)
    return dst

def r_g_b(src):
    r = src.std.ShufflePlanes(0,vs.GRAY)
    g = src.std.ShufflePlanes(1,vs.GRAY)
    b = src.std.ShufflePlanes(2,vs.GRAY)
    return [r,g,b]

def rgb(channels):
    return core.std.ShufflePlanes(channels,[0,0,0],vs.RGB).resize.Spline36(format=vs.RGBS)

def ccd(src,threshold=5,shownoise=False):
    borderl = src.std.Crop(right=src.width-12)
    borderr = src.std.Crop(left=src.width-12)
    bordert = src.std.Crop(bottom=src.height-12)
    borderb = src.std.Crop(top=src.height-12)
    corner1 = borderl.std.Crop(bottom=src.height-12)
    corner2 = borderr.std.Crop(bottom=src.height-12)
    corner3 = borderl.std.Crop(top=src.height-12)
    corner4 = borderr.std.Crop(top=src.height-12)
    exp = core.std.StackVertical([\
            core.std.StackHorizontal([corner1,bordert,corner2]),\
            core.std.StackHorizontal([borderl,  src  ,borderr]),\
            core.std.StackHorizontal([corner3,borderb,corner4])])\
            .resize.Spline36(format=vs.RGBS)
    [r,g,b] = r_g_b(exp)

    thr = threshold**2/195075.0
    expr1 = "x a - 2 pow y b - 2 pow + z c - 2 pow + {} < 1 0 ?".format(thr)
    expr2 = "y 0 > x 0 ?"
    expr3 = "x y + z + a + b + c + d + e + f + g + h + i + j + k + l + m + 1 +"
    expr4 = "x y + z + a + b + c + d + e + f + g + h + i + j + k + l + m + n + o /"
    x = -12
    for i in range(4):
        y = -12
        for j in range(4):
            n = str(i*4+j+1).zfill(2)
            [globals()["r"+n],globals()["g"+n],globals()["b"+n]] = r_g_b(shiftxy(exp,x,y))
            globals()["d"+n] = core.std.Expr([r,g,b,globals()["r"+n],globals()["g"+n],globals()["b"+n]],[expr1])
            [globals()["r"+n],globals()["g"+n],globals()["b"+n]] = [\
                    core.std.Expr([globals()[c+n],globals()["d"+n]],[expr2])\
                    for c in ['r','g','b']]
            globals()["c"+n] = rgb([globals()[c+n] for c in ['r','g','b']])
            y += 8
        x += 8
    den = core.std.Expr([d01,d02,d03,d04,d05,d06,d07,d08,d09,d10,d11,d12,d13,d14,d15,d16],[expr3])
    den = rgb([den,den,den])
    avg = core.std.Expr([exp,c01,c02,c03,c04,c05,c06,c07,c08,c09,c10,c11,c12,c13,c14,c15,c16,den],[expr4,expr4,expr4])\
            .std.Crop(left=12,right=12,top=12,bottom=12).resize.Spline36(format=vs.RGBS)
    dst = core.resize.Spline36(avg,format=vs.YUV420P8,matrix_s='170m')
    if shownoise:
        dst = core.std.Expr([src,dst],["0", "x y - 128 +"])
    else:
        dst = core.std.ShufflePlanes([src,dst],[0,1,2],colorfamily=vs.YUV)
    return dst
