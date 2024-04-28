from scapy.all import sniff, IP, Raw, conf
import threading
from queue import Queue
from threading import Event

last_map_id = None

current_map_id = None
map_id_queue = Queue()
current_pods_percentage = 0  
packet_received_event = Event()  
general_packet_received_event = Event()

def extract_numbers(raw_load):
    numbers = []
    start_index = raw_load.find(b'|') + 1
    end_index = raw_load.find(b'|', start_index)
    while start_index != -1 and end_index != -1:
        number = raw_load[start_index:end_index].decode('utf-8')
        numbers.append(number)
        start_index = raw_load.find(b'|', end_index + 1) + 1
        end_index = raw_load.find(b'|', start_index)
    return numbers

def extract_number_from_GDM(raw_load):
    start_index = raw_load.find(b'GDM|')
    if start_index != -1:
        start_index += 4  
        end_index = raw_load.find(b'|', start_index)
        if end_index != -1:
            number = raw_load[start_index:end_index].decode('utf-8')
            return number
    return None

def packet_handler(packet):
    global current_map_id
    if IP in packet and packet[IP].src == '172.65.255.133' and Raw in packet:
        if b'GA;2' in packet[Raw].load:
            numbers = extract_numbers(packet[Raw].load)
            for number in numbers:
                print("Map ID:", number)
                map_id_queue.put(number)  

        if b'GCK' in packet[Raw].load:
            number = extract_number_from_GDM(packet[Raw].load)
            if number:
                print("Extracted number:", number)

        custom_packet_callback(packet)  

def extract_parts(payload):
    parts = []
    payload_str = payload.decode('utf-8', errors='ignore')
    start_index = payload_str.find('\x00Ow')
    end_index = payload_str.find('\x00IQ')
    if start_index != -1 and end_index != -1:
        part = payload_str[start_index:end_index]
        last_pipe_index = part.rfind('|')
        if last_pipe_index != -1:
            part = part[:last_pipe_index]
        parts = part.split('|')
        if len(parts) >= 2:
            parts[0] = ''.join(filter(str.isdigit, parts[0]))
    return parts

def calculate_percentage(part1, part2):
    try:
        percentage = (int(part1) / int(part2)) * 100
        return percentage
    except ZeroDivisionError:
        return 0

def custom_packet_callback(packet):
    global current_pods_percentage
    if IP in packet and Raw in packet:
        payload = bytes(packet[Raw])
        if len(payload) > 60 and b'GDF|' in payload:
            extracted_parts = extract_parts(payload)
            if len(extracted_parts) >= 2:
                part1, part2 = extracted_parts
                current_pods_percentage = calculate_percentage(part1, part2)
                print("POD Utilisé:", part1)
                print("POD Max:", part2)
                print("Percentage:", current_pods_percentage, "%")

                general_packet_received_event.set()  

                if current_pods_percentage >= 90:
                    packet_received_event.set()

def start_sniffing():
    iface = conf.iface
    sniff(iface=iface, filter='ip', prn=packet_handler)