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
