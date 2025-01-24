import asyncio
import aiohttp
import yaml
import time
import json
import csv
from datetime import datetime
from collections import defaultdict
from math import floor


def calculate_percentile(data, percentile):
    if not data:
        return 0
    sorted_data = sorted(data)
    index = (len(sorted_data) - 1) * percentile / 100
    floor_index = floor(index)
    if floor_index == index:
        return sorted_data[floor_index]
    lower = sorted_data[floor_index]
    upper = sorted_data[floor_index + 1]
    return lower + (upper - lower) * (index - floor_index)


def generate_report(metrics, duration):
    successful = [m for m in metrics if m['error'] is None]
    errors = len(metrics) - len(successful)
    
    print(f"\n{' Load Test Results ':=^60}")
    print(f"{'Total Requests:':<25} {len(metrics)}")
    print(f"{'Successful Requests:':<25} {len(successful)}")
    print(f"{'Failed Requests:':<25} {errors}")
    print(f"{'Test Duration:':<25} {duration:.2f}s")
    print(f"{'Requests/sec:':<25} {len(metrics)/duration:.2f}\n")
    
    if successful:
        ttfts = [m['ttft'] for m in successful if m['ttft'] is not None]
        throughputs = [m['throughput'] for m in successful]
        interlaten = [m['avg_inter_token'] for m in successful if m['avg_inter_token'] > 0]
        durations = [m['total_duration'] for m in successful]
        
        print(f"{' Time to First Token (TTFT) ':-^60}")
        print(f"{'Average:':<20} {sum(ttfts)/len(ttfts):.4f}s")
        print(f"{'95th %ile:':<20} {calculate_percentile(ttfts, 95):.4f}s")
        print(f"{'99th %ile:':<20} {calculate_percentile(ttfts, 99):.4f}s")
        
        print(f"\n{' Token Throughput ':-^60}")
        print(f"{'Average:':<20} {sum(throughputs)/len(throughputs):.2f} tokens/s")
        print(f"{'95th %ile:':<20} {calculate_percentile(throughputs, 95):.2f} tokens/s")
        
        print(f"\n{' Inter-Token Latency ':-^60}")
        print(f"{'Average:':<20} {sum(interlaten)/len(interlaten):.4f}s")
        print(f"{'95th %ile:':<20} {calculate_percentile(interlaten, 95):.4f}s")
        
        print(f"\n{' Request Duration ':-^60}")
        print(f"{'Average:':<20} {sum(durations)/len(durations):.4f}s")
        print(f"{'95th %ile:':<20} {calculate_percentile(durations, 95):.4f}s")
    
    if errors > 0:
        error_counts = defaultdict(int)
        for m in metrics:
            if m['error']:
                error_counts[m['error']] += 1
        
        print(f"\n{' Errors ':-^60}")
        for error, count in error_counts.items():
            print(f"{count}x {error}")


def log_prompt_responses(metrics):
    if not metrics:
        return
    
    filename = f"prompt_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
    print(f"[{datetime.now().isoformat()}] Saving prompt/response pairs to {filename}")
    
    with open(filename, 'w') as f:
        for metric in metrics:
            if metric['error'] is None:
                record = {
                    'timestamp': metric['timestamp'],
                    'datetime': datetime.fromtimestamp(metric['timestamp']).isoformat(),
                    'prompt': metric['prompt'],
                    'response': metric['response'],
                    'tokens': metric['tokens'],
                    'duration': metric['total_duration']
                }
                f.write(json.dumps(record) + '\n')


