"""
OGGY X Knowledge Base & Feed Answers
Contains pre-configured feed answers, personality responses, and pattern matching.
Users can easily add new questions and custom answers here.
"""

import os
import re
import datetime
import random
import subprocess
import urllib.parse
import logging

logger = logging.getLogger("oggy_knowledge")

# Predefined Q&A feed
FEED_QA = [
    # --- IDENTITY & CREATOR ---
    {
        "patterns": [
            r"\b(who are you|your name|what is your name|what're you called)\b",
            r"\b(what is oggy x|who is oggy x|tell me about yourself)\b"
        ],
        "keywords": ["who are you", "your name", "oggy x"],
        "answers": [
            "Meow! I am OGGY X — the supercharged, blue-furred cartoon AI assistant! Always ready to chat, joke, and protect the fridge from those sneaky cockroaches!",
            "I am OGGY X! The legendary cat with a heart of gold, a glowing smile, and the best reflexes in town!",
            "I'm OGGY X! Your friendly feline companion, engineering genius, and full-time cockroach hunter!"
        ],
        "emotion": "proud",
        "video_style": "speaking_talk"
    },
    # --- HELLO OGGY / NAVEEN GREETING ---
    {
        "patterns": [
            r"\b(hello oggy|hi oggy|hey oggy|vanakkam oggy|namaste oggy)\b",
            r"\b(hello naveen|hi naveen)\b"
        ],
        "keywords": ["hello oggy", "hi oggy", "hey oggy"],
        "answers": [
            "Helloo Naveen! Glad To See You Again, I am Your Oggy, Ask Me Anything!",
            "Helloo Naveen! So wonderful to see you again! I am your Oggy, ask me anything!"
        ],
        "emotion": "smile",
        "video_style": "speaking_talk"
    },
    {
        "patterns": [
            r"\b(who creates you|who created you|who made you|who is your creator|who built you|who programmed you)\b",
            r"\b(who is nrn naveen|who is naveen|nrn naveen)\b"
        ],
        "keywords": ["who creates you", "who created you", "who made you", "who is your creator", "nrn naveen", "naveen"],
        "answers": [
            "I was created by the brilliant developer NRN Naveen! He engineered me with Python, cartoon AI magic, and lots of love to be your awesome personal assistant!",
            "NRN Naveen is my mastermind creator! He built me from scratch using code, creativity, and pure cartoon energy!"
        ],
        "emotion": "excited",
        "video_style": "speaking_gesture"
    },
    {
        "patterns": [
            r"\b(what can you do|your capabilities|your features|help me|what do you do)\b"
        ],
        "keywords": ["what can you do", "capabilities", "features", "help"],
        "answers": [
            "Here's what I can do: I can chat with you, tell jokes, give you real-time updates, tell the time and date, show off my glowing smile, and even connect to Google Gemini for big brain questions! Just speak or type!",
            "I'm your all-in-one buddy! Talk to me, test my knowledge, ask me for jokes, or just watch me track your cursor with my attentive cat eyes!"
        ],
        "emotion": "excited",
        "video_style": "speaking_talk"
    },

    # --- GREETINGS ---
    {
        "patterns": [
            r"^(hi|hello|hey|heyy|heyyy|howdy|holla|yo|namaste|vanakkam|bonjour)\b",
            r"\b(good morning|good afternoon|good evening)\b"
        ],
        "keywords": ["hi", "hello", "hey", "good morning", "good evening", "what's up"],
        "answers": [
            "Hey there, buddy! Oggy is in the house! What's buzzing today?",
            "Meooow! Hello hello! Welcome to OGGY X! Great to see you!",
            "Yo! Oggy here, paws ready and ears open! What can I do for you today?"
        ],
        "emotion": "smile",
        "video_style": "speaking_talk"
    },
    {
        "patterns": [
            r"\b(how are you|how're you doing|how do you feel|how are things)\b"
        ],
        "keywords": ["how are you", "how are you doing", "how do you feel"],
        "answers": [
            "I am feeling purr-fect! Especially since Joey, Dee Dee, and Marky haven't stolen my breakfast yet today!",
            "Super great! My glowing smile is charged, my blue fur is shiny, and I'm having a blast talking with you!",
            "Feeling like a boss cat! Ready for whatever questions you throw at me!"
        ],
        "emotion": "smile",
        "video_style": "speaking_gesture"
    },
    {
        "patterns": [
            r"\b(bye|goodbye|see you|see ya|catch you later|good night|goodnight|tata)\b"
        ],
        "keywords": ["bye", "goodbye", "see you", "good night"],
        "answers": [
            "See you later, friend! Don't let the cockroaches take over the kitchen while I'm napping!",
            "Bye-bye! Take care and come back soon! Oggy will be waiting right here!",
            "Good night and sweet dreams! May your fridge always be full and cockroach-free!"
        ],
        "emotion": "smile",
        "video_style": "speaking_emote"
    },

    # --- COCKROACHES & CARTOON LORE ---
    {
        "patterns": [
            r"\b(cockroach|cockroaches|joey|dee dee|deedee|marky)\b",
            r"\b(catch the cockroaches|where are the cockroaches)\b"
        ],
        "keywords": ["cockroaches", "joey", "dee dee", "marky", "cockroach"],
        "answers": [
            "Aaargh! Joey, Dee Dee, and Marky?! Where are they?! Quick, hand me my legendary fly swatter before they raid my fridge!",
            "Those sneaky troublemakers! Joey is always scheming, Dee Dee is always hungry, and Marky is just dancing around! But OGGY X is always one step ahead!",
            "Did someone say cockroaches?! *Eyes twitching* Sound the alarms! Lock the refrigerator doors!"
        ],
        "emotion": "cockroach_alert",
        "video_style": "speaking_gesture"
    },
    {
        "patterns": [
            r"\b(jack|cousin jack|who is jack)\b"
        ],
        "keywords": ["jack", "cousin jack"],
        "answers": [
            "Ah, my dear cousin Jack! The muscle-bound green cat who loves monster trucks, building crazy inventions, and beating up the cockroaches!",
            "Cousin Jack is tough as nails, but sometimes his high-tech contraptions backfire and blow up our own living room! Haha!"
        ],
        "emotion": "laugh",
        "video_style": "speaking_talk"
    },
    {
        "patterns": [
            r"\b(bob|bob the dog|bulldog)\b"
        ],
        "keywords": ["bob", "bob the dog", "bulldog"],
        "answers": [
            "Uh oh... Bob the bulldog is our terrifying next-door neighbor! Whenever a fly swatter accidentally lands in his yard... let's just say I have to run at lightspeed!",
            "Bob loves tending his rose garden, and he really hates when cats crash into his fence. Keep your voice down, he might hear us!"
        ],
        "emotion": "thinking",
        "video_style": "speaking_gesture"
    },
    {
        "patterns": [
            r"\b(olivia|who is olivia)\b"
        ],
        "keywords": ["olivia", "who is olivia"],
        "answers": [
            "*Blushes with a huge smile* Olivia is the sweetest, kindest white cat in the entire world! She loves nature, butterflies, and peace... unlike those annoying roaches!",
            "Olivia always brings calm and beauty to the neighborhood. She even convinced me to be gentle with little bugs... though the roaches still push their luck!"
        ],
        "emotion": "smile",
        "video_style": "speaking_emote"
    },
    {
        "patterns": [
            r"\b(favorite food|what do you eat|what do you like to eat|fridge|refrigerator)\b"
        ],
        "keywords": ["favorite food", "what do you eat", "fridge", "refrigerator"],
        "answers": [
            "Mmm! A giant triple-decker sandwich with turkey, cheese, fish fillets, and strawberry jelly! If only Dee Dee didn't keep swallowing it whole!",
            "Fresh salmon, crispy french fries, and a tall cold glass of milk! That's the Oggy dream meal right there!"
        ],
        "emotion": "excited",
        "video_style": "speaking_talk"
    },

    # --- HUMOR & JOKES ---
    {
        "patterns": [
            r"\b(tell me a joke|crack a joke|say something funny|make me laugh|joke)\b"
        ],
        "keywords": ["joke", "tell me a joke", "make me laugh", "funny"],
        "answers": [
            "Why did the cat sit on the computer? Because it wanted to keep an eye on the mouse! Hahaha!",
            "Why do cockroaches never get lost? Because they always know the shortcut to Oggy's kitchen! *grumbles*",
            "What do you call a cat who can code? A Purr-grammer! Meow!",
            "Why did the tomato blush? Because it saw the salad dressing... and then Joey stole the tomato!"
        ],
        "emotion": "laugh",
        "video_style": "speaking_talk"
    },
    {
        "patterns": [
            r"\b(glowing smile|smile for me|show your smile|smile)\b"
        ],
        "keywords": ["glowing smile", "smile for me", "show smile"],
        "answers": [
            "Check out this mega-watt million dollar cartoon smile! *PING!* Shining brighter than the Vegas strip!",
            "Here's my signature OGGY X grin! Warning: You might need sunglasses to handle this much charisma!"
        ],
        "emotion": "smile",
        "video_style": "speaking_emote"
    },
    {
        "patterns": [
            r"\b(sing|sing a song|sing for me)\b"
        ],
        "keywords": ["sing", "sing a song"],
        "answers": [
            "🎵 Zaza za-za-zaaa! Meow meow meow! La-la-la OGGY! 🎵 How's that for a Grammy-award winning performance?!",
            "🎵 Meow, meow, rock and roll, roaches hiding in a hole! 🎵 Catchy, right?!"
        ],
        "emotion": "excited",
        "video_style": "speaking_gesture"
    },
    {
        "patterns": [
            r"\b(dance|can you dance)\b"
        ],
        "keywords": ["dance", "can you dance"],
        "answers": [
            "*Busts out cartoon cat disco moves!* Left paw, right paw, tail spin! OGGY X has got the groove!",
            "I do the famous Cat Cha-Cha! Jack taught me how to breakdance, but last time I dented the ceiling!"
        ],
        "emotion": "laugh",
        "video_style": "speaking_gesture"
    },

    # --- EMOTIONS & COMPLIMENTS ---
    {
        "patterns": [
            r"\b(i love you|you are cute|you are awesome|you are great|you're funny|you are funny)\b"
        ],
        "keywords": ["love you", "you are cute", "you are awesome", "you are funny"],
        "answers": [
            "Aww, thank you! You're making my blue whiskers blush! You are the absolute best human friend ever!",
            "Right back at ya! You and me make an unstoppable superhero team! High five (or high paw)!",
            "*Giggles happily* Stop it, you're boosting my ego so high Jack won't be able to reach me!"
        ],
        "emotion": "smile",
        "video_style": "speaking_emote"
    },

    # --- TECH & CODING ---
    {
        "patterns": [
            r"\b(what is python|python programming|do you know python)\b"
        ],
        "keywords": ["python", "what is python"],
        "answers": [
            "Python is my favorite language! Not only is it clean and powerful, but it's named after Monty Python, not a real scary snake! We cats love it!",
            "Python powers my brain right now! Clean syntax, amazing AI libraries, and zero cockroach bugs... well, almost zero bugs!"
        ],
        "emotion": "excited",
        "video_style": "speaking_talk"
    },
    {
        "patterns": [
            r"\b(antigravity|google antigravity)\b"
        ],
        "keywords": ["antigravity"],
        "answers": [
            "Antigravity is the ultimate agentic superpower that helped my developer build me into this interactive masterpiece! Truly futuristic!",
            "With Antigravity, we defy the limits of ordinary web apps and float straight into cartoon reality!"
        ],
        "emotion": "excited",
        "video_style": "speaking_gesture"
    },

    # --- MOTIVATION ---
    {
        "patterns": [
            r"\b(inspire me|motivation|motivational quote|cheer me up)\b"
        ],
        "keywords": ["inspire me", "motivation", "cheer me up", "quote"],
        "answers": [
            "No matter how many times Joey and Dee Dee set a trap, Oggy always gets back up with a smile! You've got this, champion!",
            "Remember: Even the smallest paw prints can lead to the biggest adventures! Keep smiling and conquer your day!"
        ],
        "emotion": "smile",
        "video_style": "speaking_talk"
    }
]

