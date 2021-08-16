此程序用于将电子白板维护手册导出为用于印刷的 PDF 版本。

# 使用
首先请安装好以下软件：

- Python 3
- pip 3
- GTK+（对于 Windows 用户，请使用 [GTK+ for Windows Runtime Environment Installer](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases)

然后 clone 本仓库，以及 [维护手册的内容仓库](https://github.com/su-gzno3ms/tech-guide) 。

进入本仓库根目录，打开终端，运行 `pip3 install -r requirements.txt` 安装所需的依赖。（Windows 用户可能需要将 `pip3` 替换成 `pip`）

然后，在终端中执行 `python3 export.py path/to/tech-guide`，（参数 `path/to/tech-guide` 需替换为内容仓库的路径）即可开始导出。得到的文件为仓库根目录下的 `result.pdf`.（Windows 用户可能需要将 `python3` 替换成 `python`）

# 版权
本项目使用 MIT 协议。在分发，重用本项目的任何部分时，都请遵循该协议。

# 鸣谢
- [MkDocs](https://www.mkdocs.org/), 使用 2-clause BSD 协议授权。
- [MkPDFs for MkDocs](https://comwes.github.io/mkpdfs-mkdocs-plugin/), 使用 GPL 3.0 协议授权。
- [思源宋体](https://source.typekit.com/source-han-serif/cn/)，使用 SIL 协议授权。
- [Fira Sans](https://mozilla.github.io/Fira/), 使用 SIL 协议授权。