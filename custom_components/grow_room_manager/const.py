"""Constants for Grow Room Manager integration."""
from typing import Final

DOMAIN: Final = "grow_room_manager"
CONF_ROOMS: Final = "rooms"
CONF_ROOM_ID: Final = "room_id"
CONF_ROOM_NAME: Final = "name"
CONF_CALENDAR_ENTITY: Final = "calendar_entity"
CONF_TODO_ENTITY: Final = "todo_entity"
CONF_START_DATE_ENTITY: Final = "start_date_entity"
CONF_START_DATE: Final = "start_date"

# Grow phases
PHASE_STRETCH: Final = "Stretch"
PHASE_BULK: Final = "Bulk"
PHASE_FINISH: Final = "Finish"

# EC targets by phase
EC_STRETCH: Final = 3.0
EC_BULK: Final = 3.0
EC_FINISH: Final = 1.5  # Fade nutrients

# Dryback targets by phase
DRYBACK_STRETCH: Final = "20-25%"
DRYBACK_BULK: Final = "30-40%"
DRYBACK_FINISH: Final = "40-50%"

# Service names
SERVICE_ADD_JOURNAL: Final = "add_journal_entry"
SERVICE_GENERATE_TASKS: Final = "generate_tasks"
SERVICE_CLEAR_TASKS: Final = "clear_tasks"
SERVICE_EXPORT_JOURNAL: Final = "export_journal"
SERVICE_SET_START_DATE: Final = "set_start_date"
SERVICE_GET_TODAY_TASKS: Final = "get_today_tasks"

# Athena Pro Line Feeding Recipes (grams per liter)
# Based on Athena Pro Line feed charts
ATHENA_FEED_CHART: Final = {
    # Phase: {product: grams_per_liter}
    PHASE_STRETCH: {
        "core": 0.79,      # 3g per gallon = 0.79g/L
        "bloom": 0.79,     # 3g per gallon = 0.79g/L
        "cleanse": 0,      # Not used in stretch
        "fade": 0,         # Not used in stretch
        "target_ec": 3.0,
        "target_ph": "5.8-6.0",
    },
    PHASE_BULK: {
        "core": 0.79,      # 3g per gallon = 0.79g/L
        "bloom": 0.79,     # 3g per gallon = 0.79g/L
        "cleanse": 0,      # Optional weekly
        "fade": 0,         # Not used in bulk
        "target_ec": 3.0,
        "target_ph": "5.8-6.0",
    },
    PHASE_FINISH: {
        "core": 0,         # No core in finish
        "bloom": 0,        # No bloom in finish
        "cleanse": 0.26,   # 1g per gallon = 0.26g/L (optional flush)
        "fade": 0.79,      # 3g per gallon = 0.79g/L
        "target_ec": 1.5,
        "target_ph": "5.8-6.0",
    },
}

# Common tank sizes in liters
TANK_SIZES: Final = [20, 50, 100, 200, 500, 1000]

