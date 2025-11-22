# 📐 Technical Specifications: Bruno Robot

## 🎯 Design Requirements

### Functional Requirements
- **Primary Function**: Manual smoke machine control during WiFi failures
- **Activation Method**: Lift head → press button → smoke activated  
- **Response Time**: < 200ms from button press to 433MHz transmission
- **Operating Range**: 50m minimum line-of-sight to smoke machines
- **Battery Life**: 8+ hours continuous operation
- **Status Display**: Real-time system health via OLED "eyes"

### Environmental Requirements
- **Operating Temperature**: 10°C to 40°C (theater environment)
- **Humidity**: 20% to 80% RH (non-condensing)
- **Vibration**: Survives transport in equipment cases
- **Durability**: 1000+ button press cycles
- **Aesthetic**: Professional appearance suitable for theater control booth

## 🏗️ Mechanical Design

### Overall Dimensions
```
Width:  120mm
Depth:   80mm  
Height: 160mm (head up position)
        120mm (head down position)
Weight: 380g ± 20g (with electronics)
```

### Material Specifications
- **Primary Material**: PLA+ (eSUN brand recommended)
- **Color**: Matte black or dark gray
- **Layer Height**: 0.2mm (balance of strength/detail)
- **Infill**: 20% gyroid (optimal strength-to-weight)
- **Wall Thickness**: 1.6mm (4 perimeters @ 0.4mm nozzle)

### Print Orientation & Support
```
bruno-head.stl:        Face down, minimal supports
bruno-body.stl:        Upright, supports touching buildplate
bruno-base.stl:        Bottom down, no supports needed
oled-mount.stl:        Face down, no supports needed
button-actuator.stl:   Side down, no supports needed
battery-tray.stl:      Open side up, no supports needed
```

### Critical Tolerances
- **Button clearance**: 0.2mm ± 0.1mm
- **OLED fit**: 0.1mm interference fit
- **Screw threads**: M3 x 0.5mm standard
- **Head rotation**: 15° ± 2° tilt range

## ⚡ Electrical System

### Power Management
- **Battery**: 3.7V Li-Po, 2000mAh minimum
- **Charging**: USB-C, 5V/1A input
- **Regulation**: ESP32 internal LDO (3.3V logic)
- **Protection**: Over-discharge, over-current protection
- **Runtime**: 8-12 hours typical usage

### ESP32 Configuration
```
Board: ESP32 WROOM-32
Flash: 4MB
SRAM: 520KB
Clock: 240MHz (dual core)
WiFi: 802.11 b/g/n
Bluetooth: 4.2 BR/EDR + BLE
```

### GPIO Pin Assignment
```
GPIO 18: Button input (internal pull-up)
GPIO 21: I2C SDA (OLED display)
GPIO 22: I2C SCL (OLED display)
GPIO 4:  433MHz data pin
GPIO 2:  Status LED (built-in)
GPIO 0:  Boot mode (internal use)
EN:      Reset pin
```

### I2C Configuration
```
OLED Display: SSD1306 128x64
I2C Address: 0x3C
Clock Speed: 400kHz (fast mode)
Pull-ups: 4.7kΩ (external recommended)
```

### 433MHz Specifications
```
Module: Generic 433MHz TX
Frequency: 433.92 MHz ISM band
Power Output: 10mW (regulation compliant)
Data Rate: 2000 bps
Modulation: ASK/OOK
Range: 50-100m line-of-sight
```

## 🔧 Firmware Architecture

### Core Functions
```cpp
void setup() {
  // Initialize I2C for OLED
  // Configure button interrupt
  // Setup 433MHz transmitter
  // Display startup animation
}

void loop() {
  // Monitor button state
  // Update OLED animations  
  // Handle low battery warnings
  // Process any WiFi commands
}

void triggerSmoke() {
  // Send 433MHz activation signal
  // Update OLED with feedback
  // Log activation event
}
```

### Memory Allocation
- **Flash Usage**: ~800KB (of 4MB available)
- **RAM Usage**: ~150KB (of 520KB available)
- **OLED Buffer**: 1KB (128x64 monochrome)
- **WiFi Stack**: ~100KB when active

### Real-Time Constraints
- **Button Response**: < 50ms interrupt latency
- **OLED Update**: 60 FPS animation capability
- **433MHz Transmission**: < 100ms total time
- **Battery Monitoring**: 1Hz sample rate

## 🎨 Industrial Design

### Aesthetic Philosophy
- **Art Deco Influences**: Clean lines, geometric forms
- **Retro-Futurism**: "What 1960s thought 2020s would look like"
- **Professional Equipment**: Fits naturally in control booth
- **Human-Centered**: Intuitive operation under stress

### Color Scheme
- **Primary**: Matte black (RAL 9005 equivalent)
- **Accents**: Blue OLED glow (status indication)
- **Optional**: Dark gray (RAL 7021) for variety

### Surface Finish
- **3D Print Lines**: Intentionally visible (industrial aesthetic)
- **Critical Surfaces**: Light sanding for smooth operation
- **Texture**: Fine stipple on grip surfaces

### Ergonomic Considerations
- **Grip**: Comfortable single-hand operation
- **Button Feel**: Positive tactile feedback
- **Weight**: Bottom-heavy for stability
- **Size**: Fits standard equipment rack spacing

## 📊 Performance Specifications

### Reliability Metrics
- **MTBF**: 10,000 hours (estimated)
- **Button Life**: 100,000 actuations minimum
- **Drop Test**: 0.5m onto hard surface
- **Vibration**: 2G peak, 10-500Hz sweep

### Environmental Testing
- **Temperature Cycling**: -5°C to +50°C, 10 cycles
- **Humidity**: 85% RH, 48 hours
- **Shock**: 10G peak, 11ms duration
- **EMC**: FCC Part 15 Class B equivalent

### Communication Performance
```
433MHz Range Testing:
- Indoor (office): 25m typical
- Outdoor (clear): 100m+ typical  
- Theater (RF noise): 50m minimum
- Battery low: 30m graceful degradation
```

## 🔬 Testing & Validation

### Design Validation Tests
1. **Functional**: All features work as specified
2. **Environmental**: Operates in theater conditions
3. **Reliability**: 1000+ button press cycles
4. **Safety**: No sharp edges, secure battery
5. **Aesthetic**: Professional appearance maintained

### Production Testing
1. **Visual Inspection**: Print quality, assembly
2. **Functional Test**: Button, OLED, 433MHz
3. **Range Test**: Verify 50m minimum
4. **Battery Test**: 8+ hour runtime
5. **Final QC**: Complete documentation

### Acceptance Criteria
- [ ] All mechanical functions operate smoothly
- [ ] 433MHz range exceeds 50m in theater
- [ ] OLED displays all status conditions
- [ ] Battery life exceeds 8 hours
- [ ] Professional appearance maintained
- [ ] Documentation complete and accurate

---

*These technical specifications ensure Bruno meets professional theater reliability standards while maintaining the elegant design aesthetic that makes it suitable for high-visibility control booth environments.*