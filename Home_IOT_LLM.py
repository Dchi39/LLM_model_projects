import cv2
import time
import requests
import google.generativeai as genai

# === Configuration ===
GOOGLE_API_KEY = ""  # Replace with your actual API key
ESP32_IP = "http://192.168."  # Replace with your ESP32's IP
IMAGE_PATH = "captured_instruction.jpg"

# === Initialize Gemini Client ===
genai.configure(api_key=GOOGLE_API_KEY)
client = genai.GenerativeModel("gemini-2.0-flash")

# === Capture Image from Webcam ===
def capture_image_on_space():
    cap = cv2.VideoCapture(1)  # Adjust index if needed
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
    response = client.generate_content([uploaded_file, prompt])
    return response.text.strip().splitlines()

# === Send Commands to ESP32 Over Wi-Fi ===
def send_commands_to_esp32(commands):
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
                url = f"{ESP32_IP}/command?cmd={cmd}"
                print(f"Sending: {cmd}")
                response = requests.get(url, timeout=5)
                print(f"Response: {response.text}")
            except Exception as e:
                print(f"Error sending command '{cmd}': {e}")

# === Main Workflow ===
def main():
    capture_image_on_space()
    commands = interpret_instruction_with_gemini(IMAGE_PATH)
    print("\n=== Interpreted Commands ===")
    for cmd in commands:
        print(cmd)
    send_commands_to_esp32(commands)

if __name__ == "__main__":
    main()
