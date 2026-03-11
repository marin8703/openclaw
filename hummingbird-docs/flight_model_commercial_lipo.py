#!/usr/bin/env python3
"""
Hummingbird Flight Model — Commercial Off-The-Shelf LiPo Packs
================================================================
Uses real-world LiPo pack specs you can buy today.
No exotic chemistry. Standard hobby/industrial packs.
"""

import math

G = 9.81
RHO = 1.225
INCH_TO_M = 0.0254

# =============================================================================
# REAL COMMERCIAL LIPO PACKS (6S, 22.2V nominal)
# Specs from Tattu, CNHL, Gaoneng, Turnigy, etc.
# =============================================================================

commercial_packs = [
    # (name, capacity_mah, weight_g, max_charge_c, energy_density_whkg, price_approx)
    ("Tattu 1300mAh 6S 75C",      1300,  198,  2.0,  146, "$30"),
    ("Tattu 1550mAh 6S 75C",      1550,  228,  2.0,  151, "$35"),
    ("CNHL 1500mAh 6S 100C",      1500,  213,  3.0,  156, "$25"),
    ("Tattu 2200mAh 6S 45C",      2200,  336,  2.0,  145, "$45"),
    ("Gaoneng 2200mAh 6S 60C",    2200,  310,  3.0,  158, "$35"),
    ("Tattu 3000mAh 6S 45C",      3000,  432,  1.5,  154, "$55"),
    ("Tattu 4000mAh 6S 45C",      4000,  560,  1.5,  159, "$65"),
    ("Tattu 5000mAh 6S 45C",      5000,  680,  1.5,  163, "$75"),
    ("CNHL 5000mAh 6S 70C",       5000,  714,  3.0,  155, "$60"),
    ("Tattu 6000mAh 6S 35C",      6000,  830,  1.0,  161, "$85"),
    ("Tattu 6750mAh 6S 35C",      6750,  905,  1.0,  166, "$90"),
    ("Tattu 8000mAh 6S 35C",      8000, 1040,  1.0,  171, "$100"),
    ("Tattu 10000mAh 6S 25C",    10000, 1280,  1.0,  174, "$120"),
    ("Tattu 12000mAh 6S 22C",    12000, 1530,  1.0,  174, "$140"),
    ("Multistar 5200mAh 6S 10C",  5200,  710,  1.0,  163, "$40"),  # budget option
    ("Molicel-based custom 6S",    5400,  520,  2.0,  230, "$90"),  # premium 21700 pack
]

# =============================================================================
# HB-18 DRY WEIGHT (no battery)
# =============================================================================
DRY_WEIGHT_G = 1793  # from main model (frame+motors+ESCs+FC+wiring+comms+sensors+payload+docking+misc+jetson)
DRY_WEIGHT_NO_PAYLOAD_G = 793  # without 1kg payload

# Electronics power
ELECTRONICS_W = 21.5  # Pixhawk 2W + Jetson 10W + comms 3W + sensors 1.5W + payload 5W

def calc_hover_power(auw_kg):
    """Momentum theory hover power for ducted coaxial quad."""
    prop_r = (6.0 * INCH_TO_M) / 2  # 6" props
    disc_area = math.pi * prop_r ** 2
    
    thrust_per_duct = (auw_kg * G) / 4
    coax_eff = 0.85
    duct_aug = 1.20
    
    front_t = thrust_per_duct / ((1 + coax_eff) * duct_aug)
    rear_t = front_t * coax_eff
    
    P_front = front_t ** 1.5 / math.sqrt(2 * RHO * disc_area)
    P_rear = (rear_t ** 1.5 / math.sqrt(2 * RHO * disc_area)) * 1.2
    
    P_ideal = 4 * (P_front + P_rear)
    
    motor_eff = 0.82
    esc_eff = 0.95
    hover_derating = 0.90
    
    return P_ideal / motor_eff / esc_eff / hover_derating


