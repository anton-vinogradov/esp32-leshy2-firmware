// Leshy2 SC1512-A4 / RP2354B board identity. F2-R2.2 intentionally assigns
// no peripheral pins; F2-R2.3 generates the Hub-RP hardware domain.
#ifndef _BOARDS_LESHY2_HUB_RP2354B_H
#define _BOARDS_LESHY2_HUB_RP2354B_H

pico_board_cmake_set(PICO_PLATFORM, rp2350-arm-s)

#define LESHY2_HUB_RP2354B 1
#define PICO_RP2350A 0

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
