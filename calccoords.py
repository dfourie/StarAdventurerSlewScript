import requests
import astropy.units as u
from astropy.coordinates import SkyCoord, Angle
"""
This script automates the process laid out in this post https://www.dpreview.com/forums/post/62267807
by leveraging stellerium

Software required:
1) You need stellerium installed, with the telescope control and remote control addons 
running.
2) You will need a python environment along with astropy installed 

Stellerium setup
1) Start up stellerium 
2) In toolbar, select the telescope button and configure a new virtual telescope called Telescope1 
3) Connect to the virtual scope, you should see a recticle on the screen
4) Start the remote control server with the button on the toolbar.

Useage:
1) Aim and center your physical telescope at a bright star near your desired object
2) In Stellerium, slew your virtual telescope to the same star (ctrl+1 or use the telescope control window)
3) Once the virtual telescope is aiming at the star, use the mouse cursor to select the object you want to slew to.
4) With the object selected (its information should appear in the stellerium screen), run this script.
5) The script will fetch the values of the current star and desired coordinates from Stellerium and calculate the operations you need
to do on your star adventurer.

"""

headers={'Accept':'application/json'}

# Helper function that makes a skycoord from a json
def getSkycoordsFromJSON(coords):
    ra=coords["ra"]
    dec=coords["dec"]
    return SkyCoord(ra*u.degree, dec*u.degree)

#Telescope name in stellerium
TELESCOPE_NAME="Telescope1"

# Seconds at 12x on Star adventurer that correspond to a minute on RA
POS_MINUTE_OFFSET=4.62
NEG_MINUTE_OFFSET=5.45

# One full rotation of the DEC knob is this many degrees
DEC_FULL_TURN=2.95

# NB!! Set this to False if you are in the Southern Hemisphere.
SOUTHERN_HEMISPHERE=True

# Since I wrote this in the southern hemisphere, the dialog is from the initial perspective 
# of the southern hemisphere
S_text = 'S' if SOUTHERN_HEMISPHERE else 'N'
N_text = 'N' if SOUTHERN_HEMISPHERE else 'S'

# Print setup commands
print("Center telescope recticle to known object")
print("Slew virtual telescope to object in stellerium (Ctrl+1)")
print("Select object you want to get offset coordinates to")

# Fetch coords from stellerium
currentObj=requests.get('http://localhost:8090/api/objects/info?format=map', headers=headers)
telesecopeObj=requests.get(f'http://localhost:8090/api/objects/info?format=map&name={TELESCOPE_NAME}', headers=headers)
currentObjCoords=getSkycoordsFromJSON(currentObj.json())
telesecopeObjCoords=getSkycoordsFromJSON(telesecopeObj.json())

# Calculate the RA current difference 
RADiff= telesecopeObjCoords.ra.deg-currentObjCoords.ra.deg

# Round it a bit.
RADiff = round(RADiff)

ang=Angle(f"{RADiff}d")

# Calculate RA adjustment
RA_adjustment=abs(ang.hms.m)*NEG_MINUTE_OFFSET if ang.hms.m <0 else ang.hms.m*POS_MINUTE_OFFSET

# Print RA adjustment
print(f"Press {('S' if SOUTHERN_HEMISPHERE else 'N') if ang.hms.m <0 else ('N' if SOUTHERN_HEMISPHERE else 'S')} for {round(RA_adjustment)} seconds")

#Calculate the DEC difference 
DECDiff= telesecopeObjCoords.dec.deg-currentObjCoords.dec.deg
# Calculate number of turns
numTurns=round(DECDiff/DEC_FULL_TURN,1)

# Make 
away_text = f'away from {S_text} celestial pole'
towards_text = f"towards {S_text} celestial pole"

print(f"Rotate dec knob {abs(numTurns)} turns {away_text if numTurns <0 else towards_text}")