def analyze_with_real_world_factor(factor, label):
    """Run analysis with a real-world derating factor applied to flight time."""
    
    print(f"\n{'='*90}")
    print(f"  COMMERCIAL LIPO ANALYSIS — {label} (×{factor} real-world factor)")
    print(f"  HB-18 Primary with 1kg payload | Dry weight: {DRY_WEIGHT_G}g")
    print(f"{'='*90}")
    
    print(f"\n  {'Pack':<35} {'mAh':>6} {'Wt(g)':>6} {'AUW':>6} {'Wh':>6} {'Usable':>7} "
          f"{'HvrPwr':>7} {'TotPwr':>7} {'Flight':>7} {'RealFlt':>8} {'T/W':>5} {'ChgC':>5} {'ChgMin':>7} {'$/unit':>6}")
    print(f"  {'-'*35} {'-'*6} {'-'*6} {'-'*6} {'-'*6} {'-'*7} "
          f"{'-'*7} {'-'*7} {'-'*7} {'-'*8} {'-'*5} {'-'*5} {'-'*7} {'-'*6}")
    
    viable = []
    
    for name, mah, weight_g, max_charge_c, whkg, price in commercial_packs:
        auw_g = DRY_WEIGHT_G + weight_g
        auw_kg = auw_g / 1000
        
        capacity_wh = (mah / 1000) * 22.2
        usable_wh = capacity_wh * 0.80 * 0.95  # 80% DoD, 5% sag
        
        hover_pwr = calc_hover_power(auw_kg)
        total_pwr = hover_pwr + ELECTRONICS_W
        
        flight_min = (usable_wh / total_pwr) * 60
        real_flight = flight_min * factor
        
        # T/W
        disc_a = math.pi * ((6.0 * INCH_TO_M) / 2) ** 2
        A_eff = 4 * disc_a * 1.5
        max_pwr = 8 * 350 * 0.95
        max_thrust = (max_pwr ** 2 * 2 * RHO * A_eff) ** (1/3)
        tw = max_thrust / (auw_kg * G)
        
        charge_min = 60 / max_charge_c
        
        flag = ""
        if tw < 1.5:
            flag = " ⚠️LOW T/W"
        elif tw < 2.0:
            flag = " ⚠️"
        elif real_flight >= 20 and tw >= 2.0:
            flag = " ✅"
            viable.append((name, mah, weight_g, auw_g, real_flight, tw, max_charge_c, charge_min, price))
        
        print(f"  {name:<35} {mah:>6} {weight_g:>6} {auw_g:>6} {capacity_wh:>6.1f} {usable_wh:>7.1f} "
              f"{hover_pwr:>7.1f} {total_pwr:>7.1f} {flight_min:>7.1f} {real_flight:>7.1f}m {tw:>5.2f} {max_charge_c:>4.1f}C {charge_min:>6.0f}m {price:>6}{flag}")
    
    # Swarm analysis for viable packs
    if viable:
        print(f"\n  {'─'*90}")
        print(f"  SWARM CONTINUOUS COVERAGE (from 30 drones, 4 min transit overhead)")
        print(f"  {'─'*90}")
        print(f"  {'Pack':<35} {'Flight':>7} {'ChgTime':>8} {'Airborne':>9} {'SimChg@7kW':>11} {'Cost×30':>8}")
        print(f"  {'-'*35} {'-'*7} {'-'*8} {'-'*9} {'-'*11} {'-'*8}")
        
        for name, mah, wt, auw, flt, tw, chg_c, chg_min, price in viable:
            transit = 4
            cycle = flt + chg_min + transit
            airborne = 30 * flt / cycle
            
            charge_power = (mah/1000) * chg_c * 22.2
            sim_charge = int(7000 / charge_power)
            
            price_num = int(price.replace("$",""))
            cost_30 = f"${price_num * 30}"
            
            print(f"  {name:<35} {flt:>6.1f}m {chg_min:>7.0f}m {airborne:>9.1f} {sim_charge:>9} {cost_30:>8}")
    
    return viable


