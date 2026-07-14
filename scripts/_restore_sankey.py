src = r"D:\Ayueqian\project\code\douban-bigdata\scripts\_sankey_good.vue"
dst = r"D:\Ayueqian\project\code\douban-bigdata\frontend\src\views\Sankey.vue"
import os
data = open(src, "rb").read()
# strip BOM
if data[:3] == b"\xef\xbb\xbf":
    data = data[3:]
# strip CR
data = data.replace(b"\r\n", b"\n")
open(dst, "wb").write(data)
print("written, size:", os.path.getsize(dst), "bytes")
