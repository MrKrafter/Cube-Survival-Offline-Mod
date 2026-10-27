package cube.mod;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.graphics.Typeface;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.ScrollView;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;

import java.lang.reflect.InvocationHandler;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.util.ArrayList;
import java.util.Locale;

/** Mod menu opened from the game's settings ("Support" button). Values live in SharedPreferences and
 * are pushed to libcubefix, which applies them in its il2cpp hooks. */
public final class ModMenu {
    // Option ids shared with mods.c (enum mod_id).
    static final int SPEED = 0, GOD = 1, DUPE = 2, FREE_SHOP = 3, FREE_TRAVEL = 4, UNLOCK = 5, FREE_CRAFT = 6,
            NO_ADS = 7, NO_DURABILITY = 8, INSTANT_WORK = 9, ONE_HIT = 10, FAST_ATTACK = 11, INSTANT_LOOT = 12,
            BUNKER = 13, UNLOCK_RESEARCH = 14, NOCLIP = 15, FREEZE_EVENTS = 16, FREE_ASSEMBLY = 17, HIDE_UI = 18;
    private static final int LAST_OPTION = HIDE_UI;

    static native void nativeSet(int id, int value);
    static native int nativeSpawn(String eventId);
    static native int nativeGive(String item);
    static native int nativeRestoreNext();

    // Global map events that can be spawned: id, Russian name, English name. The horde is left out on purpose, and so
    // are siege and counter siege: they need another player's base from the (dead) raid server.
    private static final String[][] EVENTS = {
        {"airdrop", "Аирдроп", "Airdrop"},
        {"trader", "Торговец", "Trader"},
        {"aircraft", "Место крушения самолёта", "Aircraft crash site"},
        {"gas_station", "Заправка", "Gas station"},
        {"bike", "Байкер", "Biker"},
        {"chest_coordinates_1", "Сундук по координатам 1", "Coordinates chest 1"},
        {"chest_coordinates_2", "Сундук по координатам 2", "Coordinates chest 2"},
        {"chest_coordinates_3", "Сундук по координатам 3", "Coordinates chest 3"},
        {"self_raid_event", "Рейд на свою базу", "Raid on own base"},
    };
    // Events the game has but never starts (requirement false / holiday only).
    private static final String[][] CUT_EVENTS = {
        {"chinese_event", "Китайский ивент (Мулан)", "Chinese event (Mulan)"},
        {"christmas_event", "Рождественский ивент (Санта)", "Christmas event (Santa)"},
    };
    // Items the game has but never hands out; given by the actions scripts/patch_refs.py adds.
    private static final String[][] CUT_ITEMS = {
        {"fishing_rod_wooden", "Удочка деревянная", "Wooden fishing rod"},
        {"fishing_rod_professional", "Удочка профессиональная", "Professional fishing rod"},
        {"beretta", "Пистолет Беретта", "Beretta pistol"},
        {"chinese_sword", "Китайский меч", "Chinese sword"},
        {"food_mushroom_strange", "Странный гриб", "Strange mushroom"},
        {"container_green", "Зелёный контейнер", "Green container"},
        {"container_blue", "Синий контейнер", "Blue container"},
        {"container_red", "Красный контейнер", "Red container"},
        {"buildingsite_christmas_tree", "Новогодняя ёлка", "Christmas tree"},
        {"chest_christmas_tree", "Ёлка-сундук", "Christmas tree chest"},
        {"christmas_santa_workbench", "Верстак Санты", "Santa's workbench"},
        {"santa_christmas_hat", "Шапка Санты", "Santa hat"},
        {"santa_christmas_shirt", "Свитер Санты", "Santa sweater"},
        {"santa_fur_pants", "Меховые штаны Санты", "Santa fur pants"},
        {"santa_fur_boots", "Меховые сапоги Санты", "Santa fur boots"},
        {"raider_bandana", "Бандана рейдера", "Raider bandana"},
        {"backpack_raider", "Рюкзак рейдера", "Raider backpack"},
        {"chinese_npc_mulan_hat", "Шляпа Мулан", "Mulan hat"},
        {"chinese_npc_mulan_shirt", "Рубаха Мулан", "Mulan shirt"},
        {"chinese_npc_mulan_pants", "Штаны Мулан", "Mulan pants"},
        {"chinese_npc_mulan_boots", "Сапоги Мулан", "Mulan boots"},
        {"bunker_coordinates_floppy", "Дискета с координатами (для терминала бункера)",
            "Coordinates floppy (for the bunker terminal)"},
    };

