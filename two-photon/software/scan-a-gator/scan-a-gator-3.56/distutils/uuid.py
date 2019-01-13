import base64
def dec(s):
  return(base64.b64decode(s).decode("utf-8"))

import subprocess
#'dmidecode.exe -s system-uuid'
x=subprocess.check_output(dec('ZG1pZGVjb2RlLmV4ZSAtcyBzeXN0ZW0tdXVpZA=='))
x=x.decode('utf-8').replace("\n",'').replace("\r",'')
print('['+x+']')