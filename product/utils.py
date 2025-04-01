import cloudinary
import re 


class custom_review_handler:
    
    bad_words = [
  
    "arse", "arsehead", "arsehole", "ass", "ass hole", "asshole",
    "bastard", "bitch", "bloody", "bollocks", "brotherfucker", "bugger", "bullshit",
    "child-fucker", "Christ on a bike", "Christ on a cracker", "cock", "cocksucker", "crap", "cunt",
    "dammit", "damn", "damned", "damn it", "dick", "dick-head", "dickhead", "dumb ass", "dumb-ass", "dumbass", "dyke",
    "faggot", "father-fucker", "fatherfucker", "fuck", "fucked", "fucker", "fucking",
    "god dammit", "goddammit", "God damn", "god damn", "goddamn", "Goddamn", "goddamned", "goddamnit", "godsdamn",
    "hell", "holy shit", "horseshit",
    "in shit",
    "jackarse", "jack-ass", "jackass", "Jesus Christ", "Jesus fuck", "Jesus Harold Christ",
    "Jesus H. Christ", "Jesus, Mary and Joseph", "Jesus wept",
    "kike",
    "mother fucker", "mother-fucker", "motherfucker",
    "nigga", "nigra",
    "pigfucker", "piss", "prick", "pussy",
    "shit", "shit ass", "shite", "sibling fucker", "sisterfuck", "sisterfucker", "slut",
    "son of a bitch", "son of a whore", "spastic", "sweet Jesus",
    "twat",
    "wanker"
    ]

    @classmethod
    def filter_bad_words(cls , text):
        text_lower = text.lower() 

        for word in cls.bad_words:
            pattern = r'\b' + re.escape(word) + r'\b'
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    
def deleteImageInCloudinary(image):
    try:
        cloudinary.uploader.destroy(image.name)
        print("deleted successfully")
    except Exception as e:
        # Log error but continue with update
        print(f"Error deleting old image: {e}")