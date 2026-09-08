# local-docs-assistant-windows-mvp

Minimal Local Document Assistant (Windows MVP)

这是一个最小可运行示例：使用 FastAPI + llama.cpp (llama-cpp-python) + Chroma + sentence-transformers 在本地（CPU 路径）实现文档摄取（PDF/DOCX）、向量化检索（RAG）与问答接口。适合在 Windows/WSL2 上快速试验和迭代。

重要说明
- 本示例使用本地模型（gguf/ggml 格式）通过 llama.cpp 推理。你需要手动下载模型并放到 models/ 目录下，模型通常较大且受许可证约束，请先确认并接受模型许可。
- 在原生 Windows 上运行可能性能受限，推荐在 WSL2 (Ubuntu) 下运行以获得更稳定的依赖兼容性。

目录结构
- main.py — FastAPI 服务（/ingest, /query）
- requirements.txt — Python 依赖
- run_local.ps1 — 在 Windows/PowerShell 下的快速运行脚本
- download_model.ps1 — 模型下载示例脚本（模板）
- examples/curl_examples.md — ingest 与 query 的 curl 示例
- models/ — 放置模型文件（你需要手动放置）

快速开始（PowerShell）
1. 克隆仓库：
   git clone https://github.com/ZHANG9509/local-docs-assistant-windows-mvp
   cd local-docs-assistant-windows-mvp

2. 创建并激活虚拟环境：
   python -m venv venv
   .\venv\Scripts\Activate.ps1

3. 安装依赖：
   pip install -r requirements.txt

4. 放置模型文件：
   - 手动下载一个与 llama.cpp / llama-cpp-python 兼容的量化 gguf/ggml 模型（例如 7B 量化模型），并把模型文件放到 models/model.gguf
   - 注意模型许可

5. 运行服务：
   python main.py
   打开浏览器访问 http://localhost:8000/docs 进行 API 测试

常见问题
- 模型为什么要手动下载？很多模型需要在 Hugging Face 等平台上手动同意许可或使用 token 下载，本仓库不会自动分发模型。
- CPU 上会很慢吗？相较于 GPU，CPU 推理延迟明显更高。对于小规模试验（7B 量化）通常可用，但延迟可能在数秒到几十秒不等。

下一步
- 如果你有 NVIDIA GPU，我可以把仓库扩展为在 WSL2 + CUDA 下使用 vLLM/TGI 的版本，并提供 Docker Compose。