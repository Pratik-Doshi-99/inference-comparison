cd /home/srmdadmin/LLM_Inference/vLLM_dep
source myenv/bin/activate
vllm serve Qwen/Qwen2.5-7B-Instruct --quantization "fp8"
