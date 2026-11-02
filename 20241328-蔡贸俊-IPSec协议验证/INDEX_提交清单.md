# 提交清单

主要提交文件：

- `20241328-蔡贸俊-IPSec协议验证.md`
- `20241328-蔡贸俊-IPSec协议验证.pdf`

报告同时覆盖 79 分必做项与 20 分 OpenSSL 加分项；评分以教师评阅为准。

辅助材料保留在 `src/`、`data/`、`logs/`、`images/`、`references/`。直接阅读 PDF 即可查看正文及原始窗口截图。上传 Markdown 时保留其相对图片目录。

## 实际验证范围

已完成附件工具 20 项运算、OpenSSL 26 项检查。输入来自题目链接实际显示的 61 页 PPT。未获取原始抓包和原始私钥文件；未读取视频；未实施实际 VPN 网络隧道与 ESP 数据面验证。报告已准确说明这些边界。

## 最短复现

设置 OPENSSL_EXE 后，用可用 Python 3 执行：

```powershell
python src/verify_openssl.py
```
