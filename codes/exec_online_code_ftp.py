# EXECUTE SOME PYTHON CODE FROM FTPS SERVER
# Create by: Ney Moresco
# Date: 2021-11-01
'''
USAGE:
- Example using FTPS Server
REQUISITES:
- ssl, ftplib and io Packages

'''

# Load Packages
import ssl
import ftplib
from io import BytesIO

# Set variables
user = 'user'
psw = 'password'
host = 'server'
port = 21 # Integer Port, FTP default 21
filePath = 'Path_with_fileName'

# Login in the FTP
ftps = ftplib.FTP_TLS()
ftps.ssl_version = ssl.PROTOCOL_SSLv23
ftps.connect(host, port)
ftps.login(user, psw)
ftps.prot_p()

r = BytesIO()

# Download python file
ftps.retrbinary('RETR ' + filePath, r.write)
ftps.close()

# Execute python code
exec(r.getvalue())
