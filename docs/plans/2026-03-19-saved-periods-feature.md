# 时间段保存功能设计方案

## 需求概述

**目标**：实现时间段保存和加载功能，减少用户重复输入日期的操作

**用户场景**：
1. 用户配置好一个时间段（如农历 2025-01-01 到 2026-01-01）
2. 点击"保存"按钮，使用线条名称（如"线条 1"）作为默认名称
3. 允许用户自定义名称
4. 下次使用时，点击"加载已保存"下拉菜单，选择记录自动添加

**技术选型**：后端数据库存储（方案 B）

---

## 功能设计

### 1. 数据分离存储
- **农历时间段**：单独列表存储
- **公历时间段**：单独列表存储
- **最大数量**：每种类型最多 20 条

### 2. 保存流程
```
用户输入日期 → 点击保存按钮 → 弹出名称输入框（默认线条名称） → 
验证数据 → 调用后端 API → 保存到数据库 → 显示成功提示
```

### 3. 加载流程
```
点击"加载已保存"下拉按钮 → 读取对应类型的已保存列表 → 
显示下拉菜单 → 点击记录 → 自动添加到时间段列表
```

### 4. UI 交互（简洁版）
- 每个时间段行添加"保存"按钮
- "添加时间段"按钮改为下拉菜单：
  - 添加时间段（原功能）
  - 加载已保存（下拉子菜单）

---

## 技术架构

### 后端设计

#### 数据库表结构

**表 1：saved_lunar_periods（农历时间段）**
```sql
CREATE TABLE saved_lunar_periods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,
    start_date VARCHAR(10) NOT NULL,  -- 农历格式：2025-01-01
    end_date VARCHAR(10) NOT NULL,    -- 农历格式：2026-01-01
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**表 2：saved_solar_periods（公历时间段）**
```sql
CREATE TABLE saved_solar_periods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,
    start_date VARCHAR(10) NOT NULL,  -- 公历格式：2025-01-01
    end_date VARCHAR(10) NOT NULL,    -- 公历格式：2026-01-01
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### API 接口设计

**1. 获取已保存列表**
```http
GET /api/saved-periods?type=lunar
GET /api/saved-periods?type=solar

Response:
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "线条 1",
      "start_date": "2025-01-01",
      "end_date": "2026-01-01",
      "created_at": "2026-03-19T10:00:00Z"
    }
  ]
}
```

**2. 保存时间段**
```http
POST /api/saved-periods

Request:
{
  "type": "lunar",  // 或 "solar"
  "name": "线条 1",
  "start_date": "2025-01-01",
  "end_date": "2026-01-01"
}

Response:
{
  "success": true,
  "data": {
    "id": 1,
    "name": "线条 1",
    "start_date": "2025-01-01",
    "end_date": "2026-01-01"
  },
  "message": "保存成功"
}
```

**3. 删除时间段**
```http
DELETE /api/saved-periods/{id}?type=lunar

Response:
{
  "success": true,
  "message": "删除成功"
}
```

**4. 更新时间段名称**
```http
PUT /api/saved-periods/{id}

Request:
{
  "name": "自定义名称"
}

Response:
{
  "success": true,
  "data": {
    "id": 1,
    "name": "自定义名称"
  }
}
```

### 前端设计

#### 组件结构

**修改文件**：
- `frontend/src/views/ChartView.vue` - 主页面，添加保存和加载功能
- `frontend/src/api/periods.js` - 新建 API 调用模块

#### UI 组件

**1. 保存按钮**
```vue
<el-button size="small" @click="showSaveDialog(index)">
  <el-icon><Folder /></el-icon>
  保存
</el-button>
```

**2. 加载下拉菜单**
```vue
<el-dropdown @command="handleAddCommand">
  <el-button type="primary" size="small">
    添加时间段<el-icon class="el-icon--right"><ArrowDown /></el-icon>
  </el-button>
  <template #dropdown>
    <el-dropdown-menu>
      <el-dropdown-item command="new">
        <el-icon><Plus /></el-icon>
        添加时间段
      </el-dropdown-item>
      <el-dropdown-item divided disabled>
        加载已保存
      </el-dropdown-item>
      <el-dropdown-item 
        v-for="period in savedPeriods" 
        :key="period.id"
        :command="period"
      >
        {{ period.name }} ({{ period.start_date }} ~ {{ period.end_date }})
      </el-dropdown-item>
    </el-dropdown-menu>
  </template>
</el-dropdown>
```

