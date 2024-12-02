from flask import Flask, request, jsonify, render_template
import re

app = Flask(__name__, template_folder='templates', static_folder='static')

def parse_times(available_times):
    times = {}
    lines = available_times.strip().split('\n')  # 按行分割
    for line in lines:
        line = line.strip()
        match = re.match(r'^(\w+):\s*([\d:]+)-([\d:]+)$', line)
        if match:
            name = match.group(1)
            start_time = match.group(2)
            end_time = match.group(3)
            times.setdefault(name, []).append((start_time, end_time))
            print(f"Parsed time range for {name}: {start_time} - {end_time}")  # 调试信息
        else:
            print(f"Failed to parse line: {line}")  # 调试信息
    print(f"Parsed times: {times}")  # 调试信息
    return times

def find_best_time(times):
    time_slots = {}
    for name, slots in times.items():
        for start, end in slots:
            if start not in time_slots:
                time_slots[start] = 0
            if end not in time_slots:
                time_slots[end] = 0
            time_slots[start] += 1
            time_slots[end] -= 1
    
    current_count = 0
    max_count = 0
    best_start = None
    best_end = None
    for time, count in sorted(time_slots.items()):
        current_count += count
        print(f"Time: {time}, Count: {count}, Current Count: {current_count}")  # 调试信息
        if current_count > max_count:
            max_count = current_count
            best_start = time
        elif current_count < max_count and best_start is not None:
            best_end = time
            break
    
    if best_start is None or best_end is None:
        return "无合适时间"
    return f"{best_start}-{best_end}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/schedule', methods=['POST'])
def schedule_meeting():
    data = request.json
    participants = data.get('participants', '')
    available_times = data.get('availableTimes', '')
    
    times = parse_times(available_times)
    best_time = find_best_time(times)
    
    return jsonify({'bestTime': best_time})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
