# 实验三（1–3 学时）提交清单

- [实践记录 Markdown](20241328_蔡贸俊_实验三_1-3学时_实践记录.md) · [实践记录 PDF](20241328_蔡贸俊_实验三_1-3学时_实践记录.pdf)
- [SKF 新增查询](skf/device_state.cpp) · [SDF 新增实现](sdf/src/device_info.c)
- [基线运行](logs/01-baseline.txt) · [SKF 验证](logs/02-skf-state.txt) · [SDF 验证](logs/03-sdf-info.txt) · [功能提交日志](logs/git-log.txt)
- [Windows 实体 SKF 补测](logs/04-skf-hardware.txt) · [补测脚本](tests/check-skf-windows.py)
- [厂商库获取说明](vendor/README.md)：本地交付已含 x64 运行库，克隆 Git 时需按说明单独提取。

在 openEuler x86_64 中进入本目录，运行：

```bash
make
bash tests/check-skf.sh
make build/test-sdf
./build/sdf-info
./build/test-sdf
```

`bash tests/baseline.sh` 可复现附件基线；它会运行原 SKF 示例并记录退出码，在本机已知会崩溃，不是正式验收入口。SKF 实体 UKey 已通过 Windows 查询，openEuler 实机待补测。个人课程项目的 Gitee/GitHub 链接待补，未向参考仓库推送。按本阶段要求交付实践 Markdown 与 PDF，不包含另行评分的完整实验三 `.doc` 报告。
