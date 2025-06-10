# utils/constants.py

# Gamificación
MAX_DAILY_INTERACTION_POINTS = 20 # Límite de puntos por interacciones al día

# Puntos por permanencia
POINTS_PER_WEEK = 10
WEEKLY_STREAK_BONUS = 1 # Puntos extra por cada semana de racha (hasta MAX_WEEKLY_STREAK_BONUS)
MAX_WEEKLY_STREAK_BONUS = 5 # +15 puntos en la 5ta semana consecutiva (10 + 5)
POINTS_PER_MONTH = 50

# Hitos de permanencia
MILESTONE_6_MONTHS_POINTS = 100
MILESTONE_1_YEAR_POINTS = 200

# IDs de insignias (para referencia en el código)
BADGE_VETERAN_INTIMO = "veterano_intimo"
BADGE_BIG_SPENDER_VIP = "big_spender_vip"
BADGE_FAN_LEAL_APASIONADO = "fan_leal_apasionado"
BADGE_RACHA_ARDIENTE = "racha_ardiente"
BADGE_PRIMER_CANJE = "primer_canje"
BADGE_CAZADOR_TESOROS = "cazador_tesoros"

# IDs de administradores (cargados desde settings.py, pero útiles para referencia)
ADMIN_IDS: list[int] = [] # Se llenará en main.py desde settings