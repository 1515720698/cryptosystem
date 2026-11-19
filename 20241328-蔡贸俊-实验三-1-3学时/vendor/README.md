# 龙脉 SKF 运行库

`libgm3000.1.0.so` 不纳入 Git。若克隆提交仓库后本目录没有运行库，在项目根目录运行：

```bash
tmp=$(mktemp -d)
git clone https://gitee.com/rocedu/bestidiocs4stu.git "$tmp/course"
git -C "$tmp/course" checkout --detach 048ec69e7998c9d13eb4624541acbe6b1e089589
unzip -p "$tmp/course/ch06/longmaiskf0016-stu.zip" \
  longmaiskf0016-stu/skf/linux/x64/libgm3000.1.0.so \
  > vendor/libgm3000.1.0.so
sha256sum -c vendor/SHA256SUMS
```

此库适用于 Linux x86_64。实体设备测试还需要厂商支持的龙脉 UKey 和相应运行环境。
