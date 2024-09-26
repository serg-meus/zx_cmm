void set_sys_border(a) {
    // a -- border color (0..7)
    asm("    call 8859");
}

void set_sys_colors(a) {
    // a -- attribute code (0..255)
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
    // de -- address of null-terminated string
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
        b ^= 0xff; c ^= 0xff;
        ++bc;
    }
    put_word_unsigned(bc);
}

bool zx_pause(bc) {
    // bc = pause in frames
    asm("    call 7997");  // exits on any key pressed
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

void down_hl(hl) {
    h++;
    (a = h) &= 7;
    if (flag_z) {
        l += 32;
        if (flag_nc) {
            h -= 8;
        }
    }
}

void down_de(de) {
    d++;
    (a = d) &= 7;
    if (flag_z) {
        e += 32;
        if (flag_nc) {
            d -= 8;
        }
    }
}

void screen_addr_by_char_coord_hl(hl) {
    // h - column number (0..31)
    // l - row number (0..23)
    // returns screen addr in hl
    (a = l) &= 7;
    asm("    rrca"); asm("    rrca"); asm("    rrca");
    a += h;
    h = l; l = a;
    (a = h) &= 0x18;
    a |= (ZX_SCREEN_BEG/0x100);
    h = a;
}

void screen_addr_by_char_coord_de(de) {
    // d - column number (0..31)
    // e - row number (0..23)
    // returns screen addr in de
    (a = e) &= 7;
    asm("    rrca"); asm("    rrca"); asm("    rrca");
    a += d;
    d = e; e = a;
    (a = d) &= 0x18;
    a |= (ZX_SCREEN_BEG/0x100);
    d = a;
}

void attribute_addr_by_screen_addr_hl(h) {
    (a = h) &= 0x18;
    asm("    rrca"); asm("    rrca"); asm("    rrca");
    a += ((ZX_SCREEN_BEG + ZX_SCREEN_LEN)/0x100);
    h = a;
}

void attribute_addr_by_screen_addr_de(d) {
    (a = d) &= 0x18;
    asm("    rrca"); asm("    rrca"); asm("    rrca");
    a += ((ZX_SCREEN_BEG + ZX_SCREEN_LEN)/0x100);
    d = a;
}
