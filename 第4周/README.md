# 第四周预习报告文件说明

- 主报告：`20241328蔡贸俊《密码系统设计》.md`
- 提交 PDF：`20241328蔡贸俊《密码系统设计》第4周.pdf`
- 思维导图：`assets/week4-mindmap.mmd`、`assets/week4-mindmap.png`
- 本地实验原始输出：`evidence/experiment-log.txt`
- C 语言示例：`code/struct_demo.c`
- 综合复现：`code/run_experiments.mjs`（Node.js 18+、OpenSSL 3.x、GCC）
- Linux 命令复现：`code/sm2_demo.sh`（Bash、OpenSSL 3.x）
- PDF 导出源：`code/export_pdf.mjs`；生成的 HTML 可直接用浏览器打开。

## 重跑实践

工具在 PATH 中时：

```bash
node code/run_experiments.mjs
```

否则通过 `OPENSSL_BIN` 与 `CC` 环境变量分别指定 OpenSSL、GCC 可执行文件路径。Windows 下还需将 GCC 的 `bin` 目录加入当前进程 PATH，供编译器子进程加载运行库。脚本会用临时目录保存测试密钥和产物，结束后清理，并更新 `evidence/experiment-log.txt`。

Linux 下也可以：

```bash
bash code/sm2_demo.sh
gcc -std=c11 -Wall -Wextra -Werror code/struct_demo.c -o struct_demo
./struct_demo
```

综合脚本已在当前 Windows 环境实际运行。Linux 脚本提供对应命令流程，本次未在 Linux 环境执行。

## 阅读与提交

PDF 已内嵌导图，直接提交即可。Markdown 使用相对图片路径，建议将整个 `第4周` 文件夹一并保存或上传。

AI 学习部分保留真实起点，后续回答标注为参考示例。若教师要求本人逐轮对话记录，应在阅读后实际回答并用真实记录替换该部分。报告中实践已明确标注由 AI 助手执行。

仓库地址：https://github.com/1515720698/cryptosystem

## 重新导出 PDF

`code/export_pdf.mjs` 通过 `WEEK4_TOOLS` 指定渲染依赖所在目录，该目录需包含以下解压后的 npm 包文件夹：`marked`（15.0.12）、`mermaid`（10.9.5）、`playwright-core`（1.58.2）、`pdfjs-dist`（4.10.38）。通过 `BROWSER_BIN` 可指定 Chromium 或 Edge 可执行文件。

```bash
node code/export_pdf.mjs
```

脚本会校对正文与独立 Mermaid 源码的一致性，重新生成导图、HTML 和 PDF，并将 PDF 文本检查与抽样页面图保存到 `evidence/`。
