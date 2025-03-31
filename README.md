# mySudokuSolver

一个用python实现的数独求解器

A sudoku solver implemented by python

## 安装依赖 Install dependencies

可以使用 `conda` 或 `pip` 中的任意一种

### 1. 用 conda 安装 (推荐)

```bash
conda env create -f environment.yml
conda activate mySudokuSolver_env
```

### 2. 用 pip 安装

Make sure `python>=3.11`

#### 使用 venv (可选)

```bash
python -m venv venv
venv\Scripts\activate # Windows
# source venv/bin/activate # Linux/macOS 
```

#### 安装依赖

```bash
pip install -r requirements.txt
```

## Quick start

Run in the root directory of this project:

```bash
python -m src
```

你可以修改 `src/config.py` 中的 `CONFIG_PUZZLE_BOARD` 和 `CONFIG_CONSTRAINTS` 这两个常量，它们分别代表了app启动时使用的背景谜题Puzzle和外加限制规则Constraints列表。