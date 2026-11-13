import os
import re

def clean_for_speech(text):
    t = text
    
    # Callsign K7BIT identification - NEVER say John, NEVER say "from the station", say "from K7BIT"
    t = t.replace("from the station", "from K seven B I T")
    t = t.replace("the station", "K seven B I T")
    t = t.replace("John K7BIT's", "K seven B I T's")
    t = t.replace("John K7BIT", "K seven B I T")
    t = re.sub(r'\bJohn\b', 'K seven B I T', t)
    
    # Pronounce PEP naturally as peak envelope power
    t = re.sub(r'\bPEP\b', 'peak envelope power', t)
    
    # Pronounce RF-KIT as R F kit (natural speech, not spelling out R-F-dash-K-I-T)
    t = re.sub(r'\bRF-KIT\b', 'R F kit', t)
    t = re.sub(r'\bRF-Kit\b', 'R F kit', t)
    t = re.sub(r'\bRF\b', 'R F', t)
    
    # Ham bands
    t = t.replace('160 meters through 6 meters', 'one hundred sixty meters through six meters')
    t = t.replace('160m through 6m', 'one hundred sixty meters through six meters')
    t = t.replace('160 meters', 'one hundred sixty meters')
    t = t.replace('6 meters', 'six meters')
    
    # Architectures
    t = re.sub(r'\b32-bit\b', 'thirty-two-bit', t)
    t = re.sub(r'\b64-bit\b', 'sixty-four-bit', t)
    
    # Tool and binary names
    t = t.replace('JRFK.exe', 'J R F K dot E X E')
    t = re.sub(r'\bJRFK\b', 'J R F K', t)
    t = t.replace('C-sharp', 'C sharp')
    t = t.replace('166-megabyte', 'one hundred sixty-six megabyte')
    
    # Technical & Radio terms
    t = re.sub(r'\bSWR\b', 'S W R', t)
    t = t.replace('SimpleRPC', 'Simple R P C')
    t = t.replace('Full KMS DRM', 'Full K M S D R M')
    t = t.replace('fake-KMS', 'fake K M S')
    t = t.replace('X11', 'X eleven')
    t = t.replace('1024 by 600', 'ten twenty-four by six hundred')
    t = t.replace('53.5-volt DC', 'fifty-three point five volt D C')
    t = t.replace('53.5-volt', 'fifty-three point five volt')
    t = re.sub(r'\bDC\b', 'D C', t)
    t = t.replace('BLF189', 'B L F one eighty-nine')
    t = re.sub(r'\bLDMOS\b', 'L D M O S', t)
    t = t.replace('CAN bus', 'C A N bus')
    t = t.replace('CAT control', 'C A T control')
    t = re.sub(r'\bSD card\b', 'S D card', t)
    t = re.sub(r'\bSD cards\b', 'S D cards', t)
    t = re.sub(r'\bsystemd\b', 'system D', t)
    t = t.replace('K7BIT', 'K seven B I T')
    t = t.replace('193-page', 'one hundred ninety-three page')
    t = re.sub(r'\b73\b', 'seventy-three', t)
    t = t.replace('2.5 to 1', 'two point five to one')
    t = t.replace('60 degrees', 'sixty degrees')
    t = t.replace('4-volume', 'four-volume')
    t = t.replace('4-way', 'four-way')
    t = t.replace('7-screen', 'seven-screen')
    t = t.replace('5-point', 'five-point')
    t = t.replace('port 8088', 'port eighty eighty-eight')
    t = re.sub(r'\bPC\b', 'P C', t)
    
    return t
