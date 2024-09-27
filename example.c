#include "zx.h"

void main()
{
    set_sys_colors(a=ZX_ATTR(ink=ZX_YELLOW, paper=ZX_BLUE, bright=1));
    set_sys_border(a=ZX_BLUE);
    clear_screen();
    init_console();
    puts(de="Hello world!\r\r");

    set_sys_colors(a=ZX_ATTR(ink=ZX_CYAN, paper=ZX_BLUE));
    init_console();
    puts(de="Nested loop example:\r\r");
    for b = 0: 0x07  {
        for c = 7:0:-1
        {
            a = get_attr(c);
            set_sys_colors(a);
            init_console();
            putchar(a='.');
        }
        putchar(a=0x0d); // '\r'
    }
}

int get_attr(c) {
    // c - reversed symbol counter (7..0)
    (((a = c) ^= 0x0f) <<= 3) |= c;
    return a;
}