# 🔧 Assembly Guide: Bruno Theater Control Robot

## ⚡ Pre-Assembly Checklist

### Required Tools
- [ ] Soldering iron (for heat-set inserts)
- [ ] Phillips head screwdriver (small)
- [ ] Wire strippers
- [ ] Multimeter (for testing)
- [ ] Hot glue gun (optional, for cable management)

### Print Settings Used
```
Layer Height: 0.2mm
Infill: 20% gyroid
Support: Touching buildplate only
Print Speed: 60mm/s
Nozzle Temperature: 215°C (PLA+)
Bed Temperature: 60°C
```

## 📦 Unboxing and Preparation

### 3D Printed Parts Inspection
1. Check all parts for layer adhesion
2. Remove support material carefully
3. Light sanding on contact surfaces
4. Test fit all threaded inserts

### Electronics Testing
1. Flash firmware to ESP32 first
2. Test OLED display separately
3. Verify 433MHz transmission range
4. Check button responsiveness

## 🔩 Step-by-Step Assembly

### Phase 1: Heat-Set Insert Installation

**Location**: Four mounting points in main body cavity

```
Insert Positions:
- Front mounting posts (x2)
- Rear mounting posts (x2)
```

1. Heat soldering iron to 240°C
2. Place M3 heat-set insert on mounting post
3. Press insert with hot iron tip until flush
4. Allow to cool completely before handling
5. Test with M3 screw - should thread smoothly

### Phase 2: Electronics Preparation

**ESP32 Programming**
```bash
# Upload firmware (from project root)
platformio run --target upload
```

**OLED Wiring**
```
ESP32 Pin → OLED Pin
GPIO 21   → SDA
GPIO 22   → SCL
3.3V      → VCC
GND       → GND
```

**Button Wiring**
```
ESP32 Pin → Component
GPIO 18   → Button (with pull-up)
GND       → Button common
```

### Phase 3: Internal Assembly

1. **Mount ESP32**
   - Position in rear cavity
   - Secure with M3 x 8mm screws
   - Ensure USB port accessible

2. **Install OLED Display**
   - Insert into front eye cavity
   - Route wires through internal channel
   - Secure with oled-mount.stl bracket

3. **Button Mechanism**
   - Install button-actuator.stl in head
   - Route wires down through neck opening
   - Test actuation before final assembly

### Phase 4: Power System

**Battery Installation**
1. Insert Li-Po into battery-tray.stl
2. Route charging cable to side port
3. Connect power to ESP32 VIN
4. Secure with battery hold-down

**Power Management Testing**
- Verify 8+ hour operation time
- Check charging indicator function
- Test low battery warning display

### Phase 5: Final Assembly

1. **Head Attachment**
   - Route all wires through neck
   - Secure head with M3 x 12mm screws
   - Test button actuation through head

2. **Base Stability**
   - Attach weighted base
   - Check center of gravity
   - Verify stable on uneven surfaces

## 🧪 Testing Protocol

### Functional Testing
1. **Power On Test**
   - OLED should show startup animation
   - All systems green: normal eyes
   - No WiFi: X X eyes

2. **Button Response**
   - Lift head mechanism
   - Press button - should click
   - Verify smoke machine activation

3. **Wireless Range**
   - Test 433MHz at 10m, 25m, 50m
   - Document signal strength
   - Note any interference sources

### Integration Testing
4. **Theater System Integration**
   - Connect to main MIDI system
   - Verify backup mode switching
   - Test with actual smoke machine

## 🎯 Calibration Settings

### Button Sensitivity
```cpp
// In robotti_433mhz.ino
#define BUTTON_DEBOUNCE_MS 50
#define BUTTON_HOLD_TIME_MS 1000
```

### OLED Eye Animations
```cpp
// Animation timing
#define BLINK_INTERVAL 3000
#define ALERT_FLASH_SPEED 200
```

### 433MHz Settings
```cpp
// Transmission parameters
#define RADIO_FREQUENCY 433.92
#define POWER_LEVEL 10  // Max range
#define DATA_RATE 2000  // 2kbps
```

## 🔍 Troubleshooting

### Common Issues

**OLED Display Not Working**
- Check I2C address (usually 0x3C)
- Verify 3.3V power supply
- Reseat SDA/SCL connections

**Button Not Responsive**
- Check pull-up resistor (10kΩ internal)
- Verify mechanical actuation clearance
- Test with multimeter in continuity mode

**433MHz Not Transmitting**
- Verify antenna connection
- Check power supply stability
- Confirm frequency settings

### Performance Optimization

**Battery Life Extension**
- Lower OLED brightness
- Increase sleep mode usage
- Optimize transmission power

**Range Improvement**
- Upgrade to external antenna
- Check for interference sources
- Adjust transmission power

## 📋 Quality Control Checklist

Before marking Bruno as "production ready":

- [ ] All screws properly torqued
- [ ] No loose wiring connections  
- [ ] OLED displays proper animations
- [ ] Button actuation is reliable
- [ ] 433MHz range meets requirements
- [ ] Battery life exceeds 8 hours
- [ ] Professional appearance maintained
- [ ] Documentation complete

---

*This assembly guide ensures consistent, professional results when building Bruno robots for theater environments.*