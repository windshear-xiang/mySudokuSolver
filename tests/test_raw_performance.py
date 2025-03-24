import numpy as np
import pandas as pd
import sys
import pytest
from src.solver import Sudoku


def convert_to_matrix(sudoku_str):
    """使用 numpy 将 81 位数独字符串转换为 9x9 numpy 数组"""
    return np.array(list(sudoku_str), dtype=np.int8).reshape(9, 9)

@pytest.mark.parametrize("data_set, max_num_rows", [
    ("easy", 500),
    ("mid", 500),
    ("hard", 300),
    ("zbrSuperhard", 200),
    ("hardest", 100)
])
def test_performance(data_set, max_num_rows):
    # 读取数独数据
    test_df = pd.read_csv(f"./tests/test_data/{data_set}.csv", nrows=max_num_rows)

    # 将 puzzle 和 solution 列转换为 9×9 矩阵
    test_df["puzzle_matrix"] = test_df["puzzle"].apply(convert_to_matrix) # type: ignore
    has_solution = "solution" in test_df.columns
    if has_solution:
        test_df["solution_matrix"] = test_df["solution"].apply(convert_to_matrix) # type: ignore

    print(f"has_solution={has_solution}")

    num_rows = len(test_df)
    if num_rows == 0:
        print("None.\n")
        return

    t_count = 0
    t_time = 0

    for index in range(num_rows):

        sys.stdout.flush()
        sys.stdout.write(f"\r{index+1} / {num_rows} ")

        row = test_df.iloc[index]
        puzzle = row["puzzle_matrix"]

        s = Sudoku(puzzle)
        Sudoku.reset_counter()
        ret = s.solve()
        c_count, c_time = Sudoku.get_counter_stat()
        t_count += c_count
        t_time += c_time

        assert ret is not None
        if has_solution:
            assert np.array_equal(ret.assigned_board, row["solution_matrix"])

    print()
    print(f"[per puzzle] {t_count/num_rows:.2f} searches; {t_time/num_rows*1000:.3f}ms")
    print(f"[per search] {t_time/t_count*1000:.4f}ms")