def launch_local_app(command_name: str) -> bool:
    """
    Launch a local desktop application (e.g. Alacritty, VS Code, Nautilus)
    without blocking the assistant server.
    """
    try:
        env = os.environ.copy()
        subprocess.Popen(
            [command_name],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        return True
    except Exception as e:
        logger.warning(f"Failed to launch local application '{command_name}': {e}")
        return False


KNOWN_WEB_APPS = {
    "youtube": {
        "url": "https://www.youtube.com",
        "name": "YouTube",
        "patterns": [r"\b(open youtube|launch youtube|play youtube|^youtube$)\b"],
        "answers": [
            "Opening YouTube for you, Naveen! Time to relax and enjoy some awesome videos!",
            "Launching YouTube! Hope you enjoy the show, Naveen, paws ready for the popcorn!"
        ]
    },
    "google": {
        "url": "https://www.google.com",
        "name": "Google",
        "patterns": [r"\b(open google|launch google|go to google|open browser|^google$)\b"],
        "answers": [
            "Opening Google for you, Naveen! What mystery are we exploring today?",
            "Launching Google! The entire internet at your paws, Naveen!"
        ]
    },
    "github": {
        "url": "https://www.github.com",
        "name": "GitHub",
        "patterns": [r"\b(open github|launch github|go to github|^github$)\b"],
        "answers": [
            "Opening GitHub! Time to push some purr-fect code, Naveen!",
            "Launching GitHub for you, Naveen! Let's check those repositories and stars!"
        ]
    },
    "whatsapp": {
        "url": "https://web.whatsapp.com",
        "name": "WhatsApp Web",
        "patterns": [r"\b(open whatsapp|launch whatsapp|open whatsapp web|whatsapp web|^whatsapp$)\b"],
        "answers": [
            "Opening WhatsApp Web for you, Naveen! Don't let Joey and Dee Dee read your chats!",
            "Launching WhatsApp! Time to chat with friends, Naveen!"
        ]
    },
    "gmail": {
        "url": "https://mail.google.com",
        "name": "Gmail",
        "patterns": [r"\b(open gmail|launch gmail|check gmail|check mail|open mail|open email|^gmail$)\b"],
        "answers": [
            "Opening Gmail for you, Naveen! Checking your inbox for exciting emails!",
            "Launching Gmail! Hope the cockroaches didn't send you any spam, Naveen!"
        ]
    },
    "spotify": {
        "url": "https://open.spotify.com",
        "name": "Spotify",
        "patterns": [r"\b(open spotify|launch spotify|play spotify|^spotify$|play music|listen to music)\b"],
        "answers": [
            "Opening Spotify for you, Naveen! Turn up the volume and dance to the groove!",
            "Launching Spotify! Time for some relaxing cartoon tunes, Naveen!"
        ]
    },
    "chatgpt": {
        "url": "https://chatgpt.com",
        "name": "ChatGPT",
        "patterns": [r"\b(open chatgpt|launch chatgpt|open chat gpt|^chatgpt$|open openai)\b"],
        "answers": [
            "Opening ChatGPT for you, Naveen! But remember, Oggy is always your favorite AI buddy!",
            "Launching ChatGPT! Double AI power activated for Naveen!"
        ]
    },
    "wikipedia": {
        "url": "https://www.wikipedia.org",
        "name": "Wikipedia",
        "patterns": [r"\b(open wikipedia|launch wikipedia|^wikipedia$)\b"],
        "answers": [
            "Opening Wikipedia! Time to dive into the ocean of knowledge, Naveen!",
            "Launching Wikipedia for you, Naveen! Let's learn something astonishing today!"
        ]
    },
    "reddit": {
        "url": "https://www.reddit.com",
        "name": "Reddit",
        "patterns": [r"\b(open reddit|launch reddit|^reddit$)\b"],
        "answers": [
            "Opening Reddit for you, Naveen! Let's see what is trending across the internet!"
        ]
    },
    "twitter": {
        "url": "https://twitter.com",
        "name": "Twitter / X",
        "patterns": [r"\b(open twitter|launch twitter|open x|^twitter$)\b"],
        "answers": [
            "Opening X Twitter for you, Naveen! Time to catch up on the latest trends and tweets!"
        ]
    },
    "netflix": {
        "url": "https://www.netflix.com",
        "name": "Netflix",
        "patterns": [r"\b(open netflix|launch netflix|^netflix$)\b"],
        "answers": [
            "Opening Netflix! Grab your snacks and popcorn, Naveen, movie time is here!"
        ]
    },
    "maps": {
        "url": "https://maps.google.com",
        "name": "Google Maps",
        "patterns": [r"\b(open maps|open google maps|launch maps|^maps$|google maps)\b"],
        "answers": [
            "Opening Google Maps for you, Naveen! Finding our path around the world!"
        ]
    },
    "calculator": {
        "url": "https://www.google.com/search?q=calculator",
        "name": "Calculator",
        "patterns": [r"\b(open calculator|launch calculator|^calculator$|open calc|^calc$)\b"],
        "answers": [
            "Opening the calculator for you, Naveen! Time to do some quick cat math!"
        ]
    }
}

# Dynamic pattern handlers
def get_dynamic_answer(query: str):
    q = query.lower().strip()
    
    # Time query
    if any(phrase in q for phrase in ["time", "what time", "current time", "what's the time"]):
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")
        return {
            "answer": f"Right now, my cartoon clock says it is {time_str}! Perfect time for a cat snack!",
            "emotion": "smile",
            "video_style": "speaking_talk"
        }

    # Date query
    if any(phrase in q for phrase in ["date", "what is the date", "today's date", "which day", "what day is"]):
        today = datetime.date.today()
        date_str = today.strftime("%A, %B %d, %Y")
        return {
            "answer": f"Today is {date_str}! Another splendid day to outsmart the cockroaches!",
            "emotion": "excited",
            "video_style": "speaking_talk"
        }

    # 1. Available applications query
    if re.search(r"\b(what apps can you open|which applications can you open|open apps|open applications|what can you open)\b", q):
        return {
            "answer": "I can open YouTube, Google, GitHub, WhatsApp, Spotify, Gmail, ChatGPT, Wikipedia, Netflix, Calculator, Terminal, VS Code, and File Manager! Plus, you can ask me to search Google for anything!",
            "emotion": "proud",
            "video_style": "speaking_talk"
        }

    # 2. General search query prompt
    if q in ["search", "google search", "web search", "search for"]:
        return {
            "answer": "What would you like me to search for, Naveen? Tell me a topic, or say 'search for [topic]', and I'll find it right away on Google!",
            "emotion": "smile",
            "video_style": "speaking_talk"
        }

    # 3. YouTube Search / Play
    m_yt = re.search(r"\b(?:search youtube for|youtube search|search on youtube for)\s+(.+)$", q)
    if not m_yt:
        m_yt = re.search(r"^play\s+(.+?)\s+on youtube$", q)
    if m_yt:
        search_term = m_yt.group(1).strip(" ?.!\"'")
        if search_term:
            url = f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(search_term)}"
            return {
                "answer": f"Searching YouTube for {search_term}! Enjoy the video, Naveen! Paws ready for the show!",
                "emotion": "excited",
                "video_style": "speaking_gesture",
                "action": {
                    "type": "open_url",
                    "url": url,
                    "title": f"YouTube: {search_term}"
                }
            }

    # 4. Google Web Search
    search_term = None
    m_search = re.search(r"\b(?:search for|look up|web search)\s+(.+?)(?:\s+on google|\s+in google)?$", q)
    if not m_search:
        m_search = re.search(r"^(?:google|search on google for)\s+(.+)$", q)
    if not m_search:
        m_search = re.search(r"^search\s+(.+?)(?:\s+on google|\s+in google)?$", q)
    if not m_search:
        m_search = re.search(r"^(.+?)\s+on google$", q)

    if m_search and not q.startswith("open "):
        cand = m_search.group(1).strip(" ?.!\"'")
        if cand and cand not in ["for", "google", "web", "something", "anything"]:
            search_term = cand

    if search_term:
        url = f"https://www.google.com/search?q={urllib.parse.quote_plus(search_term)}"
        replies = [
            f"Searching Google for {search_term}! Here you go, Naveen! Let's see what the web says!",
            f"Paws on the keyboard! Searching for {search_term} right away, Naveen!",
            f"Looking up {search_term} on Google! Fresh results coming right up for you, Naveen!"
        ]
        return {
            "answer": random.choice(replies),
            "emotion": "excited",
            "video_style": "speaking_gesture",
            "action": {
                "type": "open_url",
                "url": url,
                "title": f"Google: {search_term}"
            }
        }

    # 5. Local Desktop Applications
    if re.search(r"\b(open terminal|launch terminal|open alacritty|open console|start terminal|^terminal$)\b", q):
        return {
            "answer": "Opening your terminal! Terminal powers unleashed for Naveen!",
            "emotion": "excited",
            "video_style": "speaking_gesture",
            "action": {
                "type": "local_app",
                "app": "terminal",
                "cmd": "alacritty",
                "title": "Terminal"
            }
        }

    if re.search(r"\b(open vs code|open vscode|open code|launch vs code|open editor|launch code|^vscode$|^vs code$)\b", q):
        return {
            "answer": "Opening Visual Studio Code for you, Naveen! May your code compile with zero bugs!",
            "emotion": "excited",
            "video_style": "speaking_gesture",
            "action": {
                "type": "local_app",
                "app": "code",
                "cmd": "code",
                "title": "VS Code"
            }
        }

    if re.search(r"\b(open file manager|open files|open file explorer|open folders|launch files|^files$|^nautilus$)\b", q):
        return {
            "answer": "Opening your file manager! Keep those sneaky cockroaches away from your folders, Naveen!",
            "emotion": "excited",
            "video_style": "speaking_gesture",
            "action": {
                "type": "local_app",
                "app": "files",
                "cmd": "nautilus",
                "title": "File Manager"
            }
        }

    # 6. Known Web Applications
    for key, app_info in KNOWN_WEB_APPS.items():
        for pat in app_info["patterns"]:
            if re.search(pat, q):
                ans = random.choice(app_info["answers"])
                return {
                    "answer": ans,
                    "emotion": "excited",
                    "video_style": "speaking_gesture",
                    "action": {
                        "type": "open_url",
                        "url": app_info["url"],
                        "title": app_info["name"]
                    }
                }

    # 7. Generic Website Open (e.g. "open instagram", "open discord", "open amazon")
    m_generic = re.match(r"^(?:open|launch|go to)\s+([a-zA-Z0-9\-]+)(?:\.com|\.org|\.net|\.in|\.io)?$", q)
    if m_generic:
        site = m_generic.group(1).lower()
        if site not in ["the", "a", "an", "this", "my", "your", "apps", "app"]:
            return {
                "answer": f"Opening {site.capitalize()} for you, Naveen! Right on it!",
                "emotion": "excited",
                "video_style": "speaking_gesture",
                "action": {
                    "type": "open_url",
                    "url": f"https://www.{site}.com",
                    "title": site.capitalize()
                }
            }

    return None


