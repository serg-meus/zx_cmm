void set_sys_border(a) {
    asm("    call 8859");
}


void set_sys_colors(a) {
    *ATTRJP = a;
}


void clear_screen() {
    asm("    call 3435");
}


void init_console() {
    a = 2;
    asm("    call 5633");
}


void puts(de) {
    while()
    {
        a = *de;
        if(a == 0)
            return;
        rst(0x10);
        de++;
    }
}


void interrupt_mode1_init() {
    di();
    ei();
}


void put_word_unsigned(bc) {
    asm("    call 11563");
    asm("    call 11747");
}


void inv_bc(bc) {
    a = b;
    asm("    cpl");
    b = a;
    a = c;
    asm("    cpl");
    c = a;
}


void inv_hl(hl) {
    a = h;
    asm("    cpl");
    h = a;
    a = l;
    asm("    cpl");
    l = a;
}


void put_word_signed(hl) {
    if(h & 0x80) {
        putchar(a = '-');
        inv_hl(hl);
        ++hl;
    }
    put_word_unsigned(bc = hl);
}


void compare_hl(de) {
    push(hl);
    asm("    sbc hl, de");  // hl -= de gives not optimal result
    a = h;
    a & 0x80;
    pop(hl);
}


void interrupt_model_init() {
    di();
    ei();
}


bool is_space_pressed() {
    a = 0x7f;
    a = in(0xfe);
    a >>= 1;
    return nc;
}


void pause24(bc) {
    do {
        bc--;  // 6 tacts
    } while(flag_nz(a = c) |= b);  // 4 + 4 + 12 = 18 tacts
}
