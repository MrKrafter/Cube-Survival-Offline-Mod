"""Verify that every replacement icon in patch_refs.SPRITE_FALLBACK exists in the game assets.  usage: check_fallback.py"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.argv = sys.argv[:1] + ['--none--']
import all_sprites
from patch_refs import SPRITE_FALLBACK

bad = sorted({v for v in SPRITE_FALLBACK.values() if not all_sprites.present(v)})
print('missing replacements:', bad or 'none')
