# GmSSL 的 SM2 加解密与签名验签

姓名：蔡贸俊；学号：20241328；班级：2413。

- [Markdown 报告](20241328-蔡贸俊-GmSSL的SM2加解密与签名验签.md)
- [PDF 报告（含运行截图）](20241328-蔡贸俊-GmSSL的SM2加解密与签名验签.pdf)
- [完整 C 源码](src/sm2_file.c)
- [AI 使用与问答记录](logs/AI使用记录.md)
- [原始运行日志](logs/practice.txt)
- [提交清单](INDEX_提交清单.md)

## 实际结果

在 openEuler 24.03 LTS / GmSSL 3.3.0-dev.1183 中完成。命令生成 SM2 密钥对；C 程序把完整 261 字节文件按 255 + 6 字节分块加解密，diff 返回 0；对完整文件签名验签通过，篡改后拒绝。CLI 解密和签名双向验证通过。

## 复现

```bash
bash run.sh
```

输入新的私钥口令后，脚本生成新密钥、编译并执行全部核心操作。重新运行会替换公钥、密文与签名，已有日志对应本次交付时的那一次运行。

公开仓库不包含私钥；`sm2_public.pem` 可用于直接复核 `sn.sig`：

```bash
gmssl sm2verify -pubkey sm2_public.pem -id 1234567812345678 -in sn.txt -sig sn.sig
```

`sn.enc` 是自定义 SM2F 分块封装，不能直接作为单个 DER 传给 CLI。`logs/block1.der` 和 `logs/block2.der` 是提取后的标准 DER 块。此格式用于课堂实验，不是标准的整文件认证加密方案。

说明：报告及 AI 使用记录由 AI 依据实际过程生成；代码编写、工具执行、验证和整理包含 AI 辅助。
