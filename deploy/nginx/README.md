# Windows Nginx 网关

网关监听 `8080`：`/` 提供 Vue 构建产物并处理路由刷新；`/api/` 代理到 Django 的 `127.0.0.1:8000`；`/media/` 从媒体目录读取文件，支持视频范围请求。

1. 按 [项目启动说明](../../README.md)启动 Django，并在 `frontend/` 执行 `npm run build`。
2. 将 `nginx.dev.windows.conf` 中的 `root` 与 `alias` 改成当前机器上 `frontend/dist` 和媒体目录的绝对路径；Windows 配置中使用正斜杠，路径含空格时保留引号。根据访问地址调整 `server_name` 和 Django 的 `ALLOWED_HOSTS`。
3. 将配置复制为 Nginx 安装目录下的 `conf/nginx.conf`，在该安装目录执行：

```powershell
.\nginx.exe -t
.\nginx.exe
```

配置变更后运行 `.\nginx.exe -t`，通过后运行 `.\nginx.exe -s reload`。访问 `http://127.0.0.1:8080/` 和 `http://127.0.0.1:8080/api/health/` 验证页面与接口；使用浏览器网络面板确认视频的有效范围请求返回 `206 Partial Content`。

校园网联调时，从同一网络访问 Nginx 主机的局域网 IP 和 8080 端口；如需让 Vite 使用该网关，将 `VITE_DEV_PROXY_TARGET` 设为网关地址。
