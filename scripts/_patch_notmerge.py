# -*- coding: utf-8 -*-
"""把 EChart.vue 的 notMerge 默认值改为 true(避免 setOption merge 模式丢数据)"""
p = r"D:\Ayueqian\project\code\douban-bigdata\frontend\src\components\EChart.vue"
data = open(p, "rb").read().decode("utf-8")
old = "  notMerge: { type: Boolean, default: false },"
new = "  notMerge: { type: Boolean, default: true },"
assert old in data, "notMerge default line not found"
data = data.replace(old, new)
open(p, "wb").write(data.encode("utf-8"))
print("[OK] EChart.vue notMerge default -> true")
