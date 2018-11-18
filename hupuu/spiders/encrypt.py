import base64
from pyDes import *
import os

Des_Key = b"DESCRYPT"
Des_IV = b"\x22\x33\x35\x81\xBC\x38\x5A\xE7" # 自定IV向量
mydes = des(Des_Key,CBC ,Des_IV, pad=None, padmode=PAD_PKCS5)
os.chdir(r"C:\Users\james\Desktop\haha")


def DesEncrypt(byte):

    EncryptStr = mydes.encrypt(byte)  #返回byte
 
    return base64.b64encode(EncryptStr) 

def DesDecrypt(str):
    bin=base64.b64decode(str)

    byte = mydes.decrypt(bin)  #返回byte

    return byte 


def parse_file(allfilename,parse):
    # path_name=os.path.split(allfilename)
    if(parse):
        with open(allfilename,'rb') as bin:
            bindata=bin.read()
            en_str= DesEncrypt(bindata)
            with open(allfilename+".DES",'wb') as out:
                out.write(en_str)
    else:
        if(allfilename[-3:]=="DES"):
            
            with open(allfilename,'rb') as bin:
                bindata=bin.read()
                en_str= DesDecrypt(bindata)
                with open(allfilename[:-4],'wb') as out:
                    out.write(en_str)

    os.remove(allfilename)


def parse_dir(path,parse):
  
    lis=os.listdir(path)
    for i in lis:
        allpath=path+'\\'+i
        if(os.path.isfile(allpath)):
            parse_file(allpath,parse)
        if(os.path.isdir(allpath)):
            parse_dir(allpath,parse)

parse_dir(r"C:\Users\james\Desktop\UUmtu\output",True)