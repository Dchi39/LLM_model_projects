import cv2
import time
import requests
import google.generativeai as genai

# === Configuration ===
GOOGLE_API_KEY = ""
ESP32_IP = "http://192.168."
IMAGE_PATH = "captured_instruction.jpg"

# === Initialize Gemini Client ===
genai.configure(api_key=GOOGLE_API_KEY)
client = genai.GenerativeModel("gemini-2.0-flash")


# === Capture Image from Webcam ===
def capture_image_on_space():
    cap = cv2.VideoCapture(1)  # Change index if necessary
    print("Press SPACE to capture image or ESC to quit.")
    while True:
        ret, frame = cap.read()
        cv2.imshow("Capture Handwritten Instruction", frame)
        key = cv2.waitKey(1)
        if key == 27:
            break
        elif key == 32:
            cv2.imwrite(IMAGE_PATH, frame)
            print("Image captured and saved.")
            break
    cap.release()
    cv2.destroyAllWindows()


# === Interpret Image with Gemini ===
def interpret_instruction_with_gemini(image_path):
    upload_start = time.time()
    uploaded_file = genai.upload_file(image_path)
    prompt = (
        "Read the handwritten instruction and convert it into commands "
        "to control a white and yellow light and a servo on Arduino. Use commands like:\n"
        "'W_ON', 'W_OFF' — for white light\n"
        "'Y_ON', 'Y_OFF' — for yellow light\n"
        "'SERVO_LEFT', 'SERVO_RIGHT', 'SERVO_CENTER' — to control direction\n"
        "'DELAY_1000' — delay in milliseconds.\n"
        "Example input: Turn on the yellow light. Wait 3 seconds. Move servo to the left.\n"
        "Respond with a plain list of commands like:\nY_ON\nDELAY_3000\nSERVO_LEFT"
    )
    start_model = time.time()
    response = client.generate_content([uploaded_file, prompt])
    end_model = time.time()
    model_time = end_model - start_model
    print(f"\n[✓] Gemini model processing time: {model_time:.2f} seconds")
    return response.text.strip().splitlines(), model_time


# === Send Commands to ESP32 Over Wi-Fi ===
def send_commands_to_esp32(commands):
    total_transmission_time = 0
    command_count = 0

    for cmd in commands:
        cmd = cmd.strip()
        if cmd.startswith("DELAY_"):
            try:
                delay_ms = int(cmd.split("_")[1])
                print(f"Waiting {delay_ms}ms...")
                time.sleep(delay_ms / 1000)
            except:
                print(f"Invalid delay command: {cmd}")
        else:
            try:
                command_count += 1
                start_time = time.time()
                url = f"{ESP32_IP}/command?cmd={cmd}"
                print(f"Sending: {cmd}")
                response = requests.get(url, timeout=5)
                end_time = time.time()
                elapsed = end_time - start_time
                total_transmission_time += elapsed
                print(f"ESP32 responded in {elapsed:.3f} seconds: {response.text}")
            except Exception as e:
                print(f"Error sending command '{cmd}': {e}")

    if command_count > 0:
        avg_transmission = total_transmission_time / command_count
        print(f"\n[✓] Average HTTP command transmission + ESP32 response time: {avg_transmission:.3f} seconds")

    return total_transmission_time


# === Main Workflow with Latency Tracking ===
def main():
    print("[*] Starting system latency measurement...")
    system_start = time.time()

    capture_image_on_space()

    model_start = time.time()
    commands, model_time = interpret_instruction_with_gemini(IMAGE_PATH)
    model_end = time.time()

    print("\n=== Interpreted Commands ===")
    for cmd in commands:
        print(cmd)

    transmission_time = send_commands_to_esp32(commands)

    system_end = time.time()
    total_system_latency = system_end - system_start

    print(f"\n[✓] Total system latency (camera to device): {total_system_latency:.2f} seconds")
    print(f"[✓] Model processing time: {model_time:.2f} seconds")
    print(f"[✓] Total HTTP transmission time: {transmission_time:.2f} seconds")


if __name__ == "__main__":
    main()
