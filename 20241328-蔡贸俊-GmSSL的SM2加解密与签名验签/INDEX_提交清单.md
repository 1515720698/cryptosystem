# 提交清单

## 必交

- `20241328-蔡贸俊-GmSSL的SM2加解密与签名验签.md`
- `20241328-蔡贸俊-GmSSL的SM2加解密与签名验签.pdf`
- `src/sm2_file.c`，也可提供报告中的 GitHub 代码链接。

## 支撑材料

- `任务要求.md`、`README.md`、`run.sh`。
- `sn.txt`、`sn2.txt`、`sn.enc`、`sn.sig`、`sm2_public.pem`。
- `logs/practice.txt`、`logs/negative-check.txt`、`logs/cross-check.txt`、`logs/results.json`。
- `logs/AI使用记录.md`：真实交流节录及辅助过程摘要，最后注明 AI 生成。
- `logs/block*.der`、`logs/block*.plain`、`logs/sn_cli.txt`、`logs/cli.sig`：交叉验证数据。
- `logs/sn_tampered.txt`、`logs/truncated.enc`：对照输入。

## 本地密钥与公开仓库

本地加密私钥位于 `private/sm2_private.pem`，不上传 GitHub。
原运行口令保存在 openEuler 的 `/root/.local/state/gmssl-sm2-20241328/password`，不进入本目录、日志或仓库。
常规复现直接执行 `bash run.sh` 生成新密钥，不依赖该状态文件。
公开仓库可利用现有公钥验证现有签名，也可自行生成新密钥重新运行全部核心操作。

## 验证结果

29 个唯一八位学号，本人最后；文件往返 diff=0；原文验签成功；篡改验签拒绝；截断解密拒绝；CLI 与 C 签名互验通过。
完整结果见 `logs/results.json`。
