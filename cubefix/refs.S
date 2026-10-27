@ Embedded references blob (TextAsset r14 from the game: xor 0x63 + lz4 block + u32 size), served as /refs.
@ r14_mod.bytes is r14.bytes plus the mod menu's cut-content actions (scripts/patch_refs.py).
    .section .rodata
    .global cube_refs
    .global cube_refs_size
    .balign 4
#ifdef CUBE_REFS_SLOT
@ Patcher build (build.ps1 -Slot): an empty slot that patcher/cube_patcher.py fills with r14_mod made from the
@ player's own game files, so the library itself carries no game data.
    .ascii "CUBEREFSLOT1"
    .word CUBE_REFS_SLOT
cube_refs_size:
    .word 0
cube_refs:
    .space CUBE_REFS_SLOT
#else
cube_refs:
    .incbin "../textassets/r14_mod.bytes"
cube_refs_end:
    .balign 4
cube_refs_size:
    .word cube_refs_end - cube_refs
#endif
