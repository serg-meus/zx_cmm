void interrupt_mode1_init() {
    di();
    ei();
}

void pause24(bc) {  // uses bc, a
    do {
        bc--;  // 6 tacts
    } while (flag_nz (a = c) |= b);  // 4 + 4 + 12 = 18 tacts
}

void rra(a) {
    asm("    rra");
}

void rla(a) {
    asm("    rla");
}

void rrca(a) {
    asm("    rrca");
}

void rlca(a) {
    asm("    rlca");
}

void memset(hl, bc, a) {
    // hl - start address
    // bc - length in bytes MINUS ONE (!)
    // a - fill value
    de = hl;
    de++;
    *hl = a;
    ldir();
}

void memcpy(hl, de, bc) {
    // hl - from address
    // de - to address
    // bc - lenght in bytes
    ldir();
}