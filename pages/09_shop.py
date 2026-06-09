"""pages/09_shop.py — 装備ショップ"""
import sys
import streamlit as st
from pathlib import Path

_root = Path(__file__).parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from core.mobile_css import MOBILE_CSS

from core.save_manager import load_player, save_player, update_ranking
from core.player import PlayerManager
from core.i18n import t, grade_label
from core.characters import sidebar_avatar_html
from core.equipment import ITEMS as _EQUIP_ITEMS
from core.pets import PET_DEFS
from core.titles import title_badge_html, evaluate_titles
from core.pets import pet_sidebar_html
from core.shop import (
    SHOP_CATALOG, CATEGORY_LABELS,
    get_weekly_sale_ids, get_weekly_rare_ids,
    get_available_exp, get_final_price, is_owned, purchase, get_item_display,
)
from core.equipment_bonus import get_bonus_description, sidebar_bonus_html

st.set_page_config(page_title="ショップ | 英検Quest", page_icon="🏪", layout="centered", initial_sidebar_state="expanded")

st.markdown("""<style>
html,body,[class*="css"]{font-family:'Noto Sans JP',sans-serif;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#1a1a2e,#16213e 60%,#0f3460);}
[data-testid="stSidebar"] *{color:#e0e0e0 !important;}
.hp-bar-outer{background:#2a0a0a;border-radius:8px;height:18px;width:100%;margin:4px 0 12px;overflow:hidden;border:1px solid #5a1a1a;}
.hp-bar-inner{background:linear-gradient(90deg,#e05252,#ff8080);height:100%;border-radius:8px;}
.exp-bar-outer{background:#1a1500;border-radius:8px;height:14px;width:100%;margin:4px 0 12px;overflow:hidden;border:1px solid #5a4a00;}
.exp-bar-inner{background:linear-gradient(90deg,#c8a000,#ffe066);height:100%;border-radius:8px;}
.stat-label{font-size:11px;color:#aaaacc !important;}
@keyframes shimmer{0%{background-position:200% center}100%{background-position:-200% center}}
@keyframes rare-glow{0%,100%{box-shadow:0 0 8px #ffaa0055,0 0 20px #ffcc0033}50%{box-shadow:0 0 16px #ffaa00aa,0 0 40px #ffcc0066}}
</style>""", unsafe_allow_html=True)
st.markdown(MOBILE_CSS, unsafe_allow_html=True)


def init_session():
    if "player" not in st.session_state or st.session_state.player is None:
        st.session_state.player = load_player(st.session_state.get("username", ""))


init_session()
username = st.session_state.get("username", "")

if not username:
    st.warning("先にホーム画面でログインしてください")
    st.stop()

p = st.session_state.player
lang = p.get("language", "ja")
pm = PlayerManager(p)


