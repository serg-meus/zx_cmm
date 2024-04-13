void set_sys_border(a) {
    asm("    call 8859");
}

void set_sys_colors(a) {
    *ZX_ATTR_P = a;
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
            break;
        rst(0x10);
        de++;
    }
}

void putchar(a) {
    rst(0x10);
}

void put_word_unsigned(bc) {
    asm("    call 11563");
    asm("    call 11747");
}

void put_word_signed(bc) {
    if (b & 0x80) {
        putchar(a = '-');
        inv_bc(bc);
        ++bc;
    }
    put_word_unsigned(bc);
}

bool is_space_pressed() {
    a = 0x7f;
    a = in(0xfe);
    a >>= 1;
    return nc;
}

bool is_break_pressed() {
    asm("    call 8020");
    return nc;
}

void zx_sound_beep(hl, de) {
    // hl = 437500/freq_hz - 30.125
    // de = freq_hz*time_s
    asm("    call 949");
}
