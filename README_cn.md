## zeus 使用说明 


### 接口说明 

#### 创建 Job 

```bash
json_data=```
{
    "data_source": {
        "url": "http://40.125.162.12:38175"
    },
    "model": "iForest",
    "metrics": ["qps"],
    "slack_channel": "#schordinger-alert", 
    "timeout": "24h"
}```

curl -H "Content-Type: application/json" \
    -X POST \
    -d "${json_data}" \
http://127.0.0.1:2333/api/v1/job/new
```

支持的 models: iForest               
支持的 metrics: qps / latency / server_is_busy / channel_full 

#### 删除正在运行 Job 

```bash
curl http://127.0.0.1:2333/api/v1/job/{id}/delete
```

#### 列出所有正在运行 Job 

```bash
cul http://127.0.0.1:2333/api/v1/jobs/list 
```

#### 查找一个正常运行 Job 的详情 

```bash
curl http://127.0.0.1:2333/api/v1/job/{id}/detail
```

