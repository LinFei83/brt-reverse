# 心率带实时监测系统

基于蓝牙心率带的实时数据采集与网页可视化系统。

## 功能特性

- 实时心电图（ECG）数据采集与可视化
- 三轴加速度数据监测
- 心率（HR）和心率变异性（HRV）分析
- 支持三种工作模式切换：Sport / ECG / HRV
- 现代化网页界面，实时数据流展示
- WebSocket 实时数据推送

## 技术架构

### 后端
- **FastAPI**: REST API 和 WebSocket 服务
- **Bleak**: 蓝牙低功耗设备通信
- **Asyncio**: 异步数据采集

### 前端
- **原生 JavaScript**: 无框架依赖
- **Chart.js**: 实时图表渲染
- **WebSocket**: 实时数据流

## 项目结构

```
hrm-web/
├── backend/                    # 后端服务
│   ├── core/                   # 核心模块
│   │   ├── device.py          # 设备管理器
│   │   ├── protocol.py        # 协议解析器
│   │   └── models.py          # 数据模型
│   ├── parsers/               # 数据解析器
│   │   ├── ecg.py
│   │   ├── gsensor.py
│   │   ├── realtime.py
│   │   └── sport_model.py
│   ├── api/                   # API 路由
│   │   ├── routes.py          # REST 端点
│   │   └── websocket.py       # WebSocket 处理
│   ├── config.py              # 配置管理
│   └── main.py                # 应用入口
├── frontend/                   # 前端界面
│   ├── index.html             # 主页面
│   ├── css/
│   │   └── style.css          # 样式
│   └── js/
│       ├── app.js             # 应用逻辑
│       ├── charts.js          # 图表管理
│       └── websocket.js       # WebSocket 客户端
├── requirements.txt            # Python 依赖
└── README.md                   # 项目文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置设备

编辑 `backend/config.py`，设置你的设备地址：

```python
DEVICE_ADDRESS = "EB:2D:1F:42:EF:4D"
```

### 3. 启动后端服务

```bash
python run.py
```

或使用 uvicorn 直接启动：

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

服务将在 `http://localhost:8000` 启动

### 4. 打开网页界面

在浏览器中访问：`http://localhost:8000`

## API 端点

### REST API

- `GET /api/status` - 获取设备连接状态
- `POST /api/connect` - 连接设备
- `POST /api/disconnect` - 断开连接
- `POST /api/mode` - 切换工作模式
  ```json
  {"mode": "sport|ecg|hrv"}
  ```
- `GET /api/mode` - 获取当前模式

### WebSocket

- `ws://localhost:8000/ws` - 实时数据流
  - 推送 ECG、加速度、心率等实时数据

## 数据格式

### 心电数据（ECG）
```json
{
  "type": "ECG",
  "timestamp": 1234567890,
  "data": {
    "id": 0,
    "uid": 1,
    "ecg": [10000.5, 10001.2, ...]
  }
}
```

### 加速度数据（GSensor）
```json
{
  "type": "GSensor",
  "timestamp": 1234567890,
  "data": {
    "x1": 100, "y1": 200, "z1": 300,
    "x2": 150, "y2": 250, "z2": 350
  }
}
```

### 心率数据（HR）
```json
{
  "type": "HR",
  "timestamp": 1234567890,
  "data": {
    "heart_rate": 75.5,
    "cadence": 120,
    "steps": 1000
  }
}
```

## 设备模式

| 模式  | ECG | SR  | XO  | 描述                               |
| ----- | --- | --- | --- | ---------------------------------- |
| Sport | 0   | 0   | 0   | 运动模式，主要采集加速度和基础心率 |
| ECG   | 1   | 0   | 1   | 心电模式，高精度心电图采集         |
| HRV   | 0   | 1   | 1   | 心率变异性模式，R-R 间期分析       |

## 开发说明

### 添加新的数据解析器

在 `backend/parsers/` 目录下创建新的解析器类，继承基础解析器接口。

### 自定义前端图表

修改 `frontend/js/charts.js` 中的 Chart.js 配置。

## 许可证

MIT