    private static final String PREFS = "cubemod";
    private static final int SPEED_MIN = 10, SPEED_MAX = 50; // tenths: 1.0x .. 5.0x
    // Three taps this close in time in the top-left square open the menu too.
    private static final int CORNER_DP = 64;
    private static final long TAP_GAP_MS = 500;
    private static Activity activity;
    private static boolean RU = Locale.getDefault().getLanguage().equals("ru");
    private static int cornerTaps;
    private static long lastCornerTap;

    private ModMenu() {}

    private static String t(String ru, String en) {
        return RU ? ru : en;
    }

    private static SharedPreferences prefs() {
        return activity.getSharedPreferences(PREFS, Activity.MODE_PRIVATE);
    }

    /** Called from MainActivity.onCreate after libcubefix is loaded. */
    public static void init(Activity a) {
        activity = a;
        SharedPreferences p = prefs();
        nativeSet(SPEED, p.getInt("speed", SPEED_MIN));
        // a hidden interface is for one recording session, the game always starts with it shown
        p.edit().putBoolean("opt" + HIDE_UI, false).apply();
        for (int id = GOD; id <= LAST_OPTION; id++)
            nativeSet(id, p.getBoolean("opt" + id, false) ? 1 : 0);
        if (p.contains("ru"))
            RU = p.getBoolean("ru", RU);
        watchCornerTaps(a.getWindow());
    }

    /** Puts a proxy in front of the window callback (the activity) that sees every touch first and passes it on. */
    private static void watchCornerTaps(Window w) {
        final Window.Callback orig = w.getCallback();
        if (orig == null)
            return;
        Object proxy = Proxy.newProxyInstance(Window.Callback.class.getClassLoader(),
                new Class<?>[] {Window.Callback.class}, new InvocationHandler() {
            @Override
            public Object invoke(Object self, Method m, Object[] args) throws Throwable {
                if (m.getName().equals("dispatchTouchEvent") && args != null && args.length == 1)
                    onTouch((MotionEvent) args[0]);
                try {
                    return m.invoke(orig, args);
                } catch (InvocationTargetException e) {
                    throw e.getCause();
                }
            }
        });
        w.setCallback((Window.Callback) proxy);
    }

    private static void onTouch(MotionEvent e) {
        if (e.getActionMasked() != MotionEvent.ACTION_DOWN)
            return;
        long now = e.getEventTime();
        if (e.getX() > dp(CORNER_DP) || e.getY() > dp(CORNER_DP) || now - lastCornerTap > TAP_GAP_MS)
            cornerTaps = 0;
        if (e.getX() > dp(CORNER_DP) || e.getY() > dp(CORNER_DP))
            return;
        lastCornerTap = now;
        if (++cornerTaps == 3) {
            cornerTaps = 0;
            show();
        }
    }

