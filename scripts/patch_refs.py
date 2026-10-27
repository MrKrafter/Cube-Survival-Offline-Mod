"""Mod the references blob served by libcubefix: add actions "cubemod_give_<item>" for every item, among them content
the game ships but never gives (LDoE-era weapons, Christmas/Chinese event gear, strange mushroom, containers). The mod
menu runs them through ActionDescription.Make. (Extra craft recipes are not an option: the craft dialog has a fixed
number of recipe slots and throws on more.)
usage: patch_refs.py   (r14.bytes -> r14_mod.bytes, both in textassets/; r14.bytes comes from extract_r14.py)"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refs_codec

TEXTASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'textassets')
SRC = os.path.join(TEXTASSETS, 'r14.bytes')
DST = os.path.join(TEXTASSETS, 'r14_mod.bytes')
CUT_ITEMS = ['fishing_rod_wooden', 'fishing_rod_professional', 'beretta', 'chinese_sword', 'food_mushroom_strange',
             'container_green', 'container_blue', 'container_red', 'buildingsite_christmas_tree',
             'chest_christmas_tree', 'christmas_santa_workbench', 'santa_christmas_hat', 'santa_christmas_shirt',
             'santa_fur_pants', 'santa_fur_boots', 'raider_bandana', 'backpack_raider', 'chinese_npc_mulan_hat',
             'chinese_npc_mulan_shirt', 'chinese_npc_mulan_pants', 'chinese_npc_mulan_boots',
             # not cut, but only hard Bunker Alfa drops it; the bunker terminal turns it into a coordinates chest
             'bunker_coordinates_floppy']
# Inventory icons the offline build lacks (they came in server-side bundles; the game draws a white square) -> the
# closest icon it has. Checked with all_sprites.py; applies to every item view that uses them, not only cut items.
SPRITE_FALLBACK = {
    'UI/wpn_beretta': 'UI/wpn_glock', 'UI/wpn_beretta_dual': 'UI/wpn_glock', 'UI/christmas_wpn_flaregun': 'UI/wpn_glock',
    'UI/wpn_rifle_m32': 'UI/wpn_shotgun', 'UI/wpn_spear_chinese': 'UI/wpn_spear_wooden',
    'UI/christmas_wpn_staff': 'UI/wpn_spear_wooden', 'UI/wpn_broom': 'UI/wpn_paddle',
    'UI/food_mushroom_strange': 'UI/food_berry', 'UI/food_mushroom_normal': 'UI/food_berry',
    'UI/food_whiskey': 'UI/food_beer', 'UI/res_oil': 'UI/res_gasoline', 'UI/resource_weapon_oil': 'UI/res_gasoline',
    'UI/container_green': 'UI/pass_card_a', 'UI/container_blue': 'UI/pass_card_b', 'UI/container_red': 'UI/pass_card_z',
    'UI/christmas_tree': 'UI/furniture_plant', 'UI/christmas_workbench': 'UI/workbench_bench',
    'UI/furniture_chest_big': 'UI/furniture_chest_16',
    'UI/christmas_hat_santa': 'UI/winter_hat', 'UI/christmas_sweater': 'UI/winter_shirt',
    'UI/halloween_hat': 'UI/thick_hat', 'UI/halloween_hat_2': 'UI/thick_hat', 'UI/cheater_hat': 'UI/thick_hat',
    'UI/basic_boots': 'UI/simple_boots', 'UI/basic_pants': 'UI/simple_pants', 'UI/basic_shirt': 'UI/simple_shirt',
    'UI/coordinates_floppy': 'UI/junk_flashdrive', 'UI/gas_mask': 'UI/tactical_hat', 'UI/diver_mask': 'UI/tactical_hat', 'UI/diver_boots': 'UI/simple_boots',
    'UI/chinese_armor_hat': 'UI/kevlar_hat_1', 'UI/chinese_armor_shirt': 'UI/kevlar_armor_1',
    'UI/chinese_armor_pants': 'UI/kevlar_pants_1', 'UI/chinese_armor_boots': 'UI/kevlar_boots_1',
}
GENERATOR_VIEW = {'sprite': 'UI/generator', 'name': 'inventory_stack_view_generator_name',
                  'description': 'inventory_stack_view_generator_description',
                  'full_description': 'inventory_stack_view_generator_full_description'}


def reward(stack_id, stack):
    if 'max_durability' in stack:  # durability, use_durability (torch), overheat_durability (minigun)
        return {'type': 'durability_inventory_stack', 'stack': stack_id,
                'durability': {'type': 'single', 'amount': stack['max_durability']}}
    if stack['type'] == 'limited':  # a full stack
        return {'type': 'limited_inventory_stack', 'stack': stack_id,
                'amount': {'type': 'single', 'amount': stack.get('max_amount', 1)}}
    return {'type': 'single_inventory_stack', 'stack': stack_id}


def patch(r14):
    """r14 blob -> r14_mod blob (also used by patcher/cube_patcher.py)."""
    R = json.loads(refs_codec.dec(r14))
    # The menu's item list (scripts/item_names.py) gives any stack that is an item; cut items are among them.
    give = [s for s in R['inventory_stacks'] if s in R['items']]
    assert all(item in give for item in CUT_ITEMS)
    for item in give:
        R['actions']['cubemod_give_' + item] = {
            'requirement': {'type': 'true'},
            'price': {'type': 'free'},
            'reward': reward(item, R['inventory_stacks'][item]),
        }
    # SVD and revolver are placeholders: tagged "weapon", so they fit the hand slot, but their items are "resource"
    # with no weapon entry. In hand, CharacterModel.get_Weapon throws InvalidCastException every frame and the global
    # map never finishes loading (softlocked a save). Make them real weapons on top of the closest existing ones.
    for item, base, damage, extra_range in (('rifle_svd', 'rifle_ak47_scope', 2.5, 2), ('revolver', 'glock', 1.6, 0)):
        weapon = dict(R['weapons'][base])
        weapon['damage'] = round(weapon['damage'] * damage)
        weapon['attack_range'] += extra_range
        R['weapons'][item] = weapon
        R['weapon_views'][item] = dict(R['weapon_views'][base])
        R['items'][item] = {'type': 'weapon', 'weapon': item}
    # The tactical backpack is craftable but its item has no equip behaviour, so wearing it adds no cells. Small and
    # big backpacks give 5 and 10 cells; this one gets 15, all the inventory screen shows (unused backpack_16 has 20,
    # the last 5 would be invisible).
    R['inventories']['backpack_15'] = {'cells': {str(i): {'type': 'simple'} for i in range(15)}}
    R['inventories_view']['backpack_15'] = dict(R['inventories_view']['backpack_16'])
    R['items']['backpack_military']['equip_behaviour'] = {'type': 'backpack', 'inventory': 'backpack_15'}
    # The portable generator carried to the watch tower has a placeholder view (no sprite, "Cargo pants" texts).
    R['inventory_stack_view']['watch_tower_generator'].update(GENERATOR_VIEW)
    icons = 0
    for view in R['inventory_stack_view'].values():
        if isinstance(view, dict) and view.get('sprite') in SPRITE_FALLBACK:
            view['sprite'] = SPRITE_FALLBACK[view['sprite']]
            icons += 1
    print('icons replaced:', icons, 'actions added:', len(give))
    raw = json.dumps(R, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    return refs_codec.enc(raw)


def main():
    open(DST, 'wb').write(patch(open(SRC, 'rb').read()))
    print('->', DST, os.path.getsize(DST))


if __name__ == '__main__':
    main()
