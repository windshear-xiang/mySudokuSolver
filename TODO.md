# TODO

已经完成的和准备进行的事项

## git 工作流

```Bash
# 继续在 dev 分支上开发
git checkout dev
# 修改代码后提交
git add .
git commit -m "改进求解算法的性能优化"

# 新的功能开发稳定后合并到 main
git checkout main
git merge dev --no-ff
git push origin main
```

## 已完成

+ [x] 做4.0版本，还是先ipynb
  + [x] 改数据结构，重构代码
  + [x] 做一个性能比较器，可以做实验：留两个版本，做完之后看看速度有没有提升
  + [x] 看看如果不转换float会不会更大
  + [x] 使用slots优化
  + [x] settle和quick_drop都扫太多次全局了，改一些扫局部，看看会不会更快
    + 会更慢
  + [x] 加入unique_in_unit策略，注意要做成动态更新：在翻新的时候每次有变化的块，就减下去对应位置
  + [x] 调节constraints成为类属性，写solve
  + [x] 修空数独的bug
  + [x] 写solve candidates
  + [x] 把特殊规则做成缩减candidate：先预处理，然后在每次以及settle的时候，都会调用。
    + [x] 记忆化
    + [x] 缓存大小 微弱优化，就None吧
  + [x] 序数运算规则
  + [x] numba加速
    + 发现numba加速序数计算可以提高预处理速度，is_valid几乎没用，搜索不能加速
    + [x] 试试分离边界检测，没有区别，统一放在外面

## 进行中

+ [x] 迁移到工程版本
  + [x] 开新仓库，组织结构
  + [x] 写一个好测试
  + [x] 加入多种constraints
    + [x] 做测试
  + 核心代码用numba加速
    + [x] np.ascontiguousarray【放弃，太麻烦了】
    + [x] numba优化Ordinal，做成jitclass
      + [x] numba传列表的warning问题解决一下【只发生在预编译时】
    + [x] 用viztracer发现优化目标
      + [x] settle每次有一多半时间耗在最后的检查上，可以numba优化
      + [x] sum 和 argwhere 都很耗时，argmin特别快（但是需要搭配any，也慢），可以numba优化
      + deepcopy的耗时和一次settle差不多，可能有点大
      + [x] get_least_cands也差不多慢，可以numba优化
      + [x] quick_drop会多做很多次检查，优化逻辑
    + [x] constraints已经高度优化了，preprocess可以numba加速
  + [ ] 优先查unknown，或者随机化，避免卡死在无解情况
  + [ ] 修整一下DenseMulticellConstraints等等类里乱七八糟的对象，少用列表
    + [ ] 能否实现一个统一的numba优化的DenseMulticellConstraints的preprocess？
  + [ ] 多进程的solve_true_candidate
  + [ ] 做记忆化，如果已经知道了某种局面会无解，就不必再往下搜了？
  + [ ] 要不要用numba整个重写solve_step方法？
    + [ ] nogil优化，多线程并行
+ [ ] 完整功能GUI
  + [x] 临时显示的旧GUI加上
  + [ ] 手动设定数字的功能，再加上可以随时撤销
  + [ ] 手动设定constraints的功能