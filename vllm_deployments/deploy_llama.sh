cd /home/srmdadmin/LLM_Inference/vLLM_dep
source myenv/bin/activate
vllm serve meta-llama/Llama-3.1-8B-Instruct --quantization bitsandbytes --load-format bitsandbytes --max-model-len 50000 > deployment.log 2>&1 &