# Athena Pro Line Schedule - Maps day number to task info
# Format: {day: {"title": str, "description": str, "category": str, "phase": str, ...}}
ATHENA_SCHEDULE: Final = {
    # =========================================================================
    # PHASE 1: STRETCH (Weeks 1-3, Days 1-21)
    # =========================================================================
    1: {
        "title": "🌱 FLIP DAY - Begin Flower Cycle",
        "description": (
            "DAY 1 OF FLOWER - FLIP DAY\n\n"
            "ACTIONS REQUIRED:\n"
            "• Switch light cycle to 12/12\n"
            "• Set Input EC to 3.0 (Athena Pro Core + Bloom)\n"
            "• Record baseline plant heights for stretch tracking\n"
            "• Verify VPD is 1.0-1.2 kPa for early flower\n\n"
            "NUTRIENT MIX (per 100gal):\n"
            "• Athena Core: 300g\n"
            "• Athena Bloom: 300g\n"
            "• Target pH: 5.8-6.0\n\n"
            "[Source: Athena Handbook, Pro Feed Chart]"
        ),
        "category": "milestone",
        "phase": PHASE_STRETCH,
        "priority": "high",
        "duration_hours": 1,
    },
    2: {
        "title": "✂️ HEAVY DEFOLIATION - Strip & Clean",
        "description": (
            "DAY 2 - HEAVY DEFOLIATION (STRIP)\n\n"
            "ACTIONS REQUIRED:\n"
            "• Remove ALL fan leaves from bottom 1/3 of plant (lollipop)\n"
            "• Strip all sucker branches and weak growth\n"
            "• Remove any yellowing or damaged leaves\n"
            "• Clean up floor/medium surface of debris\n"
            "• Sanitize tools between plants (70% isopropyl)\n\n"
            "GOALS:\n"
            "• Improve airflow through canopy\n"
            "• Direct energy to top flower sites\n"
            "• Reduce humidity pockets and mold risk\n"
            "• Establish clean baseline for stretch phase\n\n"
            "ESTIMATED TIME: 2-5 min per plant\n\n"
            "[Source: Athena Handbook, Defoliation Protocol]"
        ),
        "category": "defoliation",
        "phase": PHASE_STRETCH,
        "priority": "high",
        "duration_hours": 4,
    },
    3: {
        "title": "🐛 IPM Spray Application #1",
        "description": (
            "WEEK 1 - IPM SPRAY (Application 1 of 6)\n\n"
            "SPRAY PROTOCOL:\n"
            "• Apply IPM spray to ALL leaf surfaces (top & bottom)\n"
            "• Spray during lights-off or low light period\n"
            "• Ensure full coverage including stems\n"
            "• Allow plants to dry before lights on\n\n"
            "RECOMMENDED PRODUCTS:\n"
            "• Athena IPM (2-4 oz/gal)\n"
            "• Alternative: Neem oil, Spinosad, or BT\n"
            "• Rotate products to prevent resistance\n\n"
            "TARGETS:\n"
            "• Spider mites, thrips, aphids\n"
            "• Powdery mildew prevention\n"
            "• Fungus gnats (soil drench option)\n\n"
            "⚠️ CONTINUE 2x/WEEK UNTIL DAY 21\n\n"
            "[Source: Athena Handbook, IPM Protocol]"
        ),
        "category": "ipm",
        "phase": PHASE_STRETCH,
        "priority": "high",
        "duration_hours": 2,
    },
    7: {
        "title": "🐛 IPM Spray Application #2",
        "description": (
            "WEEK 1 - IPM SPRAY (Application 2 of 6)\n\n"
            "SPRAY PROTOCOL:\n"
            "• Apply IPM spray to ALL leaf surfaces\n"
            "• Focus on undersides of leaves\n"
            "• Check for any pest activity before spraying\n"
            "• Document any issues found\n\n"
            "INSPECTION CHECKLIST:\n"
            "□ Check leaf undersides for mites/eggs\n"
            "□ Inspect new growth for thrips damage\n"
            "□ Look for aphids on stems\n"
            "□ Check soil surface for fungus gnats\n\n"
            "STRETCH PROGRESS CHECK:\n"
            "• Plants should be 10-20% taller than Day 1\n"
            "• Internodal spacing increasing\n\n"
            "[Source: Athena Handbook, IPM Protocol]"
        ),
        "category": "ipm",
        "phase": PHASE_STRETCH,
        "priority": "medium",
        "duration_hours": 2,
    },
    10: {
        "title": "🐛 IPM Spray Application #3",
        "description": (
            "WEEK 2 - IPM SPRAY (Application 3 of 6)\n\n"
            "SPRAY PROTOCOL:\n"
            "• Continue full coverage IPM application\n"
            "• Consider rotating to different product\n"
            "• Spray early in dark cycle\n\n"
            "WEEK 2 OBSERVATIONS:\n"
            "• Stretch should be 30-50% complete\n"
            "• First pistils may be visible\n"
            "• Maintain EC at 3.0\n"
            "• VPD target: 1.0-1.2 kPa\n\n"
            "ENVIRONMENTAL TARGETS:\n"
            "• Day temp: 78-82°F (25-28°C)\n"
            "• Night temp: 68-72°F (20-22°C)\n"
            "• Humidity: 55-65% RH\n\n"
            "[Source: Athena Handbook, IPM Protocol]"
        ),
        "category": "ipm",
        "phase": PHASE_STRETCH,
        "priority": "medium",
        "duration_hours": 2,
    },
    14: {
        "title": "🐛 IPM Spray Application #4 + Week 2 Check",
        "description": (
            "WEEK 2 - IPM SPRAY (Application 4 of 6)\n\n"
            "SPRAY PROTOCOL:\n"
            "• Full coverage IPM application\n"
            "• This is the halfway point for IPM sprays\n\n"
            "WEEK 2 HEALTH CHECK:\n"
            "□ Measure plant heights (record stretch %)\n"
            "□ Check for nutrient deficiencies\n"
            "□ Verify runoff EC (should be within 0.5 of input)\n"
            "□ Inspect roots if visible (should be white)\n"
            "□ Check for any hermaphrodite signs\n\n"
            "COMMON ISSUES TO WATCH:\n"
            "• Calcium deficiency (brown spots)\n"
            "• Nitrogen toxicity (dark, clawing leaves)\n"
            "• Light stress (bleaching, taco leaves)\n\n"
            "[Source: Athena Handbook, IPM Protocol]"
        ),
        "category": "ipm",
        "phase": PHASE_STRETCH,
        "priority": "medium",
        "duration_hours": 2,
    },
    17: {
        "title": "🐛 IPM Spray Application #5",
        "description": (
            "WEEK 3 - IPM SPRAY (Application 5 of 6)\n\n"
            "SPRAY PROTOCOL:\n"
            "• Second to last IPM spray!\n"
            "• Ensure thorough coverage\n"
            "• Flowers are forming - be gentle\n\n"
            "⚠️ IMPORTANT NOTES:\n"
            "• Flowers are developing - avoid direct spray on buds\n"
            "• Focus on fan leaves and stems\n"
            "• Only 1 more spray after this!\n\n"
            "STRETCH STATUS:\n"
            "• Should be 70-90% of final stretch\n"
            "• Flower sites clearly visible\n"
            "• Trichome production beginning\n\n"
            "[Source: Athena Handbook, IPM Protocol]"
        ),
        "category": "ipm",
        "phase": PHASE_STRETCH,
        "priority": "medium",
        "duration_hours": 2,
    },
    21: {
        "title": "⚠️ DAY 21 DEFOLIATION + FINAL IPM - CRITICAL",
        "description": (
            "DAY 21 - CRITICAL MILESTONE\n\n"
            "🚨 THIS IS THE LAST DAY FOR IPM SPRAYS! 🚨\n\n"
            "DEFOLIATION (SKIRT UP):\n"
            "• Remove lower 1/3 canopy growth again\n"
            "• Strip any leaves blocking bud sites\n"
            "• Remove small/larfy lower flowers\n"
            "• Clean up any dead/yellowing material\n\n"
            "FINAL IPM SPRAY (Application 6 of 6):\n"
            "• Last chance for foliar pest control\n"
            "• After today, NO MORE SPRAYS on flowers\n"
            "• Any pest issues after this = biological controls only\n\n"
            "POST-DAY 21 PEST MANAGEMENT:\n"
            "• Beneficial insects (ladybugs, predatory mites)\n"
            "• Sticky traps for monitoring\n"
            "• Environmental controls (temp, humidity)\n\n"
            "STRETCH COMPLETE:\n"
            "• Record final plant heights\n"
            "• Calculate total stretch percentage\n"
            "• Prepare for Bulk phase\n\n"
            "[Source: Athena Handbook, IPM & Defoliation Protocol]"
        ),
        "category": "defoliation",
        "phase": PHASE_STRETCH,
        "priority": "critical",
        "duration_hours": 4,
    },
    # =========================================================================
    # PHASE 2: BULK (Weeks 4-8, Days 22-56)
    # Maintenance pruning every 3 days for airflow
    # =========================================================================
    22: {
        "title": "🌸 BEGIN BULK PHASE - Vegetative Steering",
        "description": (
            "DAY 22 - BULK PHASE BEGINS\n\n"
            "PHASE TRANSITION:\n"
            "• Stretch is complete - focus shifts to flower development\n"
            "• Implement vegetative crop steering strategy\n"
            "• Target 30-40% dryback between irrigations\n\n"
            "CROP STEERING STRATEGY:\n"
            "• Vegetative steering = larger drybacks\n"
            "• Encourages root growth and plant vigor\n"
            "• First irrigation 2-3 hours after lights on\n"
            "• Last irrigation 2-3 hours before lights off\n\n"
            "IRRIGATION ADJUSTMENTS:\n"
            "• Reduce irrigation frequency\n"
            "• Increase shot sizes slightly\n"
            "• Monitor substrate EC (should rise slightly)\n"
            "• Target 30-40% dryback overnight\n\n"
            "ENVIRONMENTAL TARGETS:\n"
            "• Day temp: 78-82°F (25-28°C)\n"
            "• Night temp: 65-70°F (18-21°C)\n"
            "• Humidity: 50-60% RH\n"
            "• VPD: 1.2-1.4 kPa\n\n"
            "[Source: Athena Handbook, Crop Steering]"
        ),
        "category": "steering",
        "phase": PHASE_BULK,
        "priority": "high",
        "duration_hours": 1,
    },
    # Bulk Phase - Maintenance every 3 days (Days 25, 28, 31, 34, 37, 40, 43, 46, 49, 52, 55)
    25: {
        "title": "🔧 Maintenance Check - Airflow & Canopy (Day 25)",
        "description": (
            "BULK PHASE - MAINTENANCE DAY (Every 3 Days)\n\n"
            "CANOPY MANAGEMENT:\n"
            "□ Remove any leaves blocking light to bud sites\n"
            "□ Tuck large fan leaves under canopy if possible\n"
            "□ Remove any dead or yellowing leaves\n"
            "□ Check for and remove any male flowers/hermies\n\n"
            "AIRFLOW CHECK:\n"
            "□ Ensure air movement through entire canopy\n"
            "□ No stagnant air pockets (mold risk)\n"
            "□ Fans oscillating properly\n"
            "□ Check for any moisture buildup on leaves\n\n"
            "PLANT HEALTH INSPECTION:\n"
            "□ Look for pest damage (spots, webbing, eggs)\n"
            "□ Check for nutrient deficiencies\n"
            "□ Inspect flower development progress\n"
            "□ Note any plants lagging behind\n\n"
            "CURRENT TARGETS:\n"
            "• EC Input: 3.0 | Dryback: 30-40%\n"
            "• VPD: 1.2-1.4 kPa\n\n"
            "[Source: Athena Handbook, Crop Steering]"
        ),
        "category": "maintenance",
        "phase": PHASE_BULK,
        "priority": "medium",
        "duration_hours": 1,
    },
    28: {
        "title": "🔧 Maintenance Check - Week 4 Complete (Day 28)",
        "description": (
            "BULK PHASE - MAINTENANCE DAY (Week 4 Complete)\n\n"
            "CANOPY MANAGEMENT:\n"
            "□ Light defoliation - remove blocking leaves\n"
            "□ Tuck or remove large fans\n"
            "□ Clean up any larf or weak growth\n"
            "□ Ensure even canopy height\n\n"
            "AIRFLOW CHECK:\n"
            "□ Verify air circulation through canopy\n"
            "□ Check humidity levels in dense areas\n"
            "□ Adjust fans if needed\n\n"
            "WEEK 4 PROGRESS CHECK:\n"
            "□ Flowers should be golf ball sized or larger\n"
            "□ Trichome production increasing\n"
            "□ Strong flower smell developing\n"
            "□ No signs of bud rot or PM\n\n"
            "IRRIGATION CHECK:\n"
            "□ Verify 30-40% dryback achieved\n"
            "□ Check runoff EC (target: input + 0.5-1.0)\n"
            "□ Adjust irrigation timing if needed\n\n"
            "[Source: Athena Handbook, Crop Steering]"
        ),
        "category": "maintenance",
        "phase": PHASE_BULK,
        "priority": "medium",
        "duration_hours": 1,
    },
    31: {
        "title": "🔧 Maintenance Check - Airflow & Canopy (Day 31)",
        "description": (
            "BULK PHASE - MAINTENANCE DAY (Every 3 Days)\n\n"
            "CANOPY MANAGEMENT:\n"
            "□ Remove leaves blocking bud sites\n"
            "□ Check for overcrowding\n"
            "□ Remove any dead material\n"
            "□ Inspect for hermaphrodite flowers\n\n"
            "AIRFLOW CHECK:\n"
            "□ Air moving through all areas\n"
            "□ No wet spots on leaves\n"
            "□ Humidity staying in range\n\n"
            "FLOWER DEVELOPMENT:\n"
            "□ Buds stacking and gaining density\n"
            "□ Pistils mostly white\n"
            "□ Trichomes developing (clear/cloudy)\n"
            "□ Smell intensifying\n\n"
            "CURRENT TARGETS:\n"
            "• EC Input: 3.0 | Dryback: 30-40%\n"
            "• VPD: 1.2-1.4 kPa\n\n"
            "[Source: Athena Handbook, Crop Steering]"
        ),
        "category": "maintenance",
        "phase": PHASE_BULK,
        "priority": "medium",
        "duration_hours": 1,
    },
    34: {
        "title": "🔧 Maintenance Check - Airflow & Canopy (Day 34)",
        "description": (
            "BULK PHASE - MAINTENANCE DAY (Every 3 Days)\n\n"
            "CANOPY MANAGEMENT:\n"
            "□ Light leaf removal for airflow\n"
            "□ Support heavy branches if needed\n"
            "□ Remove any yellowing lower leaves\n"
            "□ Check plant spacing\n\n"
            "AIRFLOW CHECK:\n"
            "□ Verify air circulation\n"
            "□ Check for condensation\n"
            "□ Monitor humidity in canopy\n\n"
            "STRUCTURAL SUPPORT:\n"
            "□ Add trellis support if branches heavy\n"
            "□ Tie up any leaning plants\n"
            "□ Ensure even light distribution\n\n"
            "CURRENT TARGETS:\n"
            "• EC Input: 3.0 | Dryback: 30-40%\n"
            "• VPD: 1.2-1.4 kPa\n\n"
            "[Source: Athena Handbook, Crop Steering]"
        ),
        "category": "maintenance",
        "phase": PHASE_BULK,
        "priority": "medium",
        "duration_hours": 1,
    },
    37: {
        "title": "🔧 Maintenance Check - Airflow & Canopy (Day 37)",
        "description": (
            "BULK PHASE - MAINTENANCE DAY (Every 3 Days)\n\n"
            "CANOPY MANAGEMENT:\n"
            "□ Remove any leaves touching buds\n"
            "□ Clear interior canopy for airflow\n"
            "□ Remove dead/dying leaves\n\n"
            "AIRFLOW CHECK:\n"
            "□ Air movement through all zones\n"
            "□ No moisture accumulation\n"
            "□ Fans functioning properly\n\n"
            "FLOWER INSPECTION:\n"
            "□ Buds gaining significant weight\n"
            "□ Check for bud rot (gray/brown spots)\n"
            "□ Trichomes mostly cloudy\n"
            "□ Some pistils turning orange\n\n"
            "CURRENT TARGETS:\n"
            "• EC Input: 3.0 | Dryback: 30-40%\n"
            "• VPD: 1.2-1.4 kPa\n\n"
            "[Source: Athena Handbook, Crop Steering]"
        ),
        "category": "maintenance",
        "phase": PHASE_BULK,
        "priority": "medium",
        "duration_hours": 1,
    },
    40: {
        "title": "🔧 Maintenance Check - Pre-Day 42 Prep (Day 40)",
        "description": (
            "BULK PHASE - MAINTENANCE DAY (Every 3 Days)\n\n"
            "⚠️ MAJOR PRUNE IN 2 DAYS - PREPARE!\n\n"
            "CANOPY ASSESSMENT:\n"
            "□ Identify areas needing heavy pruning\n"
            "□ Mark plants with airflow issues\n"
            "□ Note any problem areas\n"
            "□ Plan Day 42 defoliation strategy\n\n"
            "AIRFLOW CHECK:\n"
            "□ Document current airflow issues\n"
            "□ Check humidity in dense spots\n"
            "□ Identify mold risk areas\n\n"
            "TOOL PREPARATION:\n"
            "□ Clean and sharpen scissors\n"
            "□ Prepare sanitizer (70% isopropyl)\n"
            "□ Have trash bags ready\n"
            "□ Schedule adequate time for Day 42\n\n"
            "CURRENT TARGETS:\n"
            "• EC Input: 3.0 | Dryback: 30-40%\n\n"
            "[Source: Athena Handbook, Crop Steering]"
        ),
        "category": "maintenance",
        "phase": PHASE_BULK,
        "priority": "medium",
        "duration_hours": 1,
    },
    42: {
        "title": "✂️ DAY 42 MAJOR DEFOLIATION - Ensure Airflow",
        "description": (
            "DAY 42 - CRITICAL MAINTENANCE PRUNE\n\n"
            "🚨 MAJOR DEFOLIATION DAY 🚨\n\n"
            "DEFOLIATION PROTOCOL:\n"
            "• Remove 20-30% of remaining fan leaves\n"
            "• Focus on leaves blocking airflow\n"
            "• Remove leaves touching or shading buds\n"
            "• Clear interior canopy completely\n"
            "• Remove any remaining larf/popcorn buds\n\n"
            "PRIORITY AREAS:\n"
            "1. Interior canopy (most critical)\n"
            "2. Lower branches with small buds\n"
            "3. Any overlapping/touching leaves\n"
            "4. Yellowing or damaged leaves\n\n"
            "AIRFLOW GOALS:\n"
            "• Air should flow freely through canopy\n"
            "• No dense pockets where humidity builds\n"
            "• Light penetration to lower buds\n"
            "• Reduce bud rot risk significantly\n\n"
            "⚠️ DO NOT REMOVE:\n"
            "• Healthy sugar leaves on buds\n"
            "• Leaves providing energy to top colas\n"
            "• More than 30% of total leaf mass\n\n"
            "POST-PRUNE:\n"
            "• Lower humidity 5% for 24-48 hours\n"
            "• Increase airflow temporarily\n"
            "• Monitor for stress response\n\n"
            "ESTIMATED TIME: 3-5 min per plant\n\n"
            "[Source: Athena Handbook, Defoliation Protocol]"
        ),
        "category": "defoliation",
        "phase": PHASE_BULK,
        "priority": "critical",
        "duration_hours": 4,
    },
    43: {
        "title": "🔧 Post-Defoliation Check (Day 43)",
        "description": (
            "BULK PHASE - POST-DEFOLIATION RECOVERY\n\n"
            "RECOVERY CHECK:\n"
            "□ Plants recovering from Day 42 prune\n"
            "□ No signs of excessive stress\n"
            "□ Leaves not drooping excessively\n"
            "□ New growth appearing healthy\n\n"
            "AIRFLOW VERIFICATION:\n"
            "□ Confirm improved air circulation\n"
            "□ Check humidity levels (should be lower)\n"
            "□ Verify no moisture on leaves/buds\n\n"
            "ENVIRONMENTAL ADJUSTMENTS:\n"
            "□ Can return humidity to normal if stable\n"
            "□ Maintain good airflow\n"
            "□ Watch for any stress signs\n\n"
            "CURRENT TARGETS:\n"
            "• EC Input: 3.0 | Dryback: 30-40%\n"
            "• VPD: 1.2-1.4 kPa\n\n"
            "[Source: Athena Handbook, Crop Steering]"
        ),
        "category": "maintenance",
        "phase": PHASE_BULK,
        "priority": "medium",
        "duration_hours": 1,
    },
    46: {
        "title": "🔧 Maintenance Check - Airflow & Canopy (Day 46)",
        "description": (
            "BULK PHASE - MAINTENANCE DAY (Every 3 Days)\n\n"
            "CANOPY MANAGEMENT:\n"
            "□ Light touch-up pruning only\n"
            "□ Remove any new growth blocking airflow\n"
            "□ Check for leaves touching buds\n\n"
            "AIRFLOW CHECK:\n"
            "□ Maintain good circulation\n"
            "□ Monitor humidity in canopy\n"
            "□ Check for any wet spots\n\n"
            "FLOWER PROGRESS:\n"
            "□ Buds should be dense and heavy\n"
            "□ 30-50% of pistils turning orange\n"
            "□ Strong terpene production (smell)\n"
            "□ Trichomes mostly cloudy\n\n"
            "CURRENT TARGETS:\n"
            "• EC Input: 3.0 | Dryback: 30-40%\n"
            "• VPD: 1.2-1.4 kPa\n\n"
            "[Source: Athena Handbook, Crop Steering]"
        ),
        "category": "maintenance",
        "phase": PHASE_BULK,
        "priority": "medium",
        "duration_hours": 1,
    },
    49: {
        "title": "🔧 Maintenance Check - Week 7 (Day 49)",
        "description": (
            "BULK PHASE - MAINTENANCE DAY (Week 7)\n\n"
            "CANOPY MANAGEMENT:\n"
            "□ Minimal pruning - plants need leaves\n"
            "□ Only remove dead/dying material\n"
            "□ Support heavy branches\n\n"
            "AIRFLOW CHECK:\n"
            "□ Critical as buds get denser\n"
            "□ Watch for bud rot signs\n"
            "□ Ensure no stagnant air\n\n"
            "WEEK 7 ASSESSMENT:\n"
            "□ Buds at 70-80% final size\n"
            "□ Trichomes cloudy with some amber\n"
            "□ Pistils 50-70% orange\n"
            "□ Prepare for Finish phase transition\n\n"
            "UPCOMING:\n"
            "• Week 8 = Finish Phase begins\n"
            "• Nutrient change to Athena Fade\n"
            "• EC reduction to 1.5\n\n"
            "[Source: Athena Handbook, Crop Steering]"
        ),
        "category": "maintenance",
        "phase": PHASE_BULK,
        "priority": "medium",
        "duration_hours": 1,
    },
    52: {
        "title": "🔧 Maintenance Check - Pre-Finish Prep (Day 52)",
        "description": (
            "BULK PHASE - FINAL MAINTENANCE (Every 3 Days)\n\n"
            "⚠️ FINISH PHASE IN 4 DAYS - PREPARE!\n\n"
            "CANOPY MANAGEMENT:\n"
            "□ Final light pruning if needed\n"
            "□ Remove any remaining problem leaves\n"
            "□ Ensure good airflow for finish\n\n"
            "AIRFLOW CHECK:\n"
            "□ Critical for preventing late bud rot\n"
            "□ Lower humidity if possible\n"
            "□ Maximum air circulation\n\n"
            "FINISH PHASE PREPARATION:\n"
            "□ Order Athena Fade if not on hand\n"
            "□ Plan nutrient transition\n"
            "□ Prepare for EC reduction\n"
            "□ Consider final flush timing\n\n"
            "CURRENT TARGETS:\n"
            "• EC Input: 3.0 | Dryback: 30-40%\n\n"
            "[Source: Athena Handbook, Crop Steering]"
        ),
        "category": "maintenance",
        "phase": PHASE_BULK,
        "priority": "medium",
        "duration_hours": 1,
    },
    55: {
        "title": "🔧 Maintenance Check - Last Bulk Day (Day 55)",
        "description": (
            "BULK PHASE - FINAL DAY\n\n"
            "🔔 TOMORROW: FINISH PHASE BEGINS!\n\n"
            "FINAL BULK PHASE TASKS:\n"
            "□ Last maintenance pruning\n"
            "□ Document current plant status\n"
            "□ Take photos for records\n"
            "□ Prepare Athena Fade nutrients\n\n"
            "AIRFLOW CHECK:\n"
            "□ Ensure excellent circulation\n"
            "□ Lower humidity to 45-50%\n"
            "□ Buds are dense - rot risk highest\n\n"
            "TRANSITION PREP:\n"
            "□ Mix Athena Fade solution\n"
            "□ Target EC: 1.5 (down from 3.0)\n"
            "□ Prepare for reduced irrigation\n"
            "□ Plan harvest timeline\n\n"
            "FLOWER STATUS:\n"
            "• Buds at 85-95% final size\n"
            "• Heavy trichome coverage\n"
            "• Strong aroma\n\n"
            "[Source: Athena Handbook, Crop Steering]"
        ),
        "category": "maintenance",
        "phase": PHASE_BULK,
        "priority": "high",
        "duration_hours": 1,
    },
    # =========================================================================
    # PHASE 3: FINISH (Weeks 8-10+, Days 56-84+)
    # =========================================================================
    56: {
        "title": "🍂 BEGIN FINISH PHASE - Switch to Athena Fade",
        "description": (
            "DAY 56 - FINISH PHASE BEGINS\n\n"
            "🚨 MAJOR NUTRIENT CHANGE 🚨\n\n"
            "NUTRIENT TRANSITION:\n"
            "• Switch from Pro Line to Athena Fade\n"
            "• Athena Fade = ZERO NITROGEN formula\n"
            "• Promotes proper senescence and ripening\n"
            "• Improves final flower quality\n\n"
            "NEW NUTRIENT MIX (per 100gal):\n"
            "• Athena Fade: Follow label rates\n"
            "• Target EC: 1.5 (reduced from 3.0)\n"
            "• Target pH: 5.8-6.0\n\n"
            "IRRIGATION CHANGES:\n"
            "• Reduce irrigation frequency\n"
            "• Target 40-50% dryback\n"
            "• Generative steering for ripening\n\n"
            "ENVIRONMENTAL TARGETS:\n"
            "• Day temp: 75-78°F (24-26°C)\n"
            "• Night temp: 62-68°F (17-20°C)\n"
            "• Humidity: 40-50% RH (lower!)\n"
            "• VPD: 1.4-1.6 kPa\n\n"
            "EXPECTED CHANGES:\n"
            "• Fan leaves will yellow (normal!)\n"
            "• Plant using stored nutrients\n"
            "• Trichomes maturing faster\n\n"
            "[Source: Athena Handbook, Fade Protocol]"
        ),
        "category": "nutrients",
        "phase": PHASE_FINISH,
        "priority": "critical",
        "duration_hours": 2,
    },
    59: {
        "title": "🔧 Finish Phase Check - Day 59",
        "description": (
            "FINISH PHASE - MAINTENANCE (Every 3 Days)\n\n"
            "FADE PROGRESS CHECK:\n"
            "□ Fan leaves beginning to yellow (good!)\n"
            "□ Plants responding to reduced nitrogen\n"
            "□ No signs of nutrient lockout\n"
            "□ Buds continuing to swell\n\n"
            "AIRFLOW CHECK:\n"
            "□ CRITICAL - bud rot risk highest now\n"
            "□ Humidity must stay below 50%\n"
            "□ Maximum air circulation\n"
            "□ Check dense buds for rot daily\n\n"
            "TRICHOME CHECK:\n"
            "□ Use loupe/microscope\n"
            "□ Target: mostly cloudy, 10-20% amber\n"
            "□ Clear = too early\n"
            "□ All amber = past peak\n\n"
            "CURRENT TARGETS:\n"
            "• EC Input: 1.5 | Dryback: 40-50%\n"
            "• VPD: 1.4-1.6 kPa | RH: 40-50%\n\n"
            "[Source: Athena Handbook, Fade Protocol]"
        ),
        "category": "maintenance",
        "phase": PHASE_FINISH,
        "priority": "medium",
        "duration_hours": 1,
    },
    62: {
        "title": "🔧 Finish Phase Check - Day 62",
        "description": (
            "FINISH PHASE - MAINTENANCE (Every 3 Days)\n\n"
            "FADE PROGRESS:\n"
            "□ Yellowing spreading through fan leaves\n"
            "□ Lower leaves may be dropping\n"
            "□ This is NORMAL and desired\n"
            "□ Sugar leaves staying green\n\n"
            "AIRFLOW & ENVIRONMENT:\n"
            "□ Maintain low humidity (40-50%)\n"
            "□ Good air movement essential\n"
            "□ Check for bud rot daily\n"
            "□ Remove any affected material immediately\n\n"
            "HARVEST PLANNING:\n"
            "□ Estimate 2-3 weeks to harvest\n"
            "□ Prepare drying space\n"
            "□ Check trichomes every 2-3 days\n"
            "□ Order harvest supplies if needed\n\n"
            "CURRENT TARGETS:\n"
            "• EC Input: 1.5 | Dryback: 40-50%\n\n"
            "[Source: Athena Handbook, Fade Protocol]"
        ),
        "category": "maintenance",
        "phase": PHASE_FINISH,
        "priority": "medium",
        "duration_hours": 1,
    },
    65: {
        "title": "🔧 Finish Phase Check - Day 65",
        "description": (
            "FINISH PHASE - MAINTENANCE (Every 3 Days)\n\n"
            "PLANT STATUS:\n"
            "□ Significant leaf yellowing\n"
            "□ Buds at near-final size\n"
            "□ Trichomes maturing\n"
            "□ Aroma at peak intensity\n\n"
            "AIRFLOW CHECK:\n"
            "□ Continue maximum circulation\n"
            "□ Humidity control critical\n"
            "□ Daily bud rot inspection\n\n"
            "TRICHOME ASSESSMENT:\n"
            "□ Check multiple bud sites\n"
            "□ Look at calyxes, not sugar leaves\n"
            "□ Target: 70-80% cloudy, 10-20% amber\n\n"
            "CURRENT TARGETS:\n"
            "• EC Input: 1.5 | Dryback: 40-50%\n"
            "• VPD: 1.4-1.6 kPa\n\n"
            "[Source: Athena Handbook, Fade Protocol]"
        ),
        "category": "maintenance",
        "phase": PHASE_FINISH,
        "priority": "medium",
        "duration_hours": 1,
    },
    68: {
        "title": "🔧 Finish Phase Check - Day 68",
        "description": (
            "FINISH PHASE - MAINTENANCE (Every 3 Days)\n\n"
            "LATE FLOWER STATUS:\n"
            "□ Heavy yellowing/leaf drop normal\n"
            "□ Buds dense and frosty\n"
            "□ Pistils 70-90% orange/brown\n"
            "□ Trichomes mostly cloudy\n\n"
            "AIRFLOW CHECK:\n"
            "□ Maintain vigilance for bud rot\n"
            "□ Keep humidity at 40-50%\n"
            "□ Air movement through all buds\n\n"
            "HARVEST PREP:\n"
            "□ ~1-2 weeks to harvest window\n"
            "□ Prepare drying room/tent\n"
            "□ Clean trimming tools\n"
            "□ Plan harvest schedule\n\n"
            "CURRENT TARGETS:\n"
            "• EC Input: 1.5 | Dryback: 40-50%\n\n"
            "[Source: Athena Handbook, Fade Protocol]"
        ),
        "category": "maintenance",
        "phase": PHASE_FINISH,
        "priority": "medium",
        "duration_hours": 1,
    },
    71: {
        "title": "🔧 Finish Phase Check - Day 71",
        "description": (
            "FINISH PHASE - MAINTENANCE (Every 3 Days)\n\n"
            "PRE-HARVEST STATUS:\n"
            "□ Most fan leaves yellow/dropped\n"
            "□ Buds at final size\n"
            "□ Checking trichomes daily\n"
            "□ Harvest window approaching\n\n"
            "AIRFLOW CHECK:\n"
            "□ Final stretch - stay vigilant\n"
            "□ Bud rot can strike at any time\n"
            "□ Keep environment stable\n\n"
            "TRICHOME STATUS:\n"
            "□ Should be 80%+ cloudy\n"
            "□ 10-30% amber depending on preference\n"
            "□ More amber = more sedative effect\n"
            "□ Less amber = more energetic effect\n\n"
            "CURRENT TARGETS:\n"
            "• EC Input: 1.5 | Dryback: 40-50%\n\n"
            "[Source: Athena Handbook, Fade Protocol]"
        ),
        "category": "maintenance",
        "phase": PHASE_FINISH,
        "priority": "medium",
        "duration_hours": 1,
    },
    74: {
        "title": "🔧 Finish Phase Check - Day 74 (Pre-Harvest)",
        "description": (
            "FINISH PHASE - MAINTENANCE (Every 3 Days)\n\n"
            "⚠️ HARVEST WINDOW IN ~3 DAYS!\n\n"
            "FINAL CHECKS:\n"
            "□ Trichomes at target maturity?\n"
            "□ All preparations complete?\n"
            "□ Drying space ready?\n"
            "□ Schedule cleared for harvest?\n\n"
            "AIRFLOW CHECK:\n"
            "□ Maintain until harvest\n"
            "□ Don't let guard down now\n"
            "□ One more inspection\n\n"
            "HARVEST DECISION:\n"
            "□ If trichomes ready - harvest Day 77\n"
            "□ If need more time - continue checking\n"
            "□ Don't rush - quality over speed\n\n"
            "CURRENT TARGETS:\n"
            "• EC Input: 1.5 | Dryback: 40-50%\n\n"
            "[Source: Athena Handbook, Fade Protocol]"
        ),
        "category": "maintenance",
        "phase": PHASE_FINISH,
        "priority": "high",
        "duration_hours": 1,
    },
    77: {
        "title": "🌿 HARVEST WINDOW OPENS - Day 77",
        "description": (
            "DAY 77 - HARVEST WINDOW BEGINS\n\n"
            "🎉 CONGRATULATIONS - HARVEST TIME! 🎉\n\n"
            "HARVEST DECISION:\n"
            "• Check trichomes one final time\n"
            "• 80-90% cloudy + 10-20% amber = READY\n"
            "• Can harvest now or wait up to Day 84\n\n"
            "IF HARVESTING TODAY:\n"
            "1. Stop all irrigation 24-48 hours before\n"
            "2. Consider 24-48 hour dark period (optional)\n"
            "3. Cut plants at base or branch by branch\n"
            "4. Wet trim or dry trim based on preference\n"
            "5. Hang in drying room immediately\n\n"
            "DRYING CONDITIONS:\n"
            "• Temperature: 60-70°F (15-21°C)\n"
            "• Humidity: 55-65% RH\n"
            "• Air circulation (gentle, not direct)\n"
            "• Complete darkness\n"
            "• 7-14 days typical dry time\n\n"
            "IF WAITING:\n"
            "• Continue monitoring trichomes\n"
            "• Watch for over-ripening\n"
            "• Maintain environment\n"
            "• Harvest by Day 84 latest\n\n"
            "[Source: Athena Handbook, Harvest Protocol]"
        ),
        "category": "harvest",
        "phase": PHASE_FINISH,
        "priority": "critical",
        "duration_hours": 8,
    },
    80: {
        "title": "🔧 Harvest Window Check - Day 80",
        "description": (
            "HARVEST WINDOW - DAY 80\n\n"
            "IF NOT YET HARVESTED:\n"
            "□ Check trichomes - more amber now\n"
            "□ Assess if ready or need more time\n"
            "□ Maximum 4 more days recommended\n\n"
            "TRICHOME STATUS:\n"
            "□ Should be 80%+ cloudy\n"
            "□ 20-30% amber likely\n"
            "□ More amber = more body effect\n\n"
            "ENVIRONMENT:\n"
            "□ Maintain low humidity\n"
            "□ Continue airflow\n"
            "□ Watch for any issues\n\n"
            "HARVEST PREP:\n"
            "□ Final preparations\n"
            "□ Drying room ready\n"
            "□ Tools sanitized\n\n"
            "[Source: Athena Handbook, Harvest Protocol]"
        ),
        "category": "harvest",
        "phase": PHASE_FINISH,
        "priority": "high",
        "duration_hours": 1,
    },
    83: {
        "title": "🔧 Final Harvest Check - Day 83",
        "description": (
            "HARVEST WINDOW - DAY 83\n\n"
            "⚠️ HARVEST TOMORROW RECOMMENDED!\n\n"
            "IF NOT YET HARVESTED:\n"
            "□ Trichomes likely 30%+ amber\n"
            "□ Risk of over-ripening increases\n"
            "□ Plan to harvest Day 84\n\n"
            "FINAL ASSESSMENT:\n"
            "□ Quality will decline after Day 84\n"
            "□ THC degrading to CBN\n"
            "□ More sedative effect\n\n"
            "TOMORROW'S PLAN:\n"
            "□ Stop irrigation now\n"
            "□ Optional: 24hr dark period\n"
            "□ Harvest first thing Day 84\n\n"
            "[Source: Athena Handbook, Harvest Protocol]"
        ),
        "category": "harvest",
        "phase": PHASE_FINISH,
        "priority": "critical",
        "duration_hours": 1,
    },
    84: {
        "title": "🏁 END OF CYCLE - Harvest & Sanitize Lines",
        "description": (
            "DAY 84 - CYCLE COMPLETE\n\n"
            "🎉 HARVEST DAY / END OF CYCLE 🎉\n\n"
            "HARVEST (if not already done):\n"
            "• Cut all remaining plants\n"
            "• Process for drying\n"
            "• Clean grow space\n\n"
            "POST-HARVEST SANITATION:\n"
            "1. Remove all plant material\n"
            "2. Clean all surfaces with H2O2 or bleach\n"
            "3. Sanitize irrigation lines:\n"
            "   • Flush with Athena Renew\n"
            "   • Or use Athena Reset\n"
            "   • Run through entire system\n"
            "   • Let sit 15-30 minutes\n"
            "   • Flush with clean water\n\n"
            "LINE CLEANING PROTOCOL:\n"
            "• Athena Renew: 2-4 oz/gal\n"
            "• Run through all drippers/emitters\n"
            "• Clears salt buildup and biofilm\n"
            "• Essential for next cycle success\n\n"
            "ROOM RESET:\n"
            "□ Clean floors and walls\n"
            "□ Sanitize all equipment\n"
            "□ Check/replace filters\n"
            "□ Inspect and repair any issues\n"
            "□ Prepare for next cycle\n\n"
            "[Source: Athena Handbook, Clean Line Protocol]"
        ),
        "category": "maintenance",
        "phase": PHASE_FINISH,
        "priority": "critical",
        "duration_hours": 8,
    },
}