# ─── サイドバー ────────────────────────────────────────────────────
def render_sidebar():
    hp_pct = pm.hp_percent() * 100
    exp_pct = pm.exp_percent() * 100
    char_id = p.get("character", "")
    equip = p.get("equipment")
    available = get_available_exp(p)
    with st.sidebar:
        st.markdown(
            '<div style="text-align:center;padding:12px 0 6px;">'
            + sidebar_avatar_html(char_id, equip) +
            '<div style="font-size:1.2rem;font-weight:700;color:#ffe066;margin-top:6px;">' + p["name"] + '</div>'
            '<div style="font-size:.8rem;color:#aaaacc;">'
            + t("level", lang) + ' ' + str(p["level"]) + ' | ' + grade_label(p["grade_target"], lang) + '</div>'
            + title_badge_html(p, style="sidebar") + pet_sidebar_html(p) +
            '</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown('<div class="stat-label">' + t("hp", lang) + ' ' + str(p["hp"]) + ' / ' + str(p["hp_max"]) + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="hp-bar-outer"><div class="hp-bar-inner" style="width:' + str(round(hp_pct, 1)) + '%"></div></div>', unsafe_allow_html=True)
        st.markdown('<div class="stat-label">' + t("exp", lang) + ' ' + str(p["exp"]) + ' / ' + str(p["exp_to_next"]) + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="exp-bar-outer"><div class="exp-bar-inner" style="width:' + str(round(exp_pct, 1)) + '%"></div></div>', unsafe_allow_html=True)
        _bhtml = sidebar_bonus_html(p)
        if _bhtml:
            st.markdown(_bhtml, unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(
            '<div style="background:linear-gradient(135deg,#1a1000,#2a2000);border:2px solid #ffe066;'
            'border-radius:12px;padding:12px 16px;text-align:center;">'
            '<div style="font-size:.75rem;color:#aaaacc;margin-bottom:4px;">💰 ショップ残高</div>'
            '<div style="font-size:1.6rem;font-weight:900;color:#ffe066;">'
            + f'{available:,}' + ' EXP</div>'
            '<div style="font-size:.65rem;color:#888888;margin-top:2px;">'
            '累計 ' + f'{p.get("total_exp_earned", 0):,}' + ' | 使用済 ' + f'{p.get("exp_spent", 0):,}' +
            '</div></div>', unsafe_allow_html=True)


render_sidebar()

# キャッシュ（1回のレンダリングで使いまわす）
_sale_ids = get_weekly_sale_ids()
_rare_ids = get_weekly_rare_ids()


# ─── 購入バナー ────────────────────────────────────────────────────
if st.session_state.get("shop_purchased"):
    item_id = st.session_state.shop_purchased
    d = get_item_display(item_id)
    st.markdown(
        '<div style="background:linear-gradient(135deg,#1a2a00,#2a4400,#1a2a00);'
        'border:2px solid #88ff44;border-radius:14px;padding:14px 20px;'
        'animation:rare-glow 2s ease-in-out;margin-bottom:12px;text-align:center;">'
        '<div style="font-size:1.6rem;margin-bottom:4px;">' + d["icon"] + '</div>'
        '<div style="font-size:1.1rem;font-weight:700;color:#aaff66;">'
        '✨ ' + d["name"] + ' を購入しました！</div>'
        '</div>', unsafe_allow_html=True)
    st.balloons()
    st.session_state.shop_purchased = None


# ─── ヘッダー ──────────────────────────────────────────────────────
available = get_available_exp(p)
st.markdown(
    '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px;">'
    '<div style="font-size:2rem;font-weight:700;color:#ffe066;">🏪 装備ショップ</div>'
    '<div style="background:#1a1500;border:1px solid #ffe066;border-radius:10px;padding:6px 14px;'
    'font-size:1rem;font-weight:700;color:#ffe066;">💰 ' + f'{available:,}' + ' EXP</div>'
    '</div>'
    '<div style="font-size:.85rem;color:#888;margin-bottom:16px;">'
    'EXPを使って装備・アクセサリ・ペットたまごをゲットしよう！</div>',
    unsafe_allow_html=True)

# ─── 週替わりセール バナー ─────────────────────────────────────────
sale_items = [get_item_display(i) for i in _sale_ids]
if sale_items:
    st.markdown(
        '<div style="background:linear-gradient(135deg,#2a0022,#1a0018);'
        'border:2px solid #ff44aa;border-radius:14px;padding:14px 18px;margin-bottom:16px;">'
        '<div style="font-size:1rem;font-weight:700;color:#ff88cc;margin-bottom:10px;">'
        '🔥 今週の週替わりセール — 30% OFF！</div>'
        '<div style="display:flex;gap:10px;flex-wrap:wrap;">' +
        "".join(
            '<div style="background:#220018;border:1px solid #ff44aa;border-radius:8px;'
            'padding:6px 10px;display:flex;align-items:center;gap:8px;">'
            '<span style="font-size:1.4rem;">' + d["icon"] + '</span>'
            '<div><div style="font-size:.82rem;font-weight:700;color:#ffaadd;">' + d["name"] + '</div>'
            '<div style="font-size:.72rem;"><span style="color:#888;text-decoration:line-through;">'
            + f'{d["price"]:,}' + '</span>'
            '<span style="color:#ff88cc;font-weight:700;margin-left:6px;">'
            + f'{get_final_price(d["id"], _sale_ids):,}' + ' EXP</span></div>'
            '</div></div>'
            for d in sale_items
        ) +
        '</div></div>', unsafe_allow_html=True)

# ─── レア入荷 バナー ──────────────────────────────────────────────
rare_items = [get_item_display(i) for i in _rare_ids]
if rare_items:
    st.markdown(
        '<div style="background:linear-gradient(135deg,#1a1000,#2a1800);'
        'border:2px solid #ffaa00;border-radius:14px;padding:14px 18px;margin-bottom:16px;'
        'animation:rare-glow 3s ease-in-out infinite;">'
        '<div style="font-size:1rem;font-weight:700;color:#ffcc44;margin-bottom:10px;">'
        '⭐ 今週のレア入荷 — 数量限定！</div>'
        '<div style="display:flex;gap:10px;flex-wrap:wrap;">' +
        "".join(
            '<div style="background:#2a1800;border:1px solid #ffaa00;border-radius:8px;'
            'padding:6px 10px;display:flex;align-items:center;gap:8px;">'
            '<span style="font-size:1.4rem;">' + d["icon"] + '</span>'
            '<div><div style="font-size:.82rem;font-weight:700;color:#ffe066;">' + d["name"] + '</div>'
            '<div style="font-size:.72rem;color:#ffaa44;">' + f'{d["price"]:,}' + ' EXP</div>'
            '</div></div>'
            for d in rare_items
        ) +
        '</div></div>', unsafe_allow_html=True)


# ─── アイテムカード描画 ────────────────────────────────────────────
def render_item_card(item_id: str, col, key_suffix: str = ""):
    d = get_item_display(item_id)
    final_price = get_final_price(item_id, _sale_ids)
    owned = is_owned(p, item_id)
    can_afford = available >= final_price
    is_rare = d["rare"]
    on_sale = item_id in _sale_ids
    in_rare_stock = item_id in _rare_ids

    # ── ラベルバッジ ──
    badges = ""
    if is_rare and in_rare_stock:
        badges += '<span style="background:#2a1800;border:1px solid #ffaa00;color:#ffcc44;border-radius:6px;padding:1px 7px;font-size:.62rem;font-weight:700;margin-right:4px;">⭐ レア入荷</span>'
    elif is_rare:
        badges += '<span style="background:#1a1a1a;border:1px solid #555;color:#777;border-radius:6px;padding:1px 7px;font-size:.62rem;margin-right:4px;">入荷待ち</span>'
    if on_sale:
        badges += '<span style="background:#2a0022;border:1px solid #ff44aa;color:#ff88cc;border-radius:6px;padding:1px 7px;font-size:.62rem;font-weight:700;">🔥 30%OFF</span>'
    if owned:
        badges += '<span style="background:#1a2a1a;border:1px solid #44aa44;color:#88ff88;border-radius:6px;padding:1px 7px;font-size:.62rem;font-weight:700;margin-left:4px;">✅ 所持中</span>'

    # ── カードスタイル ──
    if is_rare and in_rare_stock:
        border = "#ffaa00"
        bg = "linear-gradient(135deg,#1a1000,#2a1800)"
        glow = "animation:rare-glow 3s ease-in-out infinite;"
    elif is_rare:
        border = "#444433"
        bg = "linear-gradient(135deg,#111110,#1a1a18)"
        glow = ""
    elif on_sale:
        border = "#ff44aa"
        bg = "linear-gradient(135deg,#1a001a,#220018)"
        glow = ""
    else:
        border = "#3a3a6a"
        bg = "linear-gradient(135deg,#1e1e3a,#2a2a4a)"
        glow = ""

    opacity = "1.0" if (not is_rare or in_rare_stock) else "0.55"

    # ── たまごSVG or 絵文字 ──
    if d["egg_svg"]:
        icon_html = (
            '<div style="width:60px;height:60px;margin:0 auto 6px;display:flex;'
            'align-items:center;justify-content:center;">'
            '<div style="width:54px;height:54px;">' + d["egg_svg"] + '</div></div>'
        )
    else:
        tier_size = {1: "2.2rem", 2: "2.6rem", 3: "3rem", 4: "3.4rem"}.get(d["tier"], "2.4rem")
        icon_html = (
            '<div style="font-size:' + tier_size + ';text-align:center;margin-bottom:6px;'
            + ('filter:drop-shadow(0 0 8px #ffaa00);' if is_rare and in_rare_stock else '') +
            '">' + d["icon"] + '</div>'
        )

    # ── 価格表示 ──
    if final_price == 0:
        price_html = '<span style="color:#88ff88;font-weight:700;">無料</span>'
    elif on_sale:
        price_html = (
            '<span style="color:#666;text-decoration:line-through;font-size:.8rem;">' + f'{d["price"]:,}' + '</span>'
            ' <span style="color:#ff88cc;font-weight:700;">' + f'{final_price:,}' + ' EXP</span>'
        )
    else:
        price_html = '<span style="color:#ffe066;font-weight:700;">' + f'{final_price:,}' + ' EXP</span>'

    with col:
        st.markdown(
            '<div style="background:' + bg + ';border:2px solid ' + border + ';border-radius:14px;'
            'padding:14px 12px;margin-bottom:8px;text-align:center;opacity:' + opacity + ';' + glow + '">'
            '<div style="min-height:20px;margin-bottom:8px;">' + badges + '</div>'
            + icon_html +
            '<div style="font-size:.92rem;font-weight:700;color:#ffe066;margin-bottom:4px;">' + d["name"] + '</div>'
            '<div style="font-size:.72rem;color:#aaaacc;margin-bottom:4px;min-height:28px;">' + d["desc"] + '</div>'
            + ('<div style="font-size:.7rem;color:#88ccaa;font-weight:700;margin-bottom:6px;">' + get_bonus_description(item_id) + '</div>' if get_bonus_description(item_id) else '')
            + '<div style="font-size:.9rem;margin-bottom:10px;">' + price_html + '</div>'
            '</div>', unsafe_allow_html=True)

        # ── ボタン ──
        if owned and not item_id.startswith("egg_"):
            st.button("✅ 所持中", key="own_" + item_id + key_suffix, disabled=True, use_container_width=True)
        elif is_rare and not in_rare_stock:
            st.button("🔒 今週は入荷なし", key="nostock_" + item_id + key_suffix, disabled=True, use_container_width=True)
        elif not can_afford:
            st.button("💰 EXP不足 (" + f'{final_price:,}' + ")", key="nofunds_" + item_id + key_suffix, disabled=True, use_container_width=True)
        else:
            btn_label = "✨ 無料で入手" if final_price == 0 else ("✨ " + f'{final_price:,}' + " EXPで購入")
            if st.button(btn_label, key="buy_" + item_id + key_suffix, use_container_width=True, type="primary"):
                ok = purchase(p, item_id, final_price)
                if ok:
                    _ = evaluate_titles(p)
                    save_player(p, username)
                    update_ranking(p, username)
                    st.session_state.shop_purchased = item_id
                    st.rerun()


# ─── カテゴリタブ ──────────────────────────────────────────────────
ALL_CATS = ["すべて", "⚔️ 武器", "🛡️ 防具", "🎩 帽子", "🧥 マント", "📿 ネックレス", "💍 指輪", "🥚 ペットたまご"]
CAT_KEYS = ["all", "weapon", "armor", "hat", "cloak", "necklace", "ring", "egg"]

tabs = st.tabs(ALL_CATS)

for tab_i, (tab, cat_key) in enumerate(zip(tabs, CAT_KEYS)):
    with tab:
        if cat_key == "all":
            # ─ すべてタブ：セール → レア入荷 → 通常の順に表示
            sections = [
                ("🔥 週替わりセール", [i for i in _sale_ids]),
                ("⭐ レア入荷", list(_rare_ids)),
                ("🛍️ 通常販売",
                 [s["id"] for s in SHOP_CATALOG
                  if not s.get("rare") and s["id"] not in _sale_ids]),
            ]
            for sec_title, ids in sections:
                if not ids:
                    continue
                st.markdown(
                    '<div style="font-size:.9rem;font-weight:700;color:#ffe066;'
                    'margin:12px 0 6px;">' + sec_title + '</div>',
                    unsafe_allow_html=True)
                cols = st.columns(2)
                for j, item_id in enumerate(ids):
                    render_item_card(item_id, cols[j % 2], key_suffix="_all" + str(j))
        else:
            # カテゴリ別
            items_in_cat = [s["id"] for s in SHOP_CATALOG if s["category"] == cat_key]
            if not items_in_cat:
                st.info("このカテゴリの商品はありません")
                continue

            # レア入荷を先頭に
            rare_here = [i for i in items_in_cat if i in _rare_ids]
            sale_here = [i for i in items_in_cat if i in _sale_ids and i not in _rare_ids]
            normal_here = [i for i in items_in_cat if i not in _rare_ids and i not in _sale_ids]
            ordered = rare_here + sale_here + normal_here

            cols = st.columns(2)
            for j, item_id in enumerate(ordered):
                render_item_card(item_id, cols[j % 2], key_suffix="_" + cat_key + str(j))

# ─── インベントリ確認 ──────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("🎒 所持アイテム一覧（インベントリ）"):
    inv = p.get("inventory", [])
    equip = p.get("equipment", {})
    equipped_ids = [v for v in equip.values() if v]
    all_owned = list(dict.fromkeys(equipped_ids + inv))
    if not all_owned:
        st.info("まだアイテムを持っていません。ショップで購入しよう！")
    else:
        cols = st.columns(4)
        for j, item_id in enumerate(all_owned):
            meta = _EQUIP_ITEMS.get(item_id, {})
            is_eq = item_id in equipped_ids
            glow = "filter:drop-shadow(0 0 4px #ffcc00);" if meta.get("rare") else ""
            with cols[j % 4]:
                st.markdown(
                    '<div style="text-align:center;padding:8px 4px;background:#1a1a2e;'
                    'border:1px solid ' + ("#ffe066" if is_eq else "#3a3a6a") + ';border-radius:8px;margin-bottom:4px;">'
                    '<div style="font-size:1.6rem;' + glow + '">' + meta.get("icon", "📦") + '</div>'
                    '<div style="font-size:.65rem;color:' + ("#ffe066" if is_eq else "#aaaacc") + ';">'
                    + meta.get("name", item_id) + '</div>'
                    + ('<div style="font-size:.55rem;color:#88ccff;">装備中</div>' if is_eq else '') +
                    '</div>', unsafe_allow_html=True)
    st.caption("装備の変更は「設定」ページから行えます")
