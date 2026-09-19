# 硅谷甄选后端镜像：FastAPI + uvicorn
# 构建上下文 = 本目录（eastern-shopping-backhand）
FROM python:3.12-slim

# 时区设为东八区：容器默认 UTC，会导致日志时间、按日期归档等相差 8 小时
ENV TZ=Asia/Shanghai
RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 先单独装依赖，利用镜像层缓存：requirements.txt 没变时跳过重装
# 国内服务器用阿里云 PyPI 镜像加速；海外服务器可删掉 -i 之后的参数
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 拷贝项目代码（.env、static/、logs/ 等已由 .dockerignore 排除）
COPY . .

EXPOSE 8000

# 必须以 /app 为工作目录启动：static/、logs/ 都是相对项目根的路径
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
