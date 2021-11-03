# EXECUTE SOME PYTHON CODE FROM WEBSITE
# Create by: Ney Moresco
# Date: 2021-11-03
'''
USAGE:
- Example using github raw code

REQUISITES:
- requests Package

'''

import requests
url = 'https://raw.githubusercontent.com/moresconey/public/main/scripts/press_one_key.py'
code = requests.get(url)
exec(code.content)