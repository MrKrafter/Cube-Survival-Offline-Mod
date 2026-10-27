@ Telegram icon for the Settings button that used to be Facebook's "Dev blog" (mods.c, tools/make_tg_icon.py).
    .section .rodata
    .global cube_tg_png
    .global cube_tg_png_size
    .balign 4
cube_tg_png:
    .incbin "telegram.png"
cube_tg_png_end:
    .balign 4
cube_tg_png_size:
    .word cube_tg_png_end - cube_tg_png
