void set_sys_border(a)
{
    asm("    call 8859");
}

void set_sys_colors(a)
{
    *ATTRJP = a;
}

void clear_screen()
{
    asm("    call 3435");
}

void init_console()
{
    a = 2;
    asm("    call 5633");
}

void puts(de)
{
    while()
    {
        a = *de;
        if(a == 0)
            return;
        rst(0x10);
        de++;
    }
}

void interrupt_mode1_init()
{
    di();
    ei();
}