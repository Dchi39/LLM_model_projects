# Handwriting-Based IoT Control System Using LLM and ESP32

This project demonstrates a novel IoT control system designed for speech-impaired users. It leverages a Large Language Model (LLM) to interpret handwritten instructions and wirelessly control electronic appliances via an ESP32 board.

📌 Project Overview

*Input: Handwritten commands are captured and interpreted using an AI-powered system (e.g., Gemini Flash 2.0).

*Processing: The commands are processed using an LLM to extract actionable instructions.

*Communication: Interpreted commands are sent over Wi-Fi to an ESP32-based IoT controller.

*Output: The ESP32 triggers relays, servo motors, or LEDs to execute the desired actions, including support for delay and sequential operations.

This solution enhances accessibility and independence for individuals with speech or motor impairments by combining handwriting recognition, natural language understanding, and IoT control.

🔧 PlatformIO Configuration

The project uses PlatformIO for development with the following environment:

[env:esp32doit-devkit-v1]

platform = espressif32

board = esp32doit-devkit-v1

framework = arduino

monitor_speed = 115200

lib_deps = 
    ESP32Servo

