#include "utils.h"

#define COLOR(ink, paper, bright=0, flash=0) \
[ink + 8*paper + 64*bright + 128*flash]

#enum(BLACK = 0, BLUE, RED, MAGENTA, GREEN, CYAN, YELLOW, WHITE)

void main()
{
    set_sys_colors(a=COLOR(ink=WHITE, paper=BLACK));
    set_sys_border(a=BLACK);
    clear_screen();
    init_console();
    puts(de="Hello world!\r");
    set_sys_colors(a=COLOR(ink=YELLOW, paper=BLUE, bright=1));
    init_console();
    puts(de="Who is on duty today?");
}

#include "utils.c"
