# Critical Flight - CTF Challenge

## 📋 Challenge Information

**Category:** Hardware  
**Difficulty:** Very Easy  
**Points:** 925  
**Challenge Type:** PCB Analysis / Gerber File Inspection  

## 📝 Challenge Description

Investigate PCB (Printed Circuit Board) production files for a flight controller that's causing DIY drones to fall out of the sky. Someone has sabotaged the design before production by hiding malicious content in the inner layers. Find the suspicious alterations.

## 🎯 Solution Overview

The challenge involves analyzing Gerber files (PCB manufacturing files) to find hidden content in the inner copper layers. The flag is cleverly hidden in the internal layers of a multi-layer PCB, which are normally invisible when the board is assembled.

### Key Insight
Inner PCB layers (In1_Cu, In2_Cu) are sandwiched between outer layers, making them perfect for hiding information that won't be visible on the final product.

## 🚀 Quick Start

### Prerequisites
- Gerber file viewer (KiCad, gerbv, or online viewer)
- No special hardware needed

### Option 1: KiCad (Recommended)
```bash
# Install KiCad
sudo apt install kicad

# Open Gerber viewer
kicad -> File -> Open -> Gerber Viewer

# Load all .gbr files from data/flight_control_board/
# Pay special attention to In1_Cu and In2_Cu layers
```

### Option 2: Online Gerber Viewer
1. Visit: https://www.pcbway.com/project/OnlineGerberViewer.html
2. Upload all .gbr files from `data/flight_control_board/`
3. Toggle layer visibility
4. Examine inner layers (In1_Cu.gbr and In2_Cu.gbr)

### Option 3: gerbv (Linux)
```bash
sudo apt install gerbv
cd data/flight_control_board/
gerbv *.gbr
# Use layer panel to show/hide layers
# Focus on In1_Cu and In2_Cu
```

## 📁 Folder Structure

```
critical_flight/
├── README.md                    # This file
├── data/                        # Challenge files
│   └── flight_control_board/   # Gerber files
│       ├── HadesMicro-F_Cu.gbr     # Front copper layer
│       ├── HadesMicro-B_Cu.gbr     # Bottom copper layer
│       ├── HadesMicro-In1_Cu.gbr   # Inner layer 1 ⚠️ FLAG HERE
│       ├── HadesMicro-In2_Cu.gbr   # Inner layer 2 ⚠️ FLAG HERE
│       ├── HadesMicro-*_Mask.gbr   # Solder mask layers
│       ├── HadesMicro-*_Paste.gbr  # Solder paste layers
│       ├── HadesMicro-*_Silkscreen.gbr  # Silkscreen layers
│       ├── HadesMicro-Edge_Cuts.gbr     # Board outline
│       ├── pcb_view.png            # PCB visualization
│       ├── top_copper.png          # Top layer view
│       └── silkscreen.png          # Silkscreen view
├── docs/                        # Documentation
│   └── SOLUTION_GUIDE.md       # Complete walkthrough
└── solution/                    # Solution scripts (if any)
```

## 🔧 Technical Details

### Understanding PCB Layers

A multi-layer PCB consists of:

**Outer Layers (Visible):**
- **F_Cu (Front Copper)** - Top layer with components
- **B_Cu (Bottom Copper)** - Bottom layer
- **F_Silkscreen / B_Silkscreen** - Text and labels
- **F_Mask / B_Mask** - Solder mask (protective coating)

**Inner Layers (Hidden):**
- **In1_Cu (Inner Layer 1)** - Hidden between layers ⚠️
- **In2_Cu (Inner Layer 2)** - Hidden between layers ⚠️

**Other:**
- **Edge_Cuts** - Board outline
- **Fab** - Fabrication notes
- **Paste** - Solder paste stencils

### The Vulnerability

The saboteur placed the flag as copper traces on the inner layers:
- Inner layers are sandwiched inside the PCB
- Not visible on assembled board
- Perfect for hiding malicious circuits or messages
- Can only be seen by examining manufacturing files

### Finding the Flag

1. **Load Gerber files** in a viewer
2. **Disable outer layers** to see through the board
3. **Enable inner layers** (In1_Cu.gbr and In2_Cu.gbr)
4. **Look for text or unusual patterns** - the flag will be clearly visible
5. **Flag format:** HTB{...}

## 💡 Learning Points

1. **PCB Design:** Understanding multi-layer PCB construction
2. **Gerber Files:** Industry-standard PCB manufacturing format
3. **Supply Chain Security:** Hidden backdoors in hardware
4. **Hardware Forensics:** Analyzing manufacturing files
5. **Layer-based Hiding:** Using internal layers to conceal information

## 🛡️ Real-World Implications

This challenge demonstrates:
- Hardware supply chain attacks
- Backdoors in PCB designs
- Importance of reviewing manufacturing files
- Trust issues in outsourced PCB production
- Need for hardware security verification

## 📖 Additional Resources

- See `docs/SOLUTION_GUIDE.md` for complete walkthrough
- [KiCad Documentation](https://docs.kicad.org/)
- [Gerber File Format](https://www.ucamco.com/en/gerber)
- [PCB Design Basics](https://learn.sparkfun.com/tutorials/pcb-basics)

## 🐛 Troubleshooting

### Can't Open Gerber Files
- Ensure you have KiCad or gerbv installed
- Try online viewer if local tools don't work
- All .gbr files should be in the same directory

### Don't See Inner Layers
- Make sure you loaded In1_Cu.gbr and In2_Cu.gbr
- Toggle layer visibility in the viewer
- Disable outer layers to see inner content clearly

### Flag Not Visible
- Zoom in on inner layers
- Adjust layer colors for better contrast
- Check both In1_Cu and In2_Cu layers
- Look for text patterns or unusual traces

## ✅ Success Criteria

- Successfully load Gerber files in viewer
- Understand PCB layer structure
- Identify inner layers containing the flag
- Extract the complete flag
- Flag format: `HTB{...}`

---

**Challenge Type:** Hardware Forensics / PCB Analysis  
**Key Skills:** Gerber file analysis, PCB layer understanding  
**Tools:** KiCad, gerbv, or online Gerber viewers  
**Difficulty:** Very Easy (simple file inspection)