**3. 保存对话框**
```vue
<el-dialog v-model="saveDialogVisible" title="保存时间段" width="400px">
  <el-form :model="saveForm">
    <el-form-item label="名称">
      <el-input v-model="saveForm.name" placeholder="使用线条名称" />
    </el-form-item>
    <el-form-item label="时间段">
      <span>{{ saveForm.start }} 至 {{ saveForm.end }}</span>
    </el-form-item>
  </el-form>
  <template #footer>
    <el-button @click="saveDialogVisible = false">取消</el-button>
    <el-button type="primary" @click="confirmSave">保存</el-button>
  </template>
</el-dialog>
```

---

## 数据验证

### 前端验证
1. 开始日期和结束日期不能为空
2. 开始日期不能晚于结束日期
3. 名称不能为空（默认使用线条名称）
4. 检查是否超过 20 条限制

### 后端验证
1. 数据类型验证（lunar/solar）
2. 日期格式验证
3. 数量限制检查（最多 20 条）
4. 名称长度限制（最多 50 字符）

---

## 错误处理

### 前端错误提示
```javascript
// 保存成功
ElMessage.success('保存成功')

// 保存失败
ElMessage.error('保存失败：已超过最大数量限制（20 条）')

// 加载失败
ElMessage.error('加载已保存时间段失败')

// 删除失败
ElMessage.error('删除失败')
```

### 后端错误响应
```javascript
// 超过数量限制
{
  "success": false,
  "error": "PERIOD_LIMIT_EXCEEDED",
  "message": "已超过最大保存数量（20 条）"
}

// 日期格式错误
{
  "success": false,
  "error": "INVALID_DATE_FORMAT",
  "message": "日期格式错误，请使用 YYYY-MM-DD 格式"
}

// 名称为空
{
  "success": false,
  "error": "NAME_REQUIRED",
  "message": "名称不能为空"
}
```

---

## 测试计划

### 后端测试
1. **数据库迁移测试**
   - 创建表结构
   - 验证索引

2. **API 接口测试**
   - GET /api/saved-periods - 获取列表
   - POST /api/saved-periods - 保存
   - DELETE /api/saved-periods/{id} - 删除
   - PUT /api/saved-periods/{id} - 更新

3. **边界条件测试**
   - 保存第 20 条（成功）
   - 保存第 21 条（失败）
   - 日期格式验证
   - 名称长度验证

### 前端测试
1. **UI 交互测试**
   - 点击保存按钮弹出对话框
   - 默认名称正确显示
   - 自定义名称输入
   - 下拉菜单加载记录

2. **功能测试**
   - 保存到数据库
   - 加载已保存记录
   - 删除记录
   - 农历/公历分开显示

3. **错误处理测试**
   - 网络错误提示
   - 超过数量限制提示
   - 日期验证提示

---

## 实现步骤

### 阶段 1：后端开发
1. 创建数据库迁移脚本
2. 实现 API 接口
3. 编写后端测试
4. 部署测试

### 阶段 2：前端开发
1. 创建 API 调用模块
2. 修改 ChartView 添加保存功能
3. 添加加载下拉菜单
4. 实现保存对话框
5. 编写前端测试

### 阶段 3：集成测试
1. 端到端测试
2. 性能测试
3. 用户验收测试

---

## 文件清单

### 后端文件
- `backend/app/models/period.py` - 新建：数据模型
- `backend/app/api/periods.py` - 新建：API 路由
- `backend/app/schemas/period.py` - 新建：数据验证 Schema
- `backend/app/main.py` - 修改：注册路由
- `backend/tests/test_periods.py` - 新建：测试文件

### 前端文件
- `frontend/src/api/periods.js` - 新建：API 调用
- `frontend/src/views/ChartView.vue` - 修改：添加保存和加载功能
- `frontend/src/components/SavePeriodDialog.vue` - 可选：保存对话框组件

---

## 时间估算

- **后端开发**：2-3 小时
- **前端开发**：3-4 小时
- **测试**：1-2 小时
- **总计**：6-9 小时

---

## 后续优化

### 短期优化
1. 添加编辑功能（完整版 UI）
2. 支持拖拽排序
3. 添加搜索功能

### 长期优化
1. 支持时间段分类标签
2. 支持导入导出
3. 支持分享时间段
4. 统计分析常用时间段

---

## 风险评估

### 技术风险
- **低**：后端数据库操作简单
- **低**：前端 UI 组件成熟

### 用户体验风险
- **低**：简洁版 UI 易于理解
- **中**：需要教育用户使用保存功能

### 缓解措施
1. 添加使用提示
2. 提供默认示例
3. 收集用户反馈快速迭代
