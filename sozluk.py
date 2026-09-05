# sozluk.py - Kapsamlı Tenis Hakemlik ve Kural Sözlüğü

TENNIS_SOZLugu = {
    # Ekipmanlar ve Kort
    "raket": ["racket", "racquet", "string", "dampener", "vibration dampener", "broken racket"],
    "top": ["ball", "balls", "defective ball", "soft ball"],
    "top değişimi": ["ball change", "change of balls", "new balls"],
    "kort": ["court", "net", "post", "singles stick", "baseline", "sideline", "center mark"],
    "kıyafet": ["attire", "clothing", "shoes", "commercial identification", "logos", "white clothing", "dress code", "hat", "sweatband"],
    
    # Maç İçi Durumlar ve Molalar
    "mola": ["break", "rest", "toilet break", "medical time-out", "mto", "rest period", "changeover", "set break"],
    "hava durumu": ["weather", "suspension", "interruption", "heat rule", "extreme weather", "inclement weather", "rain", "darkness", "postponement"],
    "tuvalet": ["toilet break", "restroom", "change of attire", "bathroom"],
    "sağlık": ["medical", "injury", "treatment", "bleed time", "evaluation", "trainer", "doctor", "cramp", "muscle", "vomiting"],
    "gecikme": ["time violation", "delay", "continuous play", "warm-up", "starting time", "punctuality", "late arrival", "no show"],
    "ısınma": ["warm-up", "practice", "hitting session", "pre-match"],
    "engelleme": ["hindrance", "out call", "let", "disturbance", "noise", "talking"],
    
    # Oyun Kuralları ve Skor
    "servis": ["serve", "service", "let", "fault", "service fault", "second serve", "foot fault", "receiver", "server"],
    "hata": ["fault", "foot fault", "double bounce", "not up", "foul strike", "touch", "invasion"],
    "uzatma": ["tie-break", "tiebreak", "match tie-break", "set tie-break", "super tie-break", "deciding set"],
    "avantaj": ["advantage", "ad", "deuce", "no-ad", "deciding point"],
    
    # Ceza ve İhlaller (Code of Conduct)
    "diskalifiye": ["default", "disqualification", "expulsion"],
    "kod ihlali": ["code violation", "penalty", "warnings", "point penalty", "game penalty", "unsportsmanlike", "conduct"],
    "hakaret": ["verbal abuse", "obscenity", "profanity", "swearing"],
    "suistimal": ["abuse", "ball abuse", "racket abuse", "equipment abuse", "physical abuse"],
    "koçluk": ["coaching", "communication", "instruction", "signals"],
    "seyirci": ["spectator", "crowd", "interruption", "noise", "behavior", "interference"],
    
    # Yetkililer ve İtirazlar
    "hakem": ["umpire", "referee", "supervisor", "chair umpire", "roving umpire", "chief", "line umpire", "off-court"],
    "itiraz": ["appeal", "challenge", "review", "hawk-eye", "electronic review", "question of law", "question of fact", "overrule"],
    
    # Turnuva Yapısı ve Kurallar
    "çekilme": ["retirement", "withdrawal", "walkover", "w/o", "ret", "scratch"],
    "hükmen": ["walkover", "default", "w/o", "bye"],
    "kura": ["draw", "seeding", "qualifying", "lucky loser", "alternate", "withdrawal", "wild card", "main draw"],
    "katılım": ["sign-in", "entry", "withdrawal", "acceptance list", "deadline", "entry fee", "registration"],
    "format": ["round robin", "feed-in consolation", "knockout", "compass draw", "short sets"]
}
