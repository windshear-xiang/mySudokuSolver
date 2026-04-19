# mySudokuSolver

一个用python实现的数独求解器及可视化工具，专门为涉及超限序数运算的变体数独设计。

求解算法使用 回溯搜索 + 多种剪枝 + 变体规则预处理 + Numba JIT 加速。可视化 GUI 基于 tkinter。

A Sudoku solver and visualization implemented in Python, specifically designed for variant Sudokus involving transfinite ordinal arithmetic.

The solving algorithm utilizes: backtracking search + various pruning techniques + variant rule preprocessing + Numba JIT acceleration. The visualization GUI is based on tkinter.

## 安装依赖 Install dependencies

项目依赖 numpy, numba, pandas 等科学计算库。请确保 Python 版本 >= 3.11。可以使用 `conda` 或 `pip` 中的任意一种进行安装：

This project depends on libraries such as `numpy`, `numba`, and `pandas`. Please make sure your Python version >= 3.11. You can choose either `conda` or `pip` for installation:

### 1. 推荐用 conda 安装 Install via conda Recommended

```bash
conda env create -f environment.yml
conda activate mySudokuSolver_env
```

### 2. 用 pip 安装 Install via pip

注意需要 `python>=3.11`。建议在虚拟环境中进行安装以避免依赖冲突：

Note that python>=3.11 is required. It is recommended to install within a virtual environment to avoid dependency conflicts:

```bash
# Create and activate a virtual environment (optional)
python -m venv venv
# Windows: venv\Scripts\activate 
# Linux/macOS: source venv/bin/activate 

# Install dependencies
pip install -r requirements.txt
```

## 快速开始 Quick start

在项目根目录下运行以下命令启动带图形界面的应用：

Run the following command in the root directory of this project to launch the application with GUI:

```bash
python -m src
```

## 配置自定义数独题 Configure custom Sudoku puzzles

您可以直接修改 `src/config.py` 文件来设定启动时的默认题目与规则：

You can directly modify the src/config.py file to set the default puzzle and rules:

+ `CONFIG_PUZZLE_BOARD`:
  定义初始的数独盘面（9x9 二维数组，0 表示空格）。
  Defines the initial Sudoku board (a 9x9 2D array, where 0 represents an empty cell).

+ `CONFIG_CONSTRAINTS`: 
  传入实例化后的限制规则列表（如 `OrdArrowConstraint` 对象），以叠加各种复杂的变体数独规则。
  Accepts a list of instantiated constraint rules (such as OrdArrowConstraint objects) to superimpose various complex variant Sudoku rules.
