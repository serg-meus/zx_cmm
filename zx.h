#define ZX_ATTR_CODE(ink, paper, bright=0, flash=0) \
[ink + 8*paper + 64*bright + 128*flash]

#enum(ZX_BLACK = 0, ZX_BLUE, ZX_RED, ZX_MAGENTA, ZX_GREEN, ZX_CYAN, \
ZX_YELLOW, ZX_WHITE)

const int SCREEN_BEG = 0x4000;
const int SCREEN_LEN = 32*192;
const int ATTRJP = 23693;

const int ZX128_PORT = 0x7ffd;
const int ZX128_RAM0 = 0;
const int ZX128_RAM1 = 1;
const int ZX128_RAM2 = 2;
const int ZX128_RAM3 = 3;
const int ZX128_RAM4 = 4;
const int ZX128_RAM5 = 5;
const int ZX128_RAM6 = 6;
const int ZX128_RAM7 = 7;
const int ZX128_SCREEN128 = 8;
const int ZX128_SCREEN48 = 0;
const int ZX128_ROM128 = 0;
const int ZX128_ROM48 = 16;
const int ZX128_CONFIG128 = 0;
const int ZX128_CONFIG48 = 32;

const int PENT1024_PORT = 0xeff7;
const int PENT1024_4BITS = 1;
const int PENT1024_512x192 = 2;
const int PENT1024_CFG128 = 4;
const int PENT1024_RAM0 = 8;
const int PENT1024_NOTURBO = 16;
const int PENT1024_MCOLOR = 32;
const int PENT1024_384x304 = 64;
const int PENT1024_CMOS = 128;

const int CALC_XCH = 1;
const int CALC_SUB = 3;
const int CALC_MUL = 4;
const int CALC_DIV = 5;
const int CALC_POW = 6;
const int CALC_ADD = 15;
const int CALC_MINUS = 27;
const int CALC_INT = 39;
const int CALC_SQRT = 40;
const int CALC_SIGN = 41;
const int CALC_ABS = 42;
const int CALC_COPY = 49;
const int CALC_END = 56;
const int CALC_ROUND = 88;
const int CALC_PUSH_0 = 160;
const int CALC_PUSH_1 = 161;
const int CALC_PUSH_0_5 = 162;
const int CALC_PUSH_PI_2 = 163;
const int CALC_PUSH_10 = 164;