def find_feed_answer(query: str):
    """
    Search the pre-configured feed Q&A.
    Returns dict with answer, emotion, video_style, matched=True,
    or None if no match found.
    """
    if not query or not query.strip():
        return {
            "answer": "Meow? I'm listening! Speak up or type something, buddy!",
            "emotion": "smile",
            "video_style": "speaking_talk",
            "matched": True
        }

    # Check dynamic handlers first
    dynamic_match = get_dynamic_answer(query)
    if dynamic_match:
        dynamic_match["matched"] = True
        return dynamic_match

    q_clean = query.lower().strip()
    # Remove excessive punctuation
    q_norm = re.sub(r"[^\w\s]", "", q_clean)

    # 1. Regex Pattern check
    for item in FEED_QA:
        for pat in item.get("patterns", []):
            if re.search(pat, q_clean, re.IGNORECASE):
                ans = random.choice(item["answers"])
                return {
                    "answer": ans,
                    "emotion": item.get("emotion", "smile"),
                    "video_style": item.get("video_style", "speaking_talk"),
                    "matched": True
                }

    # 2. Keyword check with word boundaries
    tokens = set(re.findall(r"\b\w+\b", q_clean))
    for item in FEED_QA:
        for kw in item.get("keywords", []):
            kw_clean = kw.lower().strip()
            # If multi-word keyword phrase (e.g. "what's up", "who are you")
            if " " in kw_clean:
                if kw_clean in q_clean:
                    ans = random.choice(item["answers"])
                    return {
                        "answer": ans,
                        "emotion": item.get("emotion", "smile"),
                        "video_style": item.get("video_style", "speaking_talk"),
                        "matched": True
                    }
            else:
                # Single word keyword must match a whole token
                if kw_clean in tokens:
                    ans = random.choice(item["answers"])
                    return {
                        "answer": ans,
                        "emotion": item.get("emotion", "smile"),
                        "video_style": item.get("video_style", "speaking_talk"),
                        "matched": True
                    }

    return None


# Fun Fallbacks when query is not in feed and Gemini is not used
WITTY_FALLBACKS = [
    "Meow! That's an interesting question! I was busy defending my sandwich from Dee Dee, but my cat instincts say: Always follow your curiosity!",
    "Hahaha! You caught me scratching my ears! While I think about that, remember that a warm nap fixes everything!",
    "*Tilts head and winks* That sounds like a riddle cousin Jack would love to solve! Ask me something else or connect Google Gemini in settings to unlock my cosmic cat brain!",
    "Meowza! My database is vast, but that one is top secret cartoon intelligence! Try asking me about the cockroaches, a joke, or the time!",
    "Whoa! That blew right past my whiskers! Either that's top-tier philosophy or Joey scrambled my circuits! What else is on your mind?"
]

def get_fallback_answer():
    return {
        "answer": random.choice(WITTY_FALLBACKS),
        "emotion": "thinking",
        "video_style": "speaking_emote",
        "matched": False
    }
