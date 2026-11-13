import os
import re

def clean_for_speech(text):
    t = text
    
    # 1. PEP: Explicitly "Peak Envelope Power"
    t = re.sub(r'1500\s*(?:W|watts?)?\s*PEP', 'fifteen hundred Watts Peak Envelope Power,', t, flags=re.IGNORECASE)
    t = t.replace('fifteen hundred watts, P-E-P,', 'fifteen hundred Watts Peak Envelope Power,')
    t = t.replace('fifteen hundred Watts, P, E, P,', 'fifteen hundred Watts Peak Envelope Power,')
    t = t.replace('P, E, P,', 'Peak Envelope Power')
    t = re.sub(r'\bPEP\b', 'Peak Envelope Power', t)
    t = re.sub(r'\bP-E-P\b', 'Peak Envelope Power', t)
    t = re.sub(r'\bpep\b', 'Peak Envelope Power', t)
    
    # 2. Operating System: NEVER use Debian reference! Strictly Raspberry Pi OS / RPI OS
    t = re.sub(r'\bDebian 13 Trixie\b', 'sixty-four-bit Raspberry Pi O S', t, flags=re.IGNORECASE)
    t = re.sub(r'\bDebian Trixie\b', 'Raspberry Pi O S', t, flags=re.IGNORECASE)
    t = re.sub(r'\bDebian 13\b', 'Raspberry Pi O S', t, flags=re.IGNORECASE)
    t = re.sub(r'\bDebian\b', 'Raspberry Pi O S', t, flags=re.IGNORECASE)
    t = re.sub(r'\bBookworm\b', 'Raspberry Pi O S', t, flags=re.IGNORECASE)
    t = re.sub(r'\bRPI OS\b', 'Raspberry Pi O S', t, flags=re.IGNORECASE)
    
    # 3. Callsign & Names: Never use "John". Do NOT replace "station" with K7BIT.
    # Do not use "K7BIT Master"
    t = re.sub(r'\bK7BIT Master\b', 'Station Reference', t, flags=re.IGNORECASE)
    t = t.replace("John K7BIT's", "K seven B I T's")
    t = t.replace("John K7BIT", "K seven B I T")
    t = re.sub(r'\bJohn\b', '', t)
    # When K7BIT appears literally, pronounce it as K seven B I T
    t = re.sub(r'\bK7BIT\b', 'K seven B I T', t)
    
    # 4. Terminology: NEVER say "web cockpit", ALWAYS say "JRFK Web Tools"
    t = re.sub(r'\b(?:web cockpit|operational web cockpit|web operations cockpit)\b', 'JRFK Web Tools', t, flags=re.IGNORECASE)
    t = re.sub(r'\b7-screen operational web cockpit\b', 'seven-screen JRFK Web Tools', t, flags=re.IGNORECASE)
    t = re.sub(r'\b7-screen web cockpit\b', 'seven-screen JRFK Web Tools', t, flags=re.IGNORECASE)
    t = re.sub(r'\bJRFK Web Tool\b', 'JRFK Web Tools', t, flags=re.IGNORECASE)
    
    # 5. LDMOS: pronounced "LD MOS" (L-D moss)
    t = re.sub(r'\bLDMOS\b', 'L-D moss', t)
    t = re.sub(r'\bL D M O S\b', 'L-D moss', t)
    
    # 6. RF-KIT -> R F kit
    t = re.sub(r'\bRF-KIT\b', 'R F kit', t)
    t = re.sub(r'\bRF-Kit\b', 'R F kit', t)
    t = re.sub(r'\bRF\b', 'R F', t)
    
    # 7. Bands
    t = t.replace('160 meters through 6 meters', 'one sixty through six meters')
    t = t.replace('160m through 6m', 'one sixty through six meters')
    t = t.replace('160 meters', 'one sixty')
    t = t.replace('6 meters', 'six meters')
    
    # 8. Architectures & Tool names
    t = re.sub(r'\b32-bit\b', 'thirty-two-bit', t)
    t = re.sub(r'\b64-bit\b', 'sixty-four-bit', t)
    t = t.replace('JRFK.exe', 'J R F K dot E X E')
    t = re.sub(r'\bJRFK\b', 'J R F K', t)
    t = t.replace('C-sharp', 'C sharp')
    t = t.replace('166-megabyte', 'one hundred sixty-six megabyte')
    
    # 9. Technical terms
    t = re.sub(r'\bSWR\b', 'S W R', t)
    t = re.sub(r'\bVSWR\b', 'V S W R', t)
    t = t.replace('SimpleRPC', 'Simple R P C')
    t = t.replace('Full KMS DRM', 'Full K M S D R M')
    t = t.replace('fake-KMS', 'fake K M S')
    t = t.replace('X11', 'X eleven')
    t = t.replace('1024 by 600', 'ten twenty-four by six hundred')
    t = t.replace('53.5-volt DC', 'fifty-three point five volt D C')
    t = t.replace('53.5-volt', 'fifty-three point five volt')
    t = re.sub(r'\bDC\b', 'D C', t)
    t = t.replace('BLF189', 'B L F one eighty-nine')
    t = t.replace('CAN bus', 'C A N bus')
    t = t.replace('CAT control', 'C A T control')
    t = re.sub(r'\bSD card\b', 'S D card', t)
    t = re.sub(r'\bSD cards\b', 'S D cards', t)
    t = re.sub(r'\bsystemd\b', 'system D', t)
    t = t.replace('193-page', 'one hundred ninety-three page')
    t = re.sub(r'\b73\b', 'seventy-three', t)
    t = t.replace('2.5 to 1', 'two point five to one')
    t = t.replace('2.5:1', 'two point five to one')
    t = t.replace('60 degrees', 'sixty degrees')
    t = t.replace('60°C', 'sixty degrees C')
    t = t.replace('4-volume', 'four-volume')
    t = t.replace('4-way', 'four-way')
    t = t.replace('7-screen', 'seven-screen')
    t = t.replace('5-point', 'five-point')
    t = re.sub(r'\bport 8088\b', 'port eighty eighty-eight', t, flags=re.IGNORECASE)
    t = re.sub(r'\bHDMI\b', 'H D M I', t)
    t = re.sub(r'\bHTTP\b', 'H T T P', t)
    t = re.sub(r'\bPC\b', 'P C', t)
    
    return t
