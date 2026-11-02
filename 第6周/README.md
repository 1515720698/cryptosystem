# 第六周预习作业交付清单

## 提交文件

- `20241328蔡贸俊《密码系统设计》.md`
- `20241328蔡贸俊《密码系统设计》第6周.pdf`（10 页）
- `assets/week6-mindmap.png`：实际渲染的思维导图，随 Markdown 保留。
- `assets/week6-mindmap.mmd`：独立 Mermaid 源码。

## 附件与核验

- `code/verify_cryptoapi.py`：Windows 原生 CryptoAPI 验证，无第三方依赖；运行 `python code/verify_cryptoapi.py`。
- `code/render_delivery.py`：本机渲染脚本，依赖全局 cryptosystem-report Skill、Markdown、Pillow、PyMuPDF 和 Edge；跨机器使用时需调整 Skill 与 Python 依赖路径。
- `evidence/experiment-log.txt`：实际运行结果，包含系统版本、调用参数、缓冲区错误、三项摘要交叉核对、类型不匹配及清理结果。
- `evidence/pdf-page-*.png`、`pdf-contact-sheet.png`、`pdf-text-check.txt`：PDF 分页、总览和文本核对资料。

## 要求对应

| 要求 | 报告位置 | 核验依据 |
| --- | --- | --- |
| 第 9 章学习总结 | 第一部分，覆盖 9.1—9.9 | 教材公开目录与微软官方资料 |
| 反思与补充 | 第二部分 | 四项问题及四项补充，供本人核对 |
| Mermaid 代码与图片 | 第三部分 | mmd 与 PNG，PDF 已嵌入图片 |
| 至少两个概念的苏格拉底问答 | 第四部分 | 两组学习示例，需本人作答或核对 |
| 至少两个问题及解决过程 | 第五部分 | 两个可控复现案例、一个实际脚本问题 |
| 命名和提交形式 | 文末提交说明 | 学号姓名、Markdown、中文 PDF |

## 使用说明

本稿参考 GitHub 仓库第五周作业结构教材依据为公开目录与官方接口资料，未获取付费章节全文。实践已在当前 Windows 环境实际执行并通过，PDF 已完成文本、图片及页面总览检查。

交付位置：`D:\学习资料\信息安全系统设计\第6周`。
