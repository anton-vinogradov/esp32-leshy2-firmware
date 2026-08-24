// Leshy2 SC1512-A4 / RP2354B board identity. No peripheral pins are assigned
// before the reviewed H2 contract is generated into target sources at F2.3.
#ifndef _BOARDS_LESHY2_RP2354B_H
#define _BOARDS_LESHY2_RP2354B_H

pico_board_cmake_set(PICO_PLATFORM, rp2350-arm-s)

#define LESHY2_RP2354B 1
#define PICO_RP2350A 0

// RP2354B contains a stacked 2-MiB flash device compatible with this SDK boot2.
#define PICO_BOOT_STAGE2_CHOOSE_W25Q080 1
#ifndef PICO_FLASH_SPI_CLKDIV
#define PICO_FLASH_SPI_CLKDIV 2
#endif
pico_board_cmake_set_default(PICO_FLASH_SIZE_BYTES, (2 * 1024 * 1024))
#ifndef PICO_FLASH_SIZE_BYTES
#define PICO_FLASH_SIZE_BYTES (2 * 1024 * 1024)
#endif

pico_board_cmake_set_default(PICO_RP2350_A2_SUPPORTED, 1)
#ifndef PICO_RP2350_A2_SUPPORTED
#define PICO_RP2350_A2_SUPPORTED 1
#endif

#endif