'''old code
# async def stream_processor(response, request_start, config):
#     server_type = config['server_type']
#     ttft = None
#     tokens = 0
#     previous_token_time = None
#     inter_token_latencies = []
    
#     try:
#         async for chunk in response.content.iter_any():
#             chunk_time = time.time()
            
#             try:
#                 decoded = chunk.decode().strip()
#                 if config.get('verbose', False):
#                     print(f"[{datetime.now().isoformat()}] Raw chunk: {decoded}")
                
#                 # Framework-specific parsing
#                 if server_type == 'triton':
#                     data = json.loads(decoded)
#                     token = data['outputs'][0]['data'][0]
#                 elif server_type == 'vllm':
#                     data = json.loads(decoded.lstrip('data: '))
#                     token = data['choices'][0]['text']
#                 elif server_type == 'tgi':
#                     data = json.loads(decoded)
#                     token = data['token']['text']
                
#                 tokens += 1
                
#             except (json.JSONDecodeError, KeyError) as e:
#                 if config.get('verbose', False):
#                     print(f"[{datetime.now().isoformat()}] Parsing error: {str(e)}")
#                 continue
            
#             if tokens == 1:
#                 ttft = chunk_time - request_start
#             else:
#                 inter_token_latencies.append(chunk_time - previous_token_time)
#             previous_token_time = chunk_time
            
#     except Exception as e:
#         error_msg = str(e)
#         print(f"[{datetime.now().isoformat()}] Response processing error: {error_msg}")
#         return ttft, tokens, inter_token_latencies, error_msg
    
#     return ttft, tokens, inter_token_latencies, None


# async def user_loop(session, requests, start_time, test_duration, metrics, metrics_lock, config):
#     current_idx = 0
#     user_id = id(session)
    
#     print(f"[{datetime.now().isoformat()}] User {user_id} started")
    
#     while time.time() - start_time < test_duration:
#         request_data = requests[current_idx % len(requests)]
#         current_idx += 1
        
#         metric = {
#             'timestamp': None,
#             'ttft': None,
#             'tokens': 0,
#             'throughput': 0,
#             'avg_inter_token': 0,
#             'total_duration': 0,
#             'error': None
#         }
        
#         request_start = time.time()
#         metric['timestamp'] = request_start
        
#         if config.get('verbose', False):
#             print(f"[{datetime.now().isoformat()}] User {user_id} sending request: {json.dumps(request_data)}")
        
#         try:
#             async with session.post(
#                 config['api_endpoint'],
#                 json=request_data,
#                 timeout=aiohttp.ClientTimeout(total=config.get('request_timeout', 300))
#             ) as response:
#                 ttft, tokens, latencies, error = await stream_processor(response, request_start, config)
                
#                 if error:
#                     metric['error'] = error
#                     print(f"[{datetime.now().isoformat()}] User {user_id} request error: {error}")
#                 else:
#                     metric['ttft'] = ttft
#                     metric['tokens'] = tokens
#                     metric['total_duration'] = time.time() - request_start
                    
#                     if tokens > 0:
#                         if tokens > 1:
#                             time_window = metric['total_duration'] - ttft
#                             metric['throughput'] = (tokens - 1) / time_window if time_window > 0 else 0
#                         metric['avg_inter_token'] = sum(latencies)/len(latencies) if latencies else 0
                    
#                     if config.get('verbose', False):
#                         print(f"[{datetime.now().isoformat()}] User {user_id} completed request in {metric['total_duration']:.2f}s")
                        
#         except Exception as e:
#             error_msg = str(e)
#             metric['error'] = error_msg
#             metric['total_duration'] = time.time() - request_start
#             print(f"[{datetime.now().isoformat()}] User {user_id} request failed: {error_msg}")
        
#         async with metrics_lock:
#             metrics.append(metric)
'''

async def stream_processor(response, request_start, config):
    server_type = config['server_type']
    ttft = None
    tokens = 0
    full_response = ""
    previous_token_time = None
    inter_token_latencies = []
    
    try:
        async for chunk in response.content.iter_any():
            chunk_time = time.time()
            
            try:
                decoded = chunk.decode().strip()
                if config.get('verbose', False):
                    print(f"[{datetime.now().isoformat()}] Raw chunk: {decoded}")
                
                # Framework-specific parsing
                if server_type == 'triton':
                    data = json.loads(decoded)
                    token = data['outputs'][0]['data'][0]
                elif server_type == 'vllm':
                    data = json.loads(decoded.lstrip('data: '))
                    token = data['choices'][0]['text']
                elif server_type == 'tgi':
                    data = json.loads(decoded)
                    token = data['token']['text']
                
                full_response += token
                tokens += 1
                
            except (json.JSONDecodeError, KeyError) as e:
                if config.get('verbose', False):
                    print(f"[{datetime.now().isoformat()}] Parsing error: {str(e)}")
                continue
            
            if tokens == 1:
                ttft = chunk_time - request_start
            else:
                inter_token_latencies.append(chunk_time - previous_token_time)
            previous_token_time = chunk_time
            
    except Exception as e:
        error_msg = str(e)
        print(f"[{datetime.now().isoformat()}] Response processing error: {error_msg}")
        return ttft, tokens, inter_token_latencies, error_msg, full_response
    
    return ttft, tokens, inter_token_latencies, None, full_response

