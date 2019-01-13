import base64
def enc(s):
  s=base64.b64encode(bytes(s,"utf-8")).decode("utf-8")
  return(s)

def dec(s): return(base64.b64decode(s).decode("utf-8"))

if __name__=="__main__":

  s=r"./registration.txt"

  print("\nORIGINAL STRING:")
  print(s)
  print("\nENCODED:")
  print(enc(s))
  print("\nDECODED:")
  print(dec(enc(s)))
