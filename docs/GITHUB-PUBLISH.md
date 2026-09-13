# 将此包发布为新的公开仓库

本说明不表示远程仓库已经存在。发布脚本的**线上创建和推送路径未在本次制作环境实测**；离线预检、路径/哈希检查和输入验证已测试。

## 所需环境
Python 3.10+、Git、GitHub CLI；GitHub账户具备创建公开个人仓库的权限。脚本只支持“登录账户就是owner”的个人仓库情形，不自动切换账号，也不处理组织授权。

先审阅根目录README、LICENSE、源文件清单及合成示例，确认这些内容可以公开。不要把真实论文、未公开方法、访问令牌、邮件地址列表或审稿材料加入清单。

在你自己的终端使用GitHub CLI完成认证；不要把token发送给AI。基础登录命令如下，后续根据CLI提示选择浏览器认证：

```bash
gh auth login
gh auth status
```

## 推荐发布方式

在解压后的 `visio-academic-diagrams` 根目录执行，替换 `YOUR_GITHUB_LOGIN` 为自己的登录名：

```bash
python scripts/publish_github.py --owner YOUR_GITHUB_LOGIN --repo visio-academic-diagrams
```

这是默认演练：不会联网，不建仓，不上传。它检查技能文件与manifest，并显示目标名和拟发布文件数量。

确认公开内容后执行：

```bash
python scripts/publish_github.py --owner YOUR_GITHUB_LOGIN --repo visio-academic-diagrams --public --execute
```

脚本在本机通过 `gh api user`核对账户，复制manifest中的文件到全新的临时目录，建立main提交，然后调用官方支持的`gh repo create ... --public --source ... --push`。[A03]
不会对已有工作区做`git add`，不会把旁边的论文夹一起推送。临时目录的提交作者使用当前GitHub账户对应的noreply地址，不使用系统全局git身份配置。

只有确认返回的`isPrivate=false`且远程main的SHA与本地提交一致，才显示“PUBLISHED AND VERIFIED”和真实仓库链接。没有这条成功输出，就不能宣称已经完成发布。

## 失败处理
同名仓库存在：创建会失败，脚本不会继续向该仓库推送。选择新名称或人工检查现有仓库，不使用force-push。
登录账户不符：在认证层切换到目标账户后再运行；脚本不自动替你切换。
远程建仓成功但推送失败：可能留下空仓库。脚本会明确提示可能的部分状态，不擅自删除，也不重用它。请在GitHub检查后处理。
哈希失配：意味着文件变过或不完整。维护者按下文重新审查发布清单，不绕过检查。
没有GitHub写权限：仍可使用本地Skill。只能读取GitHub的AI连接无法把“读到账号”变成“已经上传”。

## 维护者更新发布清单
`manifest.sha256`也是发布白名单。新增/删除文件先经过代码和隐私审查，再以明确的相对路径更新清单，**不要对科研工作目录无差别递归纳入**。

重算现有清单项示例（不自动添加新文件）：

```python
from pathlib import Path
import hashlib
root = Path.cwd()
manifest = root / "manifest.sha256"
paths = [line.split("  ", 1)[1] for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
for rel in paths:
    target = (root / rel).resolve()
    if not target.is_relative_to(root.resolve()) or not target.is_file():
        raise ValueError(f"Invalid path: {rel}")
manifest.write_text("\n".join(hashlib.sha256((root / rel).read_bytes()).hexdigest() + "  " + rel for rel in paths) + "\n", encoding="utf-8")
```

然后重跑测试和`validate_package.py`，再以`build_release.py --output`构建新名字的ZIP。哈希只检测清单内部的一致性，不是作者身份的数字签名，也不能证明文件安全。

[A03]的官方CLI创建仓库文档见[来源登记](../references/source-register.md)。本项目脚本不创建GitHub Release、不配置域名、不安装插件；公开仓库与这些事情是不同操作。
