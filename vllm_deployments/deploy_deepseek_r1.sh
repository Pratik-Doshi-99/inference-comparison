cd /home/srmdadmin/LLM_Inference/vLLM_dep
source myenv/bin/activate
vllm serve deepseek-ai/DeepSeek-R1-Distill-Llama-8B --quantization bitsandbytes --load-format bitsandbytes --max-model-len 50000 > deployment_deepseek.log 2>&1 &
#vllm serve deepseek-ai/DeepSeek-R1-Distill-Llama-8B --quantization bitsandbytes --load-format bitsandbytes --max-model-len 50000
