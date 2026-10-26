# GmSSL 的 SM4-CBC 文件加解密课堂测试

姓名：蔡贸俊；学号：20241328；班级：2413。

## 报告与代码

- [Markdown 报告](20241328-蔡贸俊-GmSSL的SM4-CBC文件加解密.md)
- [PDF 报告（含运行截图）](20241328-蔡贸俊-GmSSL的SM4-CBC文件加解密.pdf)
- [C 源代码](src/sm4_file.c)
- [提交清单](INDEX_提交清单.md)
- [AI 使用记录](logs/AI使用记录.md)

## 运行

环境：openEuler 24.03 LTS、GCC 12.3.1、GmSSL 3.3.0-dev.1183。
在已安装 GmSSL 的 Linux 中进入本目录，运行：

```bash
bash run.sh
```

程序分别调用 `rand_bytes` 生成 16 字节密钥与 IV，使用 SM4-CBC 和 PKCS#7 填充加密 `sn.txt`，解密为 `sn2.txt`，随后执行 Linux `diff`。本次实际结果为 261→272→261 字节，`diff` 返回 0。

`key.bin`、`iv.bin` 和日志中对应的值均为公开课堂实验的测试参数；重新运行会生成新值。`logs/screenshot-run/` 保存单独一次补充运行的数据与日志，窗口截图见 `images/`。

说明：报告正文及 AI 使用记录由 AI 依据实际交流、代码、日志和截图生成；代码编写、工具执行、排错及文档整理包含 AI 辅助。
