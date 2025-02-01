cd /home/srmdadmin/LLM_Inference/vLLM_dep
source myenv/bin/activate
#vllm serve deepseek-ai/DeepSeek-R1-Distill-Llama-8B --quantization bitsandbytes --load-format bitsandbytes --max-model-len 50000 > deployment_deepseek.log 2>&1 &
#vllm serve deepseek-ai/DeepSeek-V3 --quantization "fp8" --max-model-len 50000 --trust-remote-code   =>  Out of memory
#vllm serve deepseek-ai/deepseek-llm-7b-base --quantization "fp8" --trust-remote-code      => no chat format, nor any chat finetuning
#vllm serve deepseek-ai/deepseek-llm-7b-chat --quantization "fp8" --trust-remote-code      => context length too small: 4096
#vllm serve deepseek-ai/DeepSeek-V2-Lite-Chat --quantization "fp8" --trust-remote-code     => Out of memory
