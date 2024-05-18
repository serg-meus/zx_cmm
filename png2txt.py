from sys import argv
from PIL.PngImagePlugin import PngImageFile as png


def main(in_file, spr_width, spr_height, array_names, out_file):
    array_names = array_names.replace(';', ',').replace('|', ',')
    names = array_names.split(',')
    with open(out_file, 'w') as out_fp:
        with open(in_file, 'rb') as in_fp:
            img = png(in_fp)
            sprites_per_row = int(img.width/int(spr_width))
            sprites_per_col = int(img.height/int(spr_height))
            arr_len = int(int(spr_width)/8*int(spr_height))
            if len(names) == 1:
                arr_len *= sprites_per_col*sprites_per_row
            i = 0
            for row in range(sprites_per_row):
                for col in range(sprites_per_col):
                    spr = str(get_sprite(img, row*int(spr_width),
                                         col*int(spr_height),
                                         int(spr_width),
                                         int(spr_height)))[1:-1]
                    name = names[0] if len(names) <= 1 else names[i]
                    i += 1

                    if len(names) > 1:
                        out_fp.write('uint8_t ' + name + '[' + str(arr_len) +
                                     '] = {' + spr + '};\n')
                    elif i == 1:
                        out_fp.write('uint8_t ' + name + '[' + str(arr_len) +
                                     '] = {' + spr)
                    elif i < sprites_per_row*sprites_per_col:
                        out_fp.write(spr + ', ')
                    else:
                        out_fp.write(spr + '};\n')


def get_sprite(img, row, col, spr_width, spr_height):
    ans = []
    for y in range(spr_height):
        for x in range(int(spr_width/8)):
            ans.append(get_byte(img, row + 8*x, col + y))
    return ans


def get_byte(img, x, y):
    ans = 0
    for shft in range(8):
        ans *= 2
        if sum(img.getpixel((x + shft, y))) < 128*3:
            ans += 1
    return ans

if __name__ == '__main__':
    main(argv[1], argv[2], argv[3], argv[4], argv[5])
