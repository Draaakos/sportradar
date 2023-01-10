import os
import json
import time
import requests


url = 'https://betsapi.com/rh/6102738/Juventus-%28Calvin%29-Esports-vs-Inter-%28Petruchio%29-Esports'
response = requests.get(url)
print(response)