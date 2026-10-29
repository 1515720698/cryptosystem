# 第五周预习作业交付说明

## 文件

- `20241328蔡贸俊《密码系统设计》.md`：六部分预习报告及提交说明。
- `20241328蔡贸俊《密码系统设计》第5周.pdf`：排版后的 PDF。
- `assets/week5-mindmap.mmd`、`assets/week5-mindmap.png`：Mermaid 源码与实际渲染图。
- `code/rsa_pss.c`：RSA-PSS 流式签名、验签 C 示例。
- `code/run_experiments.py`：全部实践的复现脚本。
- `code/render_report.py`：复用课程 Skill 生成导图和 PDF，并进行文本提取及逐页渲染检查。
- `evidence/experiment-log.txt`：最终完整运行日志。
- `evidence/results.json`：14 项检查结果与消息摘要。
- `evidence/first-attempt-missing-headers.txt`：初次编译遇到缺少头文件的记录。
- `evidence/public.pem`、`message.txt`、`pss1.bin`、`c-signature.bin`：可独立验签的公开材料。

## 要求对应关系

| 要求 | 报告位置 | 验证／附件 |
| --- | --- | --- |
| 第 7 章学习总结 | 第一部分 7.1—7.5 | 官方文档及目录定位 |
| AI 总结的反思与补充 | 第二部分 | 四项问题、四项补充；标为本人待核对草稿 |
| Mermaid 代码与截图 | 第三部分 | assets/ 下的 mmd、PNG |
| 两个概念的苏格拉底学习 | 第四部分 | 两组逐步提问、第一人称学习回答与评价 |
| 至少两个实践问题 | 第五部分 | 三个可控复现案例、C 程序与原始日志 |
| Markdown、PDF、规范命名 | 提交说明 | 主报告文件与 PDF |

苏格拉底部分围绕签名机制的区别与 RSA-PSS 参数展开，采用逐问逐答的学习整理形式。教材没有全文输入，报告已注明公开目录及官方文档的使用范围。

## 复现

Python 3、OpenSSL 3.x、GCC 及 OpenSSL 开发文件就绪后：

```bash
python code/run_experiments.py
```

工具不在 PATH 时设置 `OPENSSL_BIN` 和 `CC`。Windows 还需设置 `OPENSSL_HOME` 指向包含 `include/openssl` 和 `bin/libcrypto-3-x64.dll` 的开发目录，并把该 `bin` 与 GCC 的 `bin` 加入当前进程 PATH。按实际环境设置 `OPENSSL_CONF` 指向正确配置文件。

`TEMP_WORK_ROOT` 可以指定已存在的临时目录。本次使用 `C:\Users\z8319\AppData\Local\Temp\opencode`。默认使用 `evidence` 下的随机临时子目录，结束时清理测试私钥及可执行文件。重跑将更新本周实验日志与公开验证数据。

本次最终环境是 OpenSSL 3.6.5、GCC 11.5.0、Windows x64。当前便携环境中，部分命令错误栈还含可选 `ZLIB1.dll` 加载提示；正常签名验签仍成功。报告中的预期验签失败由具体 RSA 错误和控制变量复现确认，完整错误栈已保留。

## 独立验证已保存材料

在 `evidence` 目录执行：

```bash
openssl dgst -sha256 -verify public.pem -sigopt rsa_padding_mode:pss -sigopt rsa_pss_saltlen:32 -sigopt rsa_mgf1_md:sha256 -signature pss1.bin message.txt
openssl dgst -sha256 -verify public.pem -sigopt rsa_padding_mode:pss -sigopt rsa_pss_saltlen:32 -sigopt rsa_mgf1_md:sha256 -signature c-signature.bin message.txt
```

两条命令均应输出 `Verified OK`。将消息换成 `crlf.txt` 或 `tampered.txt` 应失败。

## PDF 检查与重新导出

本次 PDF 共 11 页，已提取全文检查六部分与提交说明，逐页渲染并检查中文、表格、命令和导图。页面预览、总览图和检查结果位于 `evidence/pdf-page-*.png`、`pdf-contact-sheet.png`、`pdf-check.json`。

安装 Markdown、Pillow、PyMuPDF，并具备本机 `cryptosystem-report` Skill 与 Edge 时，可执行：

```bash
python code/render_report.py
```

`CRYPTO_REPORT_SKILL` 可指定 Skill 目录，`EDGE_PATH` 可指定 Edge 可执行文件。正文 Mermaid 源码和 `assets/week5-mindmap.mmd` 必须同步修改；脚本会校对一致性。