    /** Called from native code (any thread); ru is the game's current UI language. */
    public static void open(boolean ru) {
        if (activity == null)
            return;
        RU = ru;
        prefs().edit().putBoolean("ru", ru).apply();
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                show();
            }
        });
    }

    private static int dp(int v) {
        return (int) TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, v, activity.getResources().getDisplayMetrics());
    }

    private static void addHeader(LinearLayout root, String text) {
        TextView h = new TextView(activity);
        h.setText(text);
        h.setTextSize(TypedValue.COMPLEX_UNIT_SP, 14);
        h.setTypeface(Typeface.DEFAULT_BOLD);
        h.setTextColor(Color.GRAY);
        h.setPadding(0, dp(12), 0, dp(2));
        root.addView(h);
    }

    private static void addOption(LinearLayout root, final int id, String text) {
        CheckBox cb = new CheckBox(activity);
        cb.setText(text);
        cb.setTextSize(TypedValue.COMPLEX_UNIT_SP, 16);
        cb.setChecked(prefs().getBoolean("opt" + id, false));
        cb.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton b, boolean on) {
                prefs().edit().putBoolean("opt" + id, on).apply();
                nativeSet(id, on ? 1 : 0);
            }
        });
        root.addView(cb);
    }

    private static void addButton(LinearLayout root, String text, View.OnClickListener l) {
        Button b = new Button(activity);
        b.setText(text);
        b.setOnClickListener(l);
        root.addView(b);
    }

    private static void addNote(LinearLayout root, String text) {
        TextView note = new TextView(activity);
        note.setText(text);
        note.setTextColor(Color.GRAY);
        note.setPadding(0, dp(4), 0, dp(4));
        root.addView(note);
    }

    private static LinearLayout column() {
        LinearLayout root = new LinearLayout(activity);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(20), dp(8), dp(20), dp(8));
        return root;
    }

    private static void dialog(String title, LinearLayout root) {
        ScrollView scroll = new ScrollView(activity);
        scroll.addView(root);
        new AlertDialog.Builder(activity)
                .setTitle(title)
                .setView(scroll)
                .setPositiveButton(t("Закрыть", "Close"), null)
                .show();
    }

    private static void spawn(String id) {
        int known = nativeSpawn(id);
        Toast.makeText(activity, known != 0 ? t("Ивент появится на карте", "The event will appear on the map")
                : t("Откройте карту — ивент появится там", "Open the map, the event will appear there"),
                Toast.LENGTH_SHORT).show();
    }

    private static void confirmRollback() {
        new AlertDialog.Builder(activity)
                .setTitle(t("Откатить сейв?", "Roll back the save?"))
                .setMessage(t("Игра закроется, а при запуске вернётся к моменту перед последним входом в локацию "
                        + "(или выходом на карту). Всё, что было после, пропадёт.",
                        "The game closes and starts from the moment before the last location entry (or return "
                        + "to the map). Everything after that is lost."))
                .setPositiveButton(t("Откатить", "Roll back"), new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface d, int which) {
                        if (nativeRestoreNext() == 0) {
                            Toast.makeText(activity, t("Копии сейва ещё нет", "No save copy yet"),
                                    Toast.LENGTH_SHORT).show();
                            return;
                        }
                        activity.finishAffinity();
                        android.os.Process.killProcess(android.os.Process.myPid());
                    }
                })
                .setNegativeButton(t("Отмена", "Cancel"), null)
                .show();
    }

    /** Called from native code (any thread): 1 = save restored after a hung load, 2 = safe mode. */
    public static void notice(final int code) {
        if (activity == null)
            return;
        if (code == 2) {
            SharedPreferences.Editor e = prefs().edit();
            for (int id = GOD; id <= LAST_OPTION; id++)
                e.putBoolean("opt" + id, false);
            e.putInt("speed", SPEED_MIN).apply();
        }
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                Toast.makeText(activity, code == 2
                        ? t("Загрузка снова не прошла: все функции мод-меню выключены",
                            "The load failed again: all mod menu options are switched off")
                        : t("Прошлая загрузка зависла — сейв откатен к моменту до неё",
                            "The last load hung: the save was rolled back to before it"),
                        Toast.LENGTH_LONG).show();
            }
        });
    }

    private static void showEventList(final String[][] events) {
        String[] names = new String[events.length];
        for (int i = 0; i < events.length; i++)
            names[i] = RU ? events[i][1] : events[i][2];
        new AlertDialog.Builder(activity)
                .setTitle(t("Создать ивент на карте", "Spawn a map event"))
                .setItems(names, new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface d, int which) {
                        spawn(events[which][0]);
                    }
                })
                .setNegativeButton(t("Отмена", "Cancel"), null)
                .show();
    }

    private static void showCutItems() {
        String[] names = new String[CUT_ITEMS.length];
        for (int i = 0; i < CUT_ITEMS.length; i++)
            names[i] = RU ? CUT_ITEMS[i][1] : CUT_ITEMS[i][2];
        new AlertDialog.Builder(activity)
                .setTitle(t("Получить предмет", "Get an item"))
                .setItems(names, new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface d, int which) {
                        give(CUT_ITEMS[which][0]);
                    }
                })
                .setNegativeButton(t("Отмена", "Cancel"), null)
                .show();
    }

    private static void give(String id) {
        int ok = nativeGive(id);
        Toast.makeText(activity, ok != 0 ? t("Предмет в инвентаре (нужно свободное место)",
                "Item added to the inventory (needs a free slot)")
                : t("Не загружено, перезапустите игру", "Not loaded, restart the game"),
                Toast.LENGTH_SHORT).show();
    }

    /** Every item of the game (ItemList, generated from its references), filtered by a search field. */
    private static void showAllItems() {
        final ArrayList<String[]> shown = new ArrayList<String[]>();
        final ArrayAdapter<String[]> adapter = new ArrayAdapter<String[]>(activity,
                android.R.layout.simple_list_item_2, android.R.id.text1, shown) {
            @Override
            public View getView(int pos, View convert, ViewGroup parent) {
                View v = super.getView(pos, convert, parent);
                String[] it = getItem(pos);
                String group = ItemList.GROUPS[Integer.parseInt(it[0])][RU ? 0 : 1];
                ((TextView) v.findViewById(android.R.id.text1)).setText(RU ? it[2] : it[3]);
                ((TextView) v.findViewById(android.R.id.text2)).setText(group + " · " + it[1]);
                return v;
            }
        };
        final EditText search = new EditText(activity);
        search.setHint(t("Поиск по названию", "Search by name"));
        search.setSingleLine(true);
        search.addTextChangedListener(new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int a, int b, int c) {}

            @Override
            public void onTextChanged(CharSequence s, int a, int b, int c) {}

            @Override
            public void afterTextChanged(Editable s) {
                String q = s.toString().trim().toLowerCase(Locale.ROOT);
                shown.clear();
                for (String[] it : ItemList.ITEMS)
                    if (q.isEmpty() || it[1].contains(q) || it[2].toLowerCase(Locale.ROOT).contains(q)
                            || it[3].toLowerCase(Locale.ROOT).contains(q))
                        shown.add(it);
                adapter.notifyDataSetChanged();
            }
        });
        for (String[] it : ItemList.ITEMS)
            shown.add(it);
        ListView list = new ListView(activity);
        list.setAdapter(adapter);
        list.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> p, View v, int pos, long id) {
                give(shown.get(pos)[1]);
            }
        });
        LinearLayout root = new LinearLayout(activity);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(16), dp(4), dp(16), 0);
        root.addView(search);
        int h = (int) (activity.getResources().getDisplayMetrics().heightPixels * 0.55f);
        root.addView(list, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, h));
        AlertDialog d = new AlertDialog.Builder(activity)
                .setTitle(t("Получить любой предмет", "Get any item"))
                .setView(root)
                .setPositiveButton(t("Закрыть", "Close"), null)
                .create();
        // The keyboard only when the search field is tapped: the list is what most people want.
        d.getWindow().setSoftInputMode(android.view.WindowManager.LayoutParams.SOFT_INPUT_STATE_ALWAYS_HIDDEN);
        d.show();
    }

    private static void showCutContent() {
        LinearLayout root = column();
        addButton(root, t("Вырезанные предметы…", "Cut items…"), new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showCutItems();
            }
        });
        addNote(root, t("Удочки, Беретта, странный гриб и контейнеры — из старой LDoE; костюмы Санты и Мулан, "
                + "ёлка и верстак Санты — из праздничных ивентов, которые здесь не запускаются.",
                "Fishing rods, Beretta, strange mushroom and containers come from old LDoE; Santa and Mulan outfits, "
                + "the tree and Santa's workbench from holiday events that never start here."));
        addButton(root, t("Вырезанные ивенты…", "Cut events…"), new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showEventList(CUT_EVENTS);
            }
        });
        addNote(root, t("Закрытые локации (Нефтебаза, Башни, Бункер Чарли, зимний лес) открываются "
                + "переключателем «Открыть все локации».",
                "Closed locations (Oil plant, Towers, Bunker Charlie, winter forest) open with \"Unlock all locations\"."));
        dialog(t("Вырезанный контент", "Cut content"), root);
    }

    private static void show() {
        LinearLayout root = column();

        final TextView speedLabel = new TextView(activity);
        speedLabel.setTextSize(TypedValue.COMPLEX_UNIT_SP, 16);
        root.addView(speedLabel);
        SeekBar speed = new SeekBar(activity);
        speed.setMax(SPEED_MAX - SPEED_MIN);
        int cur = prefs().getInt("speed", SPEED_MIN);
        speed.setProgress(cur - SPEED_MIN);
        speedLabel.setText(t("Скорость персонажа: x", "Character speed: x") + (cur / 10f));
        speed.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar s, int progress, boolean user) {
                int v = progress + SPEED_MIN;
                speedLabel.setText(t("Скорость персонажа: x", "Character speed: x") + (v / 10f));
                prefs().edit().putInt("speed", v).apply();
                nativeSet(SPEED, v);
            }

            @Override
            public void onStartTrackingTouch(SeekBar s) {}

            @Override
            public void onStopTrackingTouch(SeekBar s) {}
        });
        root.addView(speed);

        // only in the recording copy (build_apk.py --rec)
        if (activity.getPackageName().endsWith(".rec")) {
            addHeader(root, t("Запись видео", "Video recording"));
            addOption(root, HIDE_UI, t("Скрыть интерфейс (кнопки работают; меню — тройной тап в левом верхнем углу)",
                    "Hide the interface (buttons still work; menu: triple tap in the top-left corner)"));
        }

        addHeader(root, t("Персонаж", "Character"));
        addOption(root, GOD, t("Режим бога (без урона, голода и жажды)", "God mode (no damage, hunger, thirst)"));
        addOption(root, NOCLIP, t("Ноуклип (сквозь стены)", "Noclip (walk through walls)"));
        addOption(root, ONE_HIT, t("Убийство с одного удара", "One-hit kill"));
        addOption(root, FAST_ATTACK, t("Мгновенная атака", "Instant attack"));
        addOption(root, NO_DURABILITY, t("Бесконечная прочность предметов", "Infinite item durability"));

        addHeader(root, t("Крафт и база", "Craft and base"));
        addOption(root, FREE_CRAFT, t("Крафт, стройка и улучшение стен/дверей без ресурсов, душ без воды",
                "Craft, build and upgrade walls/doors without resources, shower without water"));
        addOption(root, FREE_ASSEMBLY, t("Сборка генератора, машин, вышек и т.п. без деталей",
                "Assemble the generator, vehicles, towers etc. without parts"));
        addOption(root, INSTANT_WORK, t("Мгновенное производство на станках", "Instant workbench production"));
        addOption(root, UNLOCK_RESEARCH, t("Открыть любой крафт (исследования на любом уровне, бесплатно)",
                "Unlock any craft (researches at any level, free)"));
        addOption(root, DUPE, t("Дюп предметов через «Разделить»", "Duplicate items with Split"));
        addOption(root, INSTANT_LOOT, t("Мгновенное открытие сундуков", "Instant chest opening"));
        addButton(root, t("Получить любой предмет…", "Get any item…"), new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showAllItems();
            }
        });

        addHeader(root, t("Магазин", "Shop"));
        addOption(root, FREE_SHOP, t("Магазин бесплатно", "Free shop"));
        addOption(root, NO_ADS, t("Награда за рекламу без рекламы", "Ad rewards without ads"));

        addHeader(root, t("Карта и ивенты", "Map and events"));
        addOption(root, FREE_TRAVEL, t("Мгновенное и бесплатное передвижение по карте", "Instant free map travel"));
        addOption(root, UNLOCK, t("Открыть все локации", "Unlock all locations"));
        addOption(root, BUNKER, t("Бункер Альфа без кулдауна (любой код)", "Bunker Alfa without cooldown (any code)"));
        addOption(root, FREEZE_EVENTS, t("Заморозить ивенты (кроме орды)", "Freeze events (except horde)"));
        addButton(root, t("Создать ивент на карте…", "Spawn a map event…"), new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showEventList(EVENTS);
            }
        });
        addButton(root, t("Вырезанный контент…", "Cut content…"), new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                showCutContent();
            }
        });

        addHeader(root, t("Сохранение", "Save"));
        addButton(root, t("Откатить сейв и перезапустить…", "Roll back the save and restart…"),
                new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                confirmRollback();
            }
        });
        addNote(root, t("Если загрузка локации зависла и игру пришлось закрыть, при следующем запуске сейв "
                + "откатится сам — к моменту перед входом в неё.",
                "If a location load hangs and the game had to be closed, the next start rolls the save back "
                + "on its own, to the moment before entering it."));

        TextView note = new TextView(activity);
        note.setText(t("Локации обновятся при следующем открытии карты.\n"
                + "Меню также открывается тремя быстрыми нажатиями в левом верхнем углу экрана.",
                "Locations refresh the next time the map is opened.\n"
                + "The menu also opens with three quick taps in the top-left corner of the screen."));
        note.setTextColor(Color.GRAY);
        note.setGravity(Gravity.CENTER_HORIZONTAL);
        note.setPadding(0, dp(8), 0, 0);
        root.addView(note);

        dialog(t("Мод-меню", "Mod menu"), root);
    }
}
