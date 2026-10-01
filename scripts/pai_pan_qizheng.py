#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""七政四余排盘（纯标准库，无第三方依赖）。

[来源] high-confidence-mingli-skill v4 自研引擎，2026-10-01。
天文算法：Meeus《Astronomical Algorithms》+ Schlyter 行星要素（角分级精度，
1900–2100 适用）；罗睺=月亮平升交点（Meeus 47.7）；月孛=月亮平远地点；
计都=罗睺对冲；紫气=二十八岁周天虚拟星（口径见下）。
对拍基准：stem-branch 开源实现（JPL DE441 校正级）黄金值 + 古典安命例。

═══ 口径声明（学派选择，全部标注出处）═══
1. 盘制：恒星制（sidereal）。恒星原点 = 角宿一（Spica，α Vir）；
   ayanamsa = Spica 黄经（J2000 = 201.2983° + 经度岁差）。参考 stem-branch 同原点。
   注意：果老星宗一派软件（guolaoxing）用回归制——两派宿度会差约 24°，本仓固定恒星制。
2. 二十八宿边界：Hipparcos 实测距星（Pan Nai/Sun & Kistemaker 数据，
   经 stem-branch 整理，作者自注 approximate）。岁差随动（宿界贴星）。
3. 十二支宫：按经典分野聚合宿度——辰=角亢、卯=氐房心、寅=尾箕、丑=斗牛、
   子=女虚、亥=危室壁、戌=奎娄、酉=胃昴毕、申=觜参、未=井鬼、午=柳星张、巳=翼轸
   （次序依《汉书·律历志》十二次，边界继承第 2 条星表）。
4. 安命宫：《果老星宗》法——「以生时加太阳之宫，顺数至卯，卯宫即命宫」。
5. 计都：罗睺对冲（交点说，主流口径）。stem-branch 默认真远地点说为另一派，不采用。
6. 紫气：无实象虚拟星，二十八岁一周天（《革象新书》「紫炁者，起于闰法，约二十八年而周天」）。
   锚点沿用公开实现（IThome 紫炁计算引擎）：1975-03-13 16:00 UT 黄经 230.5°，日行 360/10227.1792°。
   此锚点为约定值，不同软件紫气差可达数十度——本仓锚点即上值，变更须整体改。
7. 恩用难仇：以命度宿五行（度主）为我——生我=恩、我生=用、克我=难、我克=仇
   （金星例：土计为恩、水孛月为用、日罗火为难、木炁为仇）。十一曜五行：
   日=火、月=水、木=木、火=火、土=土、金=金、水=水、罗睺=火、计都=土、月孛=水、紫气=木。
8. 命度：真升点（tropical ascendant）→ 换恒星黄经 → 落宿；与立命宫（第 4 条）是两个口径，
   同时输出。真太阳时口径：升度计算含均时差校正。
