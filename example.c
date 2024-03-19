#include "utils.h"

#define ZX_COLOR(ink, paper, bright=0, flash=0) \
[ink + 8*paper + 64*bright + 128*flash]

#enum(BLACK = 0, BLUE, RED, MAGENTA, GREEN, CYAN, YELLOW, WHITE)


void main()
{
    set_sys_colors(a=ZX_COLOR(ink=YELLOW, paper=BLACK, bright=1));
    set_sys_border(a=BLACK);
    clear_screen();
    init_console();
    puts(de="Hello world!\r\r");

    set_sys_colors(a=ZX_COLOR(ink=CYAN, paper=BLACK));
    init_console();
    puts(de="Nested loop example:\r\r");
    for b = 0:7  {
        for c = 7:0:-1
        {
            a = c; a ^= 0x0f; a <<= 3; a |= c;
            set_sys_colors(a);
            init_console();
            putchar(a='.');
        }
        putchar(a=0x0d); // '\r'
    }
}

#include "utils.c"