# =============================================================================
# PAYLOAD SENSITIVITY WITH BEST COMMERCIAL PACK
# =============================================================================
def payload_sweep(pack_name, pack_mah, pack_weight, max_charge_c, factor):
    print(f"\n{'='*70}")
    print(f"  PAYLOAD SENSITIVITY — {pack_name}")
    print(f"  Real-world factor: ×{factor}")
    print(f"{'='*70}")
    
    print(f"  {'Payload':>10} {'AUW':>8} {'Flight':>10} {'Real Flt':>10} {'T/W':>6}")
    print(f"  {'-'*10} {'-'*8} {'-'*10} {'-'*10} {'-'*6}")
    
    capacity_wh = (pack_mah / 1000) * 22.2
    usable_wh = capacity_wh * 0.80 * 0.95
    
    for payload in [0, 100, 200, 300, 500, 750, 1000, 1500]:
        dry = DRY_WEIGHT_NO_PAYLOAD_G + payload
        auw_g = dry + pack_weight
        auw_kg = auw_g / 1000
        
        hover_pwr = calc_hover_power(auw_kg)
        # Adjust electronics for payload
        if payload == 0:
            elec = ELECTRONICS_W - 5.0 + 1.0  # no payload camera, just basic sensors
        else:
            elec = ELECTRONICS_W
        total_pwr = hover_pwr + elec
        
        flight_min = (usable_wh / total_pwr) * 60
        real_flight = flight_min * factor
        
        disc_a = math.pi * ((6.0 * INCH_TO_M) / 2) ** 2
        A_eff = 4 * disc_a * 1.5
        max_pwr = 8 * 350 * 0.95
        max_thrust = (max_pwr ** 2 * 2 * RHO * A_eff) ** (1/3)
        tw = max_thrust / (auw_kg * G)
        
        flag = " ⚠️" if tw < 2.0 else ""
        print(f"  {payload:>9}g {auw_g:>7}g {flight_min:>9.1f}m {real_flight:>9.1f}m {tw:>5.2f}{flag}")


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    print("█" * 90)
    print("  HUMMINGBIRD HB-18 — COMMERCIAL OFF-THE-SHELF LIPO ANALYSIS")
    print("█" * 90)
    
    # Run with model-only (no derating)
    print("\n" + "▓" * 90)
    print("  SECTION 1: RAW MODEL (hover theory, no derating)")
    print("▓" * 90)
    analyze_with_real_world_factor(1.0, "Raw Model")
    
    # Run with 65% real-world factor (to match docs)
    print("\n" + "▓" * 90)
    print("  SECTION 2: WITH 65% REAL-WORLD FACTOR (matches doc specs)")
    print("  (Accounts for: wind, maneuvering, altitude hold corrections,")
    print("   non-hover flight profiles, safety reserve)")
    print("▓" * 90)
    viable = analyze_with_real_world_factor(0.65, "Real-World Estimated")
    
    # Payload sweep with a good mid-range pack
    if viable:
        # Pick the best viable pack for payload analysis
        best = max(viable, key=lambda x: x[4])  # longest real flight
        payload_sweep(best[0], best[1], best[2], best[6], 0.65)
    
    # Quick reference: what you'd actually buy
    print(f"\n{'='*70}")
    print(f"  💡 RECOMMENDED STARTING PACKS (available now, good balance)")
    print(f"{'='*70}")
    print(f"""
  FOR PROTOTYPING (P1):
  • Tattu 5000mAh 6S 45C — ~$75, 680g, good all-rounder
  • CNHL 5000mAh 6S 70C — ~$60, 714g, better charge rate (3C)
  
  FOR LONGER FLIGHTS:
  • Tattu 6750mAh 6S 35C — ~$90, 905g, more capacity but heavier
  • Tattu 8000mAh 6S 35C — ~$100, 1040g, near doc spec battery weight
  
  FOR LIGHTER BUILDS (reduced payload):
  • Tattu 4000mAh 6S 45C — ~$65, 560g, good if payload < 500g
  
  PREMIUM (if budget allows):
  • Molicel 21700 custom pack — ~$90, 520g for 5400mAh, best Wh/kg
    (230 Wh/kg vs ~160 for standard packs)
    
  NOTE: Standard LiPo packs are 145-175 Wh/kg. Premium cells
  (Molicel, Samsung 50S) hit 200-230 Wh/kg but need custom packs.
  For P1 prototyping, off-the-shelf is the way to go.
""")
    
    print("✅ Analysis complete.\n")