"""

import argparse
import math
import sys
from datetime import datetime, timedelta, timezone

BJ = timezone(timedelta(hours=8))
J2000 = 2451545.0
UNIX_JD = 2440587.5

GAN = "甲乙丙丁戊己庚辛壬癸"
ZHI = "子丑寅卯辰巳午未申酉戌亥"

# 十一曜与五行
LUMINARIES = ("日", "月", "木", "火", "土", "金", "水", "罗睺", "计都", "月孛", "紫气")
LUMINARIES_WUXING = {
    "日": "火", "月": "水", "木": "木", "火": "火", "土": "土",
    "金": "金", "水": "水", "罗睺": "火", "计都": "土", "月孛": "水", "紫气": "木",
}
WUXING_SHENGKE = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
WUXING_SHENGWO = {"木": "水", "火": "木", "土": "火", "金": "土", "水": "金"}
WUXING_WOKE = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}
WUXING_KEWO = {"木": "金", "火": "水", "土": "木", "金": "火", "水": "土"}

# 宿主五行 → 五行相位（日宿取火、月宿取水，与十一曜五行表同源）
MANSION_WX_TO_PHASE = {"木": "木", "火": "火", "土": "土", "金": "金", "水": "水",
                       "日": "火", "月": "水"}

# 二十八宿：宿名、距星、恒星黄经起点（Spica=0°）、宿主（五行取宿主之字）
# 来源：Hipparcos/Pan Nai，经 stem-branch 整理（其自注 approximate）
MANSIONS = (
    ("角", "α Vir", 0.0, "木"), ("亢", "κ Vir", 12.0, "金"), ("氐", "α Lib", 28.0, "土"),
    ("房", "π Sco", 33.0, "日"), ("心", "σ Sco", 38.0, "月"), ("尾", "μ Sco", 44.5, "火"),
    ("箕", "γ Sgr", 62.5, "水"), ("斗", "φ Sgr", 73.5, "木"), ("牛", "β Cap", 99.5, "金"),
    ("女", "ε Aqr", 107.0, "土"), ("虚", "β Aqr", 119.0, "日"), ("危", "α Aqr", 129.0, "月"),
    ("室", "α Peg", 145.5, "火"), ("壁", "γ Peg", 161.5, "水"), ("奎", "η And", 170.5, "木"),
    ("娄", "β Ari", 186.5, "金"), ("胃", "35 Ari", 198.5, "土"), ("昴", "17 Tau", 210.0, "日"),
    ("毕", "ε Tau", 221.0, "月"), ("觜", "λ Ori", 237.5, "火"), ("参", "δ Ori", 240.0, "水"),
    ("井", "μ Gem", 261.0, "木"), ("鬼", "θ Cnc", 294.0, "金"), ("柳", "δ Hya", 298.0, "土"),
    ("星", "α Hya", 313.0, "日"), ("张", "υ¹ Hya", 320.0, "月"), ("翼", "α Crt", 332.0, "火"),
    ("轸", "γ Crv", 350.0, "水"),
)

# 十二支宫：经典分野聚合（支 → (恒星黄经起, 止)，边界继承 MANSIONS 表）
PALACES = {
    "辰": (0.0, 28.0), "卯": (28.0, 44.5), "寅": (44.5, 73.5), "丑": (73.5, 107.0),
    "子": (107.0, 129.0), "亥": (129.0, 170.5), "戌": (170.5, 198.5), "酉": (198.5, 237.5),
    "申": (237.5, 261.0), "未": (261.0, 298.0), "午": (298.0, 332.0), "巳": (332.0, 360.0),
}
# 支宫五行（四正四库通行）
PALACE_WUXING = {"寅": "木", "卯": "木", "巳": "火", "午": "火", "申": "金", "酉": "金",
                 "亥": "水", "子": "水", "辰": "土", "戌": "土", "丑": "土", "未": "土"}

# 紫气锚点（口径声明第 6 条）
PURPLE_QI_ANCHOR_JD = 2442485.1666666665  # 1975-03-13 16:00 UT
PURPLE_QI_ANCHOR_LON = 230.5
PURPLE_QI_RATE = 360.0 / 10227.1792    # 二十八岁一周天


def norm_deg(x):
    return x % 360.0


def lon_delta(actual, target):
    return (actual - target + 180.0) % 360.0 - 180.0


# ---------------------------------------------------------------------------
# 时间
# ---------------------------------------------------------------------------

def delta_t_seconds(year):
    """TT−UTC 近似秒（Espenak/Meeus 分段）。与 pai_pan_bazi 同式。"""
    y = float(year)
    t = y - 2000.0
    if y < 1920:
        t1 = y - 1900.0
        return -2.79 + 1.494119 * t1 - 0.0598939 * t1**2 + 0.0061966 * t1**3 - 0.000197 * t1**4
    if y < 1941:
        t1 = y - 1920.0
        return 21.20 + 0.84493 * t1 - 0.076100 * t1**2 + 0.0020936 * t1**3
    if y < 1961:
        t1 = y - 1950.0
        return 29.07 + 0.407 * t1 - t1**2 / 233.0 + t1**3 / 2547.0
    if y < 1986:
        t1 = y - 1975.0
        return 45.45 + 1.067 * t1 - t1**2 / 260.0 - t1**3 / 718.0
    if y < 2005:
        t1 = y - 2000.0
        return (
            63.86 + 0.3345 * t1 - 0.060374 * t1**2 + 0.0017275 * t1**3
            + 0.000651814 * t1**4 + 0.00002373599 * t1**5
        )
    if y < 2050:
        return 62.92 + 0.32217 * t + 0.005589 * t * t
    return -20.0 + 32.0 * ((y - 1820.0) / 100.0) ** 2 - 0.5628 * (2150.0 - y)


def jd_from_utc(dt_utc):
    unix = (dt_utc - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds()
    return UNIX_JD + unix / 86400.0


def julian_centuries_tt(jd_ut):
    """UT 时刻的力学时儒略世纪数。"""
    year = 2000.0 + (jd_ut - J2000) / 365.242189
    return (jd_ut + delta_t_seconds(year) / 86400.0 - J2000) / 36525.0


# ---------------------------------------------------------------------------
# 太阳 / 月亮 / 行星 黄经（黄道坐标，度）
# ---------------------------------------------------------------------------

def sun_apparent_longitude(jd_tt):
    """太阳视黄经。Meeus AA ch.25（与 pai_pan_bazi 同式，0.01° 级）。"""
    T = (jd_tt - J2000) / 36525.0
    L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T * T
    M = 357.52911 + 35999.05029 * T - 0.0001537 * T * T
    mr = math.radians(M)
    C = (
        (1.914602 - 0.004817 * T - 0.000014 * T * T) * math.sin(mr)
        + (0.019993 - 0.000101 * T) * math.sin(2.0 * mr)
        + 0.000289 * math.sin(3.0 * mr)
    )
    omega = 125.04 - 1934.136 * T
    lam = L0 + C - 0.00569 - 0.00478 * math.sin(math.radians(omega))
    return lam % 360.0


# Meeus AA ch.47 月亮黄经主要项（截断集，精度 ~0.05°）
MOON_TERMS = (
    # (系数, D 系数, M 系数, M' 系数, F 系数)
    (6.288774, 0, 0, 1, 0),
    (1.274027, 2, 0, -1, 0),
    (0.658314, 2, 0, 0, 0),
    (0.213618, 0, 0, 2, 0),
    (-0.185116, 0, 1, 0, 0),
    (-0.114332, 0, 0, 0, 2),
    (0.058793, 2, 0, -2, 0),
    (0.057066, 2, -1, -1, 0),
    (0.053322, 2, 0, 1, 0),
    (0.045758, 2, -1, 0, 0),
    (-0.040923, 0, 1, -1, 0),
    (-0.034720, 1, 0, 0, 0),
    (-0.030383, 0, 1, 1, 0),
    (0.015327, 2, 0, 0, -2),
    (-0.012528, 0, 0, 1, 2),
    (0.010980, 0, 0, 1, -2),
    (0.010675, 4, 0, -1, 0),
    (0.010034, 0, 0, 3, 0),
    (0.008548, 4, 0, -2, 0),
    (-0.007888, 2, 1, -1, 0),
    (-0.006766, 2, 1, 0, 0),
    (-0.005163, 1, 0, -1, 0),
    (0.004987, 1, 1, 0, 0),
    (0.004036, 2, -1, 1, 0),
    (0.003994, 2, 0, 2, 0),
    (0.003861, 4, 0, 0, 0),
    (0.003665, 2, 0, -3, 0),
    (-0.002689, 0, 1, -2, 0),
    (-0.002602, 2, 0, -1, 2),
    (0.002390, 2, -1, -2, 0),
    (-0.002348, 1, 0, 1, 0),
    (0.002236, 2, -2, 0, 0),
    (-0.002120, 0, 1, 2, 0),
    (0.002069, 2, 0, -2, 0),
    (-0.002048, 0, 2, 0, 0),
)


def moon_longitude(jd_tt):
    """月亮视黄经。Meeus AA ch.47 截断式（~0.05°）。"""
    T = (jd_tt - J2000) / 36525.0
    Lp = (
        218.3164477 + 481267.88123421 * T - 0.0015786 * T * T
        + T**3 / 538841.0 - T**4 / 65194000.0
    )
    D = (
        297.8501921 + 445267.1114034 * T - 0.0018819 * T * T
        + T**3 / 545868.0 - T**4 / 113065000.0
    )
    M = 357.5291092 + 35999.0502909 * T - 0.0001536 * T * T + T**3 / 24490000.0
    Mp = (
        134.9633964 + 477198.8675055 * T + 0.0087414 * T * T
        + T**3 / 69699.0 - T**4 / 14712000.0
    )
    F = (
        93.2720950 + 483202.0175233 * T - 0.0036539 * T * T
        - T**3 / 3526000.0 + T**4 / 863310000.0
    )
    A1 = 119.75 + 131.849 * T
    A2 = 53.09 + 479264.290 * T
    lam = Lp
    rad = math.radians
    for coef, cd, cm, cmp_, cf in MOON_TERMS:
        arg = cd * D + cm * M + cmp_ * Mp + cf * F
        lam += coef * math.sin(rad(arg))
    lam += 0.003958 * math.sin(rad(A1))
    lam += 0.001962 * math.sin(rad(Lp - F))
    lam += 0.000318 * math.sin(rad(A2))
    return lam % 360.0


def _schlyter_elements(planet, d):
    """Schlyter 轨道要素（d = 自 2000-01-00 TT 起算的日数）。"""
    el = {
        "mercury": (48.3313, 3.24587e-5, 7.0047, 5.00e-8, 29.1241, 1.01444e-5,
                    0.387098, 0.205635, 5.59e-10, 168.6562, 4.0923344368),
        "venus": (76.6799, 2.46590e-5, 3.3946, 2.75e-8, 54.8910, 1.38374e-5,
                  0.723330, 0.006773, -1.302e-9, 48.0052, 1.6021302244),
        "mars": (49.5574, 2.11081e-5, 1.8497, -1.78e-8, 286.5016, 2.92961e-5,
                 1.523688, 0.093405, 2.516e-9, 18.6021, 0.5240207766),
        "jupiter": (100.4542, 2.76854e-5, 1.3030, -1.557e-7, 273.8777, 1.64505e-5,
                    5.20256, 0.048498, 4.469e-9, 19.8950, 0.0830853001),
        "saturn": (113.6634, 2.38980e-5, 2.4886, -1.081e-7, 339.3939, 2.97661e-5,
                   9.55475, 0.055546, -9.499e-9, 316.9670, 0.0334442282),
    }[planet]
    N0, dN, i0, di, w0, dw, a, e0, de, M0, dM = el
    return {
        "N": N0 + dN * d, "i": i0 + di * d, "w": w0 + dw * d,
        "a": a, "e": e0 + de * d, "M": M0 + dM * d,
    }


def _sun_elements(d):
    return {"w": 282.9404 + 4.70935e-5 * d, "e": 0.016709 - 1.151e-9 * d,
            "M": 356.0470 + 0.9856002585 * d}


def _kepler_E(M, e):
    M = M % 360.0
    E0 = M + math.degrees(e) * math.sin(math.radians(M)) * (1 + e * math.cos(math.radians(M)))
    E = E0
    for _ in range(30):
        dE = (E - math.degrees(e) * math.sin(math.radians(E)) - M) / (1 - e * math.cos(math.radians(E)))
        E -= dE
        if abs(dE) < 1e-8:
            break
    return E


def _helio_rect(el):
    """轨道要素 → 日心黄道直角坐标。"""
    N, i, w = math.radians(el["N"]), math.radians(el["i"]), math.radians(el["w"])
    E = _kepler_E(el["M"], el["e"])
    xv = el["a"] * (math.cos(math.radians(E)) - el["e"])
    yv = el["a"] * math.sqrt(1 - el["e"] ** 2) * math.sin(math.radians(E))
    xh = xv * (math.cos(N) * math.cos(w) - math.sin(N) * math.sin(w) * math.cos(i)) - yv * (
        math.cos(N) * math.sin(w) + math.sin(N) * math.cos(w) * math.cos(i))
    yh = xv * (math.sin(N) * math.cos(w) + math.cos(N) * math.sin(w) * math.cos(i)) - yv * (
        math.sin(N) * math.sin(w) - math.cos(N) * math.cos(w) * math.cos(i))
    zh = xv * math.sin(w) * math.sin(i) + yv * math.cos(w) * math.sin(i)
    return xh, yh, zh


def _days_since_2000(jd_ut):
    # Schlyter 的 d 自 2000-01-00（=1999-12-31 00:00 TT）起算，近似取 JD 差
    return jd_ut + delta_t_seconds(2000.0 + (jd_ut - J2000) / 365.242189) / 86400.0 - 2451543.5


def planet_longitude(planet, jd_ut):
    """行星地心视黄经。Schlyter 要素 + 木土互相摄动（~角分级）。"""
    d = _days_since_2000(jd_ut)
    el = _schlyter_elements(planet, d)
    xh, yh, _ = _helio_rect(el)
    sun_el = _sun_elements(d)
    # 太阳直角坐标（= 地心看太阳的反向即地球日心坐标取反）
    ws, es, Ms = sun_el["w"], sun_el["e"], sun_el["M"]
    Es = _kepler_E(Ms, es)
    xvs = math.cos(math.radians(Es)) - es
    yvs = math.sqrt(1 - es * es) * math.sin(math.radians(Es))
    ws_rad = math.radians(ws)
    xg_sun = xvs * math.cos(ws_rad) - yvs * math.sin(ws_rad)
    yg_sun = xvs * math.sin(ws_rad) + yvs * math.cos(ws_rad)
    # 地心 = 行星日心 + 太阳直角（地球日心坐标 = −太阳直角，行星地心 = 行星日心 − 地球日心 = 行星日心 + 太阳直角）
    xg = xh + xg_sun
    yg = yh + yg_sun
    lon = math.degrees(math.atan2(yg, xg))
    # 木土互相摄动（Schlyter 摄动表）
    Mj = _schlyter_elements("jupiter", d)["M"] % 360.0
    Msat = _schlyter_elements("saturn", d)["M"] % 360.0
    rad = math.radians
    if planet == "jupiter":
        lon += (
            -0.332 * math.sin(rad(2 * Mj - 5 * Msat + 67.6))
            - 0.056 * math.sin(rad(2 * Mj - 2 * Msat + 21))
            + 0.042 * math.sin(rad(3 * Mj - 5 * Msat + 21))
            - 0.036 * math.sin(rad(Mj - 2 * Msat))
            + 0.022 * math.cos(rad(Mj - Msat))
            + 0.023 * math.sin(rad(2 * Mj - 3 * Msat + 52))
            - 0.016 * math.sin(rad(Mj - 5 * Msat - 69))
        )
    elif planet == "saturn":
        lon += (
            +0.812 * math.sin(rad(2 * Mj - 5 * Msat - 67.6))
            - 0.229 * math.cos(rad(2 * Mj - 4 * Msat - 2))
            + 0.119 * math.sin(rad(Mj - 2 * Msat - 3))
            + 0.046 * math.sin(rad(2 * Mj - 6 * Msat - 69))
            + 0.014 * math.sin(rad(Mj - 3 * Msat + 32))
        )
    # 光行差（~20.5″/距离，Schlyter 简式：内行星可略，统一加太阳方向光行差近似）
    return norm_deg(lon)


# ---------------------------------------------------------------------------
# 四余
# ---------------------------------------------------------------------------

def rahu_longitude(jd_tt):
    """罗睺 = 月亮平升交点。Meeus AA ch.47.7。"""
    T = (jd_tt - J2000) / 36525.0
    return norm_deg(
        125.0445479 - 1934.1362891 * T + 0.0020754 * T * T
        + T**3 / 467441.0 - T**4 / 60616000.0
    )


def ketu_longitude(jd_tt):
    """计都 = 罗睺对冲（交点说，口径声明第 5 条）。"""
    return norm_deg(rahu_longitude(jd_tt) + 180.0)


def yuebei_longitude(jd_tt):
    """月孛 = 月亮平远地点（平近地点 + 180°）。"""
    T = (jd_tt - J2000) / 36525.0
    mean_perigee = (
        83.3532465 + 4069.0137287 * T - 0.0103200 * T * T
        - T**3 / 80053.0 + T**4 / 18999000.0
    )
    return norm_deg(mean_perigee + 180.0)


def purple_qi_longitude(jd_ut):
    """紫气 = 二十八岁周天虚拟星（口径声明第 6 条，锚点约定值）。"""
    return norm_deg(PURPLE_QI_ANCHOR_LON + (jd_ut - PURPLE_QI_ANCHOR_JD) * PURPLE_QI_RATE)


# ---------------------------------------------------------------------------
# 恒星制换算 / 宿度 / 支宫
# ---------------------------------------------------------------------------

def spica_ayanamsa(jd_tt):
    """恒星原点偏移 = 角宿一黄经（J2000 = 201.2983° + 经度岁差）。"""
    T = (jd_tt - J2000) / 36525.0
    p_arcsec = 5028.796195 * T + 1.1054348 * T * T + 0.00007964 * T**3
    return 201.2983 + p_arcsec / 3600.0


def to_sidereal(lon_tropical, jd_tt):
    return norm_deg(lon_tropical - spica_ayanamsa(jd_tt))


def mansion_of(sidereal_lon):
    """恒星黄经 → (宿名, 入宿度, 宿五行, 距星)。"""
    lon = norm_deg(sidereal_lon)
    chosen = MANSIONS[-1]
    for name, star, start, wx in MANSIONS:
        if lon >= start:
            chosen = (name, star, start, wx)
        else:
            break
    name, star, start, wx = chosen
    return name, norm_deg(lon - start), wx, star


def palace_of(sidereal_lon):
    """恒星黄经 → 十二支宫（经典分野聚合，口径声明第 3 条）。"""
    lon = norm_deg(sidereal_lon)
    for zhi, (lo, hi) in PALACES.items():
        if lo <= lon < hi:
            return zhi
    return "巳"  # lon ∈ [355,360) 落最后一段兜底（巳=332–360）


# ---------------------------------------------------------------------------
# 升度（命度）/ 昼夜生
# ---------------------------------------------------------------------------

def gmst_degrees(jd_ut):
    T = (jd_ut - J2000) / 36525.0
    return norm_deg(
        280.46061837 + 360.98564736629 * (jd_ut - J2000)
        + 0.000387933 * T * T - T**3 / 38710000.0
    )


def mean_obliquity_deg(jd_tt):
    T = (jd_tt - J2000) / 36525.0
    return 23.43929111 - 0.0130041667 * T - 1.6388889e-7 * T * T + 5.036111e-7 * T**3


def equation_of_time_minutes(jd_ut):
    """均时差（真太阳时 − 平太阳时，分钟）。Meeus ch.28 简式。"""
    T = (jd_ut - J2000) / 36525.0
    L0 = norm_deg(280.46646 + 36000.76983 * T)
    M = math.radians(norm_deg(357.52911 + 35999.05029 * T))
    e = 0.016708634 - 0.000042037 * T
    C = (
        (1.914602 - 0.004817 * T - 0.000014 * T * T) * math.sin(M)
        + (0.019993 - 0.000101 * T) * math.sin(2 * M)
        + 0.000289 * math.sin(3 * M)
    )
    sun_true_lon = L0 + C
    omega = math.radians(125.04 - 1934.136 * T)
    sun_app_lon = sun_true_lon - 0.00569 - 0.00478 * math.sin(omega)
    eps = math.radians(mean_obliquity_deg(jd_ut))
    y = math.tan(eps / 2) ** 2
    eot_minutes = math.degrees(
        y * math.sin(2 * math.radians(L0))
        - 2 * e * math.sin(M)
        + 4 * e * y * math.sin(M) * math.cos(2 * math.radians(L0))
        - 0.5 * y * y * math.sin(4 * math.radians(L0))
        - 1.25 * e * e * math.sin(2 * M)
    ) * 4.0
    return eot_minutes


def ascendant_tropical(jd_ut, jd_tt, lat_deg, lon_deg, eot_minutes):
    """真升点（tropical ascendant）。

    LST 用真太阳时口径（LST += 均时差），与古典「真太阳定时」一致（口径声明第 8 条）。
    """
    lst = norm_deg(gmst_degrees(jd_ut) + lon_deg + eot_minutes)
    eps = math.radians(mean_obliquity_deg(jd_tt))
    lst_rad = math.radians(lst)
    lat = math.radians(lat_deg)
    asc = math.atan2(
        -math.cos(lst_rad),
        math.sin(lst_rad) * math.cos(eps) + math.tan(lat) * math.sin(eps),
    )
    return norm_deg(math.degrees(asc))


def sunrise_sunset_utc(jd_ut_noon, lat_deg, lon_deg):
    """日出日落 UTC 时刻（小时偏移自当日 UTC 0 点）。Meeus ch.15 简式。

    返回 (日出小时, 日落小时, 极昼/极夜标记)。
    """
    T = (jd_ut_noon - J2000) / 36525.0
    # 当日 UTC 0 点太阳平黄经与平近点角
    jd0 = math.floor(jd_ut_noon - 0.5) + 0.5
    T0 = (jd0 - J2000) / 36525.0
    L0 = norm_deg(280.46646 + 36000.76983 * T0)
    M = math.radians(norm_deg(357.52911 + 35999.05029 * T0))
    C = 1.914602 * math.sin(M) + 0.019993 * math.sin(2 * M) + 0.000289 * math.sin(3 * M)
    true_lon = norm_deg(L0 + C)
    eps = math.radians(mean_obliquity_deg(jd0))
    dec = math.degrees(math.asin(math.sin(eps) * math.sin(math.radians(true_lon))))
    lat = math.radians(lat_deg)
    cos_h = (math.sin(math.radians(-0.833)) - math.sin(lat) * math.sin(math.radians(dec))) / (
        math.cos(lat) * math.cos(math.radians(dec)))
    if cos_h > 1:
        return None, None, "极夜"
    if cos_h < -1:
        return None, None, "极昼"
    h = math.degrees(math.acos(cos_h))
    solar_noon_ut = 12.0 - lon_deg / 15.0 - equation_of_time_minutes(jd0) / 60.0
    # 恒星时修正：太阳赤经日变化 ≈ 3.94 分钟/天，并入 noon 修正
    sunrise = solar_noon_ut - h / 15.0
    sunset = solar_noon_ut + h / 15.0
    return sunrise, sunset, None


# ---------------------------------------------------------------------------
# 安命宫
# ---------------------------------------------------------------------------

def ming_gong_zhi(sun_palace_zhi, hour_zhi):
    """安命宫：《果老星宗》「以生时加太阳之宫，顺数至卯」。

    命宫支 = 太阳宫支 + (卯 − 生时支) mod 12。
    古典例：太阳子宫+子时生→卯宫；太阳子宫+丑时生→寅宫；太阳酉宫+午时生→午宫。
    """
    offset = (3 - ZHI.index(hour_zhi)) % 12
    return ZHI[(ZHI.index(sun_palace_zhi) + offset) % 12]


# ---------------------------------------------------------------------------
# 恩用难仇
# ---------------------------------------------------------------------------

def en_yong_chou_nan(du_zhu_wuxing):
    """以命度宿五行（度主）为我，分十一曜入恩用仇难（口径声明第 7 条）。"""
    groups = {"恩": [], "用": [], "仇": [], "难": [], "同": []}
    for lum in LUMINARIES:
        wx = LUMINARIES_WUXING[lum]
        if wx == WUXING_SHENGWO[du_zhu_wuxing]:      # 生我 → 恩
            groups["恩"].append(lum)
        elif wx == WUXING_SHENGKE[du_zhu_wuxing]:    # 我生 → 用
            groups["用"].append(lum)
        elif wx == WUXING_KEWO[du_zhu_wuxing]:       # 克我 → 难
            groups["难"].append(lum)
        elif wx == WUXING_WOKE[du_zhu_wuxing]:       # 我克 → 仇
            groups["仇"].append(lum)
        else:
            groups["同"].append(lum)
    return groups


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def compute(solar_date, hour, minute, lat, lon, place=None):
    """排七政四余盘。solar_date=(y,m,d) 公历；hour/minute 北京钟表；lat/lon 度。

    缺 lat/lon 时不计命度/立命宫/昼夜生/恩用难仇，只出十一曜躔度。
    """
    warnings = []
    dt_bj = datetime(solar_date[0], solar_date[1], solar_date[2], hour, minute, tzinfo=BJ)
    dt_utc = dt_bj.astimezone(timezone.utc)
    jd_ut = jd_from_utc(dt_utc)
    jd_tt = jd_ut + delta_t_seconds(dt_utc.year) / 86400.0

    sun = sun_apparent_longitude(jd_tt)
    moon = moon_longitude(jd_tt)
    bodies_tropical = {
        "日": sun, "月": moon,
        "木": planet_longitude("jupiter", jd_ut),
        "火": planet_longitude("mars", jd_ut),
        "土": planet_longitude("saturn", jd_ut),
        "金": planet_longitude("venus", jd_ut),
        "水": planet_longitude("mercury", jd_ut),
        "罗睺": rahu_longitude(jd_tt),
        "计都": ketu_longitude(jd_tt),
        "月孛": yuebei_longitude(jd_tt),
        "紫气": purple_qi_longitude(jd_ut),
    }
    ayan = spica_ayanamsa(jd_tt)
    bodies = {}
    for name, trop in bodies_tropical.items():
        sid = to_sidereal(trop, jd_tt)
        m_name, m_deg, m_wx, m_star = mansion_of(sid)
        bodies[name] = {
            "tropical": trop, "sidereal": sid, "ayanamsa": ayan,
            "mansion": m_name, "mansion_deg": m_deg, "mansion_wx": m_wx, "star": m_star,
        }

    sun_palace = palace_of(to_sidereal(sun, jd_tt))

    result = {
        "jd_ut": jd_ut,
        "ayanamsa": ayan,
        "bodies": bodies,
        "sun_palace_zhi": sun_palace,
        "eot_minutes": equation_of_time_minutes(jd_ut),
    }

    if lat is None or lon is None:
        warnings.append("未提供经纬度（--lat --lon）：命度、立命宫、昼夜生、恩用难仇未计算，只出十一曜躔度")
        result.update({"ming_du": None, "ming_gong": None, "day_night": None, "en_yong": None})
        return result, warnings

    if lat < 0:
        warnings.append("南半球出生：昼夜判定与部分口径无传统定则，结果按北半球公式计算并整体标注")

    asc_trop = ascendant_tropical(jd_ut, jd_tt, lat, lon, result["eot_minutes"])
    asc_sid = to_sidereal(asc_trop, jd_tt)
    m_name, m_deg, m_wx, m_star = mansion_of(asc_sid)
    ming_du = {
        "tropical": asc_trop, "sidereal": asc_sid,
        "mansion": m_name, "mansion_deg": m_deg, "wuxing": m_wx, "star": m_star,
    }
    hour_zhi = _hour_to_shichen(hour, minute)
    ming_gong = ming_gong_zhi(sun_palace, hour_zhi)

    jd_noon = jd_ut  # 附近正午即可，公式内部再取当日 0 点
    sr, ss, polar = sunrise_sunset_utc(jd_noon, lat, lon)
    utc_hours = ((jd_ut + 0.5) % 1.0) * 24.0  # JD 自正午起算，先转自 0 点起算
    local_hours = utc_hours + lon / 15.0  # 当地平太阳时（近似，用于昼夜粗判）
    if polar:
        day_night = {"type": polar, "note": "极昼/极夜，昼夜生传统口径不适用"}
    else:
        local_apparent = local_hours + result["eot_minutes"] / 60.0
        sr_local = (sr + lon / 15.0) % 24.0
        ss_local = (ss + lon / 15.0) % 24.0
        if sr_local <= local_apparent < ss_local:
            day_night = {"type": "昼生", "sunrise_local": sr_local, "sunset_local": ss_local}
        else:
            day_night = {"type": "夜生", "sunrise_local": sr_local, "sunset_local": ss_local}

    result["ming_du"] = ming_du
    result["ming_gong"] = {"zhi": ming_gong, "wuxing": PALACE_WUXING[ming_gong],
                           "sun_palace": sun_palace, "hour_zhi": hour_zhi}
    result["day_night"] = day_night
    result["du_zhu_wuxing"] = MANSION_WX_TO_PHASE[m_wx]
    result["en_yong"] = en_yong_chou_nan(result["du_zhu_wuxing"])
    return result, warnings


def _hour_to_shichen(hour, minute):
    total = hour * 60 + minute
    if total >= 23 * 60 or total < 60:
        return "子"
    return ZHI[((hour + 1) // 2) % 12]


def format_report(result, warnings, meta):
    lines = []
    lines.append("## 输入")
    lines.append("- 阳历：%s %02d:%02d（北京时间）" % (meta["solar"], meta["hour"], meta["minute"]))
    if meta.get("place"):
        lines.append("- 出生地：%s（纬 %.2f，经 %.2f）" % (meta["place"], meta["lat"], meta["lon"]))
    else:
        lines.append("- 经纬度：纬 %.2f，经 %.2f" % (meta["lat"], meta["lon"]))
    lines.append("")
    lines.append("## 口径声明（详见文件头）")
    lines.append("- 恒星制，角宿一=0°，ayanamsa=%.4f°" % result["ayanamsa"])
    lines.append("- 计都=罗睺对冲；紫气=28岁周天锚点 1975-03-13 16:00 UT=230.5°")
    lines.append("- 精度：日月 0.05° / 行星角分级 / 升度含均时差校正")
    lines.append("")
    lines.append("## 七政四余躔度")
    lines.append("| 星 | 黄道经度 | 恒星黄经 | 躔宿 | 入宿度 | 宿五行 |")
    lines.append("|---|---|---|---|---|---|")
    for name in LUMINARIES:
        b = result["bodies"][name]
        lines.append(
            "| %s | %.4f | %.4f | %s宿 | %.2f | %s |"
            % (name, b["tropical"], b["sidereal"], b["mansion"], b["mansion_deg"], b["mansion_wx"])
        )
    lines.append("")
    if result.get("ming_du") is None:
        lines.append("## 警告")
        for w in warnings:
            lines.append("- %s" % w)
        lines.append("")
        return "\n".join(lines)

    md = result["ming_du"]
    mg = result["ming_gong"]
    lines.append("## 命度（真升点，恒星制）")
    lines.append("- 黄道经度：%.4f → 恒星 %.4f" % (md["tropical"], md["sidereal"]))
    lines.append("- 命躔：%s宿%.2f度（度主五行：%s，距星 %s）" % (md["mansion"], md["mansion_deg"], md["wuxing"], md["star"]))
    lines.append("")
    lines.append("## 立命宫（果老安命法）")
    lines.append("- 太阳踞 %s 宫，生时 %s 时 → 命宫在 %s 宫（宫五行 %s）" % (
        mg["sun_palace"], mg["hour_zhi"], mg["zhi"], mg["wuxing"]))
    lines.append("")
    dn = result["day_night"]
    lines.append("## 昼夜生")
    if dn["type"] in ("极昼", "极夜"):
        lines.append("- %s：%s" % (dn["type"], dn.get("note", "")))
    else:
        lines.append("- 日出（当地平太阳时）：%02d:%02d｜日落：%02d:%02d" % (
            int(dn["sunrise_local"]), int(round((dn["sunrise_local"] % 1) * 60)),
            int(dn["sunset_local"]), int(round((dn["sunset_local"] % 1) * 60))))
        lines.append("- 判定：%s（昼生重日，夜生重月）" % dn["type"])
    lines.append("")
    lines.append("## 恩用难仇（以命度宿五行为我：%s；日宿取火、月宿取水）" % result["du_zhu_wuxing"])
    ey = result["en_yong"]
    meaning = {"恩": "生我者——印贵扶持", "用": "我生者——才华施展",
               "难": "克我者——压力侵害", "仇": "我克者——消耗争斗", "同": "同我者——命度同气"}
    lines.append("| 关系 | 五行 | 对应星曜 | 含义 |")
    lines.append("|---|---|---|---|")
    for key in ("恩", "用", "难", "仇", "同"):
        members = ey.get(key, [])
        wx = {"恩": None, "用": None, "难": None, "仇": None, "同": md["wuxing"]}[key]
        if key != "同":
            wxs = {LUMINARIES_WUXING[m] for m in members}
            wx = "、".join(sorted(wxs)) if wxs else "—"
        lines.append("| %s | %s | %s | %s |" % (
            key, wx or "—", "、".join(members) if members else "—", meaning[key]))
    lines.append("")
    lines.append("## 真太阳时副产品")
    lines.append("- 均时差：%.2f 分钟（真太阳时 = 平太阳时 %+d 分）" % (result["eot_minutes"], round(result["eot_minutes"])))
    lines.append("")
    lines.append("## 警告")
    if warnings:
        for w in warnings:
            lines.append("- %s" % w)
    else:
        lines.append("- 无")
    lines.append("")
    return "\n".join(lines)


def build_parser():
    p = argparse.ArgumentParser(description="七政四余排盘（恒星制，无第三方依赖）")
    p.add_argument("--solar", required=True, help="阳历 YYYY-MM-DD")
    p.add_argument("--hour", required=True, help="出生钟点 HH:MM（北京时间）")
    p.add_argument("--lat", type=float, default=None, help="出生纬度（度，北正）")
    p.add_argument("--lon", type=float, default=None, help="出生经度（度，东正）")
    p.add_argument("--place", help="出生地名称（仅展示）")
    return p


def run(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        y, m, d = (int(x) for x in args.solar.split("-"))
    except ValueError:
        parser.error("--solar 需要 YYYY-MM-DD")
        return 2
    try:
        hh, mm = (int(x) for x in args.hour.split(":"))
        if not (0 <= hh <= 23 and 0 <= mm <= 59):
            raise ValueError
    except ValueError:
        parser.error("--hour 需要 HH:MM")
        return 2

    result, warnings = compute((y, m, d), hh, mm, args.lat, args.lon, args.place)
    report = format_report(result, warnings, {"solar": args.solar, "hour": hh, "minute": mm,
                                              "lat": args.lat, "lon": args.lon, "place": args.place})
    sys.stdout.write(report)
    return 0


def main():
    sys.exit(run())


if __name__ == "__main__":
    main()
