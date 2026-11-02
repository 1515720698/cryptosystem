# 第七周预习报告交付清单

## 主要文件

- `20241328蔡贸俊《密码系统设计》.md`
- `20241328蔡贸俊《密码系统设计》第7周.pdf`（11 页，按 Markdown 重新排版生成）
- `assets/week7-mindmap.png`、`assets/week7-mindmap.mmd`

## 要求对应

| 课程要求 | 报告章节 | 证据或附件 |
| --- | --- | --- |
| 第 10 章 10.1—10.4 | 第一部分第 1 节 | 认证方式、PKI、X.509 与数字信封 |
| 重点第 11 章 11.1—11.4 | 第一部分第 2 节 | CA 配置、签发与原生 X.509 接口调用 |
| AI 总结反思 | 第二部分 | 学生视角草稿，待本人核对 |
| 导图源码和截图 | 第三部分 | Mermaid 源文件、实际渲染的 PNG |
| 两个概念的苏格拉底问答 | 第四部分 | 明确标注的 AI 学习示例，待本人作答或核对 |
| 至少两个问题的解决过程 | 第五部分 | 缺中间证书、域名与用途错误、吊销检查未启用 |
| Markdown 与 PDF | 主文件和文末说明 | 学号姓名正确、PDF 文本与图像检查 |

## 复现

Windows 安装 Python 和 OpenSSL 后，在本目录执行：

```powershell
python code/run_pki.py --openssl "C:\Program Files\Git\usr\bin\openssl.exe"
python code/verify_x509_api.py --libcrypto "C:\Program Files\Git\ucrt64\bin\libcrypto-3-x64.dll"
```

本次实际采用 Windows 10 x64、Python 3.12.10、OpenSSL 3.5.9。第一条脚本在隔离临时目录创建教学 CA，完成后导出公开证书和 CRL，自动清理测试私钥。第二条通过 ctypes 调用原生 C API，不是编译 C 源码。

重新运行会重新生成本目录中的公开实验材料并更新日志，其证书指纹与时间自然变化；如需严格保留本次证据，请先复制整个目录。

## 验证结果与附件

- `evidence/experiment-log.txt`：完整命令与输出，10 项命令行检查通过。
- `evidence/results.json`：10 项检查的结构化结果。
- `evidence/x509-api-log.txt`：3 项原生 API 检查通过及字段读取结果。
- `evidence/root-cert.pem`、`intermediate-cert.pem`、`server-cert.pem`、`server-cert.der`：公开证书。
- `evidence/before.crl.pem`、`after.crl.pem`：吊销前后 CRL，7 天有效，逾期应重跑生成新材料。
- `evidence/server.csr`：服务器公开申请；`intermediate-index.txt`：吊销后的 CA 数据库快照。
- `code/root.cnf`、`code/intermediate.cnf`：实际配置快照，完整运行环境由脚本初始化。
- `evidence/pdf-contact-sheet.png`、`pdf-page-*.png`、`pdf-text-check.txt`：分页图、总览和文本核验。

## 来源与使用说明

报告按往周六部分格式和老师要求完成，第 11 章重点展开。本次依据教材公开目录及 OpenSSL 官方资料整理，未取得付费章节全文。个人反思属于待本人核对的学生视角草稿，苏格拉底问答属于 AI 生成的学习示例；真实逐轮问答仍需本人参与。

渲染脚本 `code/render_delivery.py` 依赖本机全局 cryptosystem-report Skill、Markdown、Pillow、PyMuPDF 和 Edge，跨机器需相应配置。