async def user_loop(session, user_id, requests, start_time, test_duration, metrics, metrics_lock, config):
    start_idx = int(user_id / config['users'] * len(requests))
    #user_id = id(session)
    current_idx = start_idx
    end_idx = min(int((user_id + 1) / config['users'] * len(requests)), len(requests))
    print(f"[{datetime.now().isoformat()}] User {user_id} starting at {start_idx}")
    
    while time.time() - start_time < test_duration:
        if current_idx >= end_idx:
            current_idx = start_idx
        request_data = requests[current_idx]
        print(f'User {user_id} picking request #{current_idx}')
        # Extract prompt based on server type
        if config['server_type'] == 'triton':
            prompt = request_data['inputs'][0]['data'][0]
        elif config['server_type'] == 'vllm':
            prompt = request_data['prompt']
        elif config['server_type'] == 'tgi':
            prompt = request_data['inputs']
        
        metric = {
            'timestamp': None,
            'prompt': prompt,
            'response': None,
            'ttft': None,
            'tokens': 0,
            'throughput': 0,
            'avg_inter_token': 0,
            'total_duration': 0,
            'error': None
        }
        
        
        
        if config.get('verbose', False):
            print(f"[{datetime.now().isoformat()}] User {user_id} sending request: {json.dumps(request_data)}")
        
        try:
            async with session.post(
                config['api_endpoint'],
                json=request_data,
                timeout=aiohttp.ClientTimeout(total=config.get('request_timeout', 300))
            ) as response:
                request_start = time.time()
                metric['timestamp'] = request_start
                ttft, tokens, latencies, error, full_response = await stream_processor(response, request_start, config)
                metric['response'] = full_response
                
                if error:
                    metric['error'] = error
                    print(f"[{datetime.now().isoformat()}] User {user_id} request error: {error}")
                else:
                    metric['ttft'] = ttft
                    metric['tokens'] = tokens
                    metric['total_duration'] = time.time() - request_start
                    
                    if tokens > 0:
                        if tokens > 1:
                            time_window = metric['total_duration'] - ttft
                            metric['throughput'] = (tokens - 1) / time_window if time_window > 0 else 0
                        metric['avg_inter_token'] = sum(latencies)/len(latencies) if latencies else 0
                    
                    if config.get('verbose', False):
                        print(f"[{datetime.now().isoformat()}] User {user_id} completed request in {metric['total_duration']:.2f}s")
                        
        except Exception as e:
            error_msg = str(e)
            metric['error'] = error_msg
            metric['total_duration'] = time.time() - request_start
            print(f"[{datetime.now().isoformat()}] User {user_id} request failed: {error_msg}")
        
        async with metrics_lock:
            metrics.append(metric)
        current_idx += 1

def log_metrics(metrics):
    if not metrics:
        return
    
    filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    print(f"[{datetime.now().isoformat()}] Saving metrics to {filename}")
    
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = [
            'timestamp', 'datetime', 'ttft', 'tokens',
            'throughput', 'avg_inter_token', 'total_duration', 'error'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for metric in metrics:
            row = {
                'timestamp': metric['timestamp'],
                'datetime': datetime.fromtimestamp(metric['timestamp']).isoformat(),
                'ttft': metric['ttft'],
                'tokens': metric['tokens'],
                'throughput': metric['throughput'],
                'avg_inter_token': metric['avg_inter_token'],
                'total_duration': metric['total_duration'],
                'error': metric['error']
            }
            writer.writerow(row)

async def main(config):
    print(f"[{datetime.now().isoformat()}] Starting load test")
    print(f"[{datetime.now().isoformat()}] Configuration: {json.dumps(config, indent=2)}")
    
    with open(config['requests_file']) as f:
        requests = json.load(f)
    
    metrics = []
    metrics_lock = asyncio.Lock()
    start_time = time.time()
    end_time = start_time + config['duration']
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        print(f"[{datetime.now().isoformat()}] Spawning {config['users']} users over {config['ramp_up']}s")
        
        for user_id in range(config['users']):
            spawn_delay = (config['ramp_up'] / config['users']) * user_id
            await asyncio.sleep(spawn_delay)
            
            task = asyncio.create_task(
                user_loop(session, user_id, requests, start_time, config['duration'], metrics, metrics_lock, config)
            )
            tasks.append(task)
        
        print(f"[{datetime.now().isoformat()}] Load test running for {config['duration']}s")
        await asyncio.sleep(max(0, end_time - time.time()))
        
        print(f"[{datetime.now().isoformat()}] Stopping test")
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
    
    print(f"[{datetime.now().isoformat()}] Generating report")
    generate_report(metrics, config['duration'])
    log_metrics(metrics)
    log_prompt_responses(metrics)
    print(f"[{datetime.now().isoformat()}] Test complete")

# generate_report() and calculate_percentile() remain unchanged from previous version

if __name__ == "__main__":
    with open("/home/srmdadmin/LLM_Inference/tests/inference-comparison/configs/vllm.yaml") as f:
        config = yaml.safe_load(f)
    
    config.setdefault('verbose', False)
    asyncio.run(main(config))