from scapy.all import *
import re
import time
import pyautogui
import subprocess
import sniffer

map_id_queue = sniffer.map_id_queue
general_packet_received_event = sniffer.general_packet_received_event

fight_mode = False
player_id = None
player_id_set = False
initial_coordinates_clicked = False
one_time_click_done = False

def click_coordinate(coordinate):
    x, y = map(int, coordinate.split(':'))
    pyautogui.click(x, y)
    time.sleep(1)  

def packet_callback(packet):
    global player_id, player_id_set, initial_coordinates_clicked, one_time_click_done, fight_mode

    if IP in packet and packet[IP].src == '172.65.255.133':  
        raw_layer = packet.getlayer(Raw)
        if raw_layer:
            payload = str(raw_layer.load)

            if 'GA;905' in payload:
                handle_fight_start(payload)

            elif 'GTM' in payload and player_id_set and 'GTS' + str(player_id) in payload or 'GTS' + str(player_id) in payload:
                handle_player_turn()

            elif 'GCK' in payload:
                handle_fight_end()

            elif 'GR1' + str(player_id) in payload:
                handle_ready_state()

def handle_fight_start(payload):
    global player_id, player_id_set, initial_coordinates_clicked, fight_mode
    if not fight_mode:  
        match = re.search(r'GA;905;(\d+)', payload)
        if match:
            player_id = match.group(1)
            player_id_set = True
            fight_mode = True

            print("FIGHT STARTED - Fight mode ON")
            click_initial_coordinates()
            time.sleep(1)

def click_initial_coordinates():
    global initial_coordinates_clicked

    if not initial_coordinates_clicked:
        for coordinate in ['1464:713', '1508:721', '1582:719']:
            x, y = map(int, coordinate.split(':'))
            pyautogui.moveTo(x, y)  
            pyautogui.click()  
            time.sleep(1)  
        initial_coordinates_clicked = True

    x, y = 1520, 766
    pyautogui.moveTo(x, y)  
    pyautogui.click()  
    time.sleep(1)  

def handle_player_turn():
    print("Your Turn")
    click_coordinate('1625:1065')
    time.sleep(1)
    subprocess.run(["python", "Combat/deplacement.py"])
    time.sleep(1)
    click_coordinate('1736:559')
    time.sleep(1)
    subprocess.run(["python", "Combat/attack.py"])

def handle_fight_end():
    global fight_mode, player_id_set
    print("Fight Ended - Fight mode OFF")
    time.sleep(1)  
    pyautogui.press('esc')  

    fight_mode = False
    player_id_set = False

    general_packet_received_event.set()

def handle_ready_state():
    global one_time_click_done
    click_coordinate('1540:716')
    if not one_time_click_done:
        click_coordinate('308:125')  
        one_time_click_done = True

def main():
    sniff(filter="ip", prn=packet_callback, store=0)

if __name__ == "__main__":
    main()