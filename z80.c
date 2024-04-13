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

bool hl_is_bigger_de(hl, de) {
    push(hl);
    hl -= de;
    a = h;
    a &= 0x80;
    pop(hl);
    return nz;
}

bool hl_is_bigger_than(hl, bc) {
    push(hl);
    hl -= bc;
    a = h;
    a &= 0x80;
    pop(hl);
    return nz;
}

void interrupt_mode1_init() {
    di();
    ei();
}

void pause24(bc ) {  // uses bc, a
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
