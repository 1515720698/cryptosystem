# 提交清单

姓名：蔡贸俊；学号：20241328。

## 必交

- `20241328-蔡贸俊-GmSSL的SM4-CBC文件加解密.md`
- `20241328-蔡贸俊-GmSSL的SM4-CBC文件加解密.pdf`：含运行截图的最新提交版。
- `src/sm4_file.c`：建议与两份报告一并提交；报告附录也包含全文。

## 运行证据与数据

- `sn.txt`：以前课堂文件的原样副本，29 个学号，本人最后。
- `sn.enc`：SM4-CBC / PKCS#7 密文，272 字节。
- `sn2.txt`：解密明文，261 字节，与 sn.txt 的 Linux diff 返回 0。
- `key.bin`、`iv.bin`：本次实验生成的各 16 字节随机值。
- `logs/practice.txt`：环境、编译、运行、diff、SHA-256 的真实记录。
- `logs/cross-check.txt`、`logs/sn_cli.txt`：CLI 交叉验证记录及输出。
- `logs/initial-cross-check.txt`：首次 CLI 填充选项问题记录（控制字符已注明可读表示）。
- `logs/AI问答记录.md`：本次真实对话节录。
- `logs/AI使用记录.md`：按实际辅助过程整理的 AI 使用摘要，文末注明由 AI 生成。
- `logs/input-source.txt`：学号文件来源及摘要。
- `images/`：两张原始终端窗口截图及用于报告的裁剪展示版。
- `logs/screenshot-run/`：截图对应的补充运行源码、数据、随机值及两份文本记录。

## 复现

在安装了相同 GmSSL 的 openEuler 中进入本目录，执行：

```bash
bash run.sh
```

重新运行会更换随机密钥、IV 和密文；报告中的数值对应交付时的那次运行。
`tools/execute.py` 用于采集原环境日志，依赖原环境的 `/root/hash_hw/sn.txt`；常规复现使用现有 sn.txt 和 run.sh。
`tools/make_report.py` 根据 logs 和源码生成 Markdown；PDF 使用本机 Markdown 转 PDF 工具生成。
