# EchoLink: An Offline Emergency Messenger

## 1. Problem Definition and Context

During natural disasters, power outages, or other emergencies, traditional communication infrastructure like cellular networks and internet services often fail. This leaves people stranded without a way to contact loved ones, coordinate rescue efforts, or receive critical information. The lack of reliable communication can exacerbate the danger and chaos of an emergency situation.

EchoLink is a prototype designed to address this problem by providing a resilient, decentralized messaging system that operates entirely offline. It enables users to send and receive text messages to nearby devices using local network technologies like Wi-Fi Direct, creating a peer-to-peer network that is not dependent on any centralized infrastructure.

## 2. Identified Constraints

The solution must operate under the following constraints:

*   **No Internet Connectivity:** The system must function without any access to the internet.
*   **Low Power Consumption:** Devices may be running on battery power, so the application should be energy-efficient.
*   **Minimal Dependencies:** The software should be lightweight and require minimal pre-installed libraries or complex setup.
*   **Cross-Platform:** The solution should ideally run on a variety of devices, including laptops and smartphones.

## 3. Design Alternatives and Final Decisions

### Communication Technology

*   **Bluetooth:** Low energy consumption, but limited range and bandwidth.
*   **Wi-Fi Ad-Hoc:** A decentralized mode, but less commonly supported on modern devices.
*   **Wi-Fi Direct (Chosen):** Offers a good balance of range, bandwidth, and power consumption. It is well-supported on most modern laptops and smartphones.

### Architecture

*   **Client-Server:** A central server would manage communication, but this introduces a single point of failure.
*   **Peer-to-Peer (P2P) (Chosen):** A decentralized model where each device acts as a node. This is more resilient and aligns with the project's goals.

### User Interface

*   **Graphical User Interface (GUI):** More user-friendly, but requires more complex libraries and more power.
*   **Command-Line Interface (CLI) (Chosen for Prototype):** Lightweight, fast, and highly portable. It is ideal for a resource-constrained environment.

## 4. Tools Used

*   **Programming Language:** Python 3
*   **Core Library:** `socket` (for networking)
*   **UI:** Standard input/output (for the CLI)

## 5. Performance Tests and Benchmarks

*(This section will be filled in after the prototype is developed and tested.)*
