# HTB Challenge: Critical Flight - Complete Solution Guide

## Challenge Information
- **Name:** Critical Flight
- **Category:** Hardware
- **Difficulty:** Very Easy
- **Points:** 925

---

## Challenge Description
Your team needs to investigate PCB (Printed Circuit Board) production files for a flight controller that's causing DIY drones to fall out of the sky. Someone has sabotaged the design before production. Find the suspicious alterations.

---

## Files Provided

You'll receive Gerber files (PCB manufacturing files):

```
HadesMicro-B_Cu.gbr          - Bottom copper layer
HadesMicro-B_Fab.gbr         - Bottom fabrication layer
HadesMicro-B_Mask.gbr        - Bottom solder mask
HadesMicro-B_Paste.gbr       - Bottom solder paste
HadesMicro-B_Silkscreen.gbr  - Bottom silkscreen
HadesMicro-Edge_Cuts.gbr     - Board outline
HadesMicro-F_Cu.gbr          - Front (top) copper layer
HadesMicro-F_Fab.gbr         - Front fabrication layer
HadesMicro-F_Mask.gbr        - Front solder mask
HadesMicro-F_Paste.gbr       - Front solder paste
HadesMicro-F_Silkscreen.gbr  - Front silkscreen
HadesMicro-In1_Cu.gbr        - Inner layer 1 copper ⚠️ FLAG HERE
HadesMicro-In2_Cu.gbr        - Inner layer 2 copper ⚠️ FLAG HERE
```

---

## Step-by-Step Solution

### **Step 1: Understand PCB Layers**

A multi-layer PCB has:
- **Outer layers** (F_Cu and B_Cu) - Visible, contain components
- **Inner layers** (In1_Cu, In2_Cu) - Hidden between outer layers
- **Silkscreen** - Text and labels visible on board
- **Solder mask** - Green protective coating
- **Other layers** - Fabrication notes, paste stencils, etc.

**Key insight:** Inner layers are perfect for hiding things because they're sandwiched inside the board!

---

### **Step 2: Install Gerber Viewer**

Gerber files are industry-standard PCB manufacturing files. We need a viewer to see them.

```bash
sudo apt-get update
sudo apt-get install -y gerbv
```

**Alternative viewers:**
- KiCad (open-source PCB design software)
- gerbv (lightweight Gerber viewer)
- Online: https://gerber-viewer.easyeda.com/

---

### **Step 3: Navigate to Files**

```bash
cd /path/to/hw_critical_flight/flight_control_board/
ls -la
```

You should see 13 `.gbr` files.

---

### **Step 4: View Individual Layers**

Export each copper layer as PNG images:

```bash
# Export inner layer 1
gerbv --export=png --output=inner1.png --dpi=600 HadesMicro-In1_Cu.gbr

# Export inner layer 2
gerbv --export=png --output=inner2.png --dpi=600 HadesMicro-In2_Cu.gbr

# Export both together
gerbv --export=png --output=both_inner.png --dpi=600 HadesMicro-In1_Cu.gbr HadesMicro-In2_Cu.gbr
```

---

### **Step 5: Open and Examine Images**

```bash
xdg-open inner1.png
xdg-open inner2.png
```

**Or use the interactive viewer:**
```bash
gerbv HadesMicro-In1_Cu.gbr HadesMicro-In2_Cu.gbr
```

---

### **Step 6: Find the Flag**

**What to look for:**
- Text etched into the copper traces
- The flag is split between the two inner layers
- One layer has the first half: `HTB{533_7h3_1nn32_w02k1n95_0f_`
- Other layer has the second half: `313c720n1c5#$@}`

**Complete flag:**
```
HTB{533_7h3_1nn32_w02k1n95_0f_313c720n1c5#$@}
```

---

## Understanding the Flag

**Decoded (leetspeak):**
```
HTB{see_the_inner_workings_of_electronics#$@}
```

**Meaning:** The flag literally tells you to "see the inner workings" - referring to the inner layers of the PCB!

---

## Why This is a Security Issue

### **Real-World PCB Sabotage:**

1. **Hardware Backdoors**
   - Extra chips or circuits added to boards
   - Hidden data exfiltration paths
   - Kill switches or trojans

2. **Supply Chain Attacks**
   - Modified PCB designs during manufacturing
   - Counterfeit components
   - Malicious firmware pre-installed

3. **Notable Examples:**
   - **Bloomberg Supermicro story** (2018) - Alleged Chinese spy chips on server motherboards
   - **NSA ANT Catalog** - Hardware implants for surveillance
   - **Counterfeit network equipment** - Backdoored routers and switches

4. **Why Inner Layers?**
   - Not visible during visual inspection
   - Requires X-ray or destructive testing to detect
   - Can hide extra traces, chips, or antennas
   - Perfect for covert modifications

---

## Key Concepts Explained

### **What are Gerber Files?**
- Industry-standard format for PCB manufacturing
- Named after Gerber Systems Corp (now Ucamco)
- Each layer of the PCB is a separate file
- Contains coordinates and drawing commands
- Like a blueprint for the PCB fabrication machine

### **PCB Layer Stack:**
```
Top Silkscreen      (white text/graphics)
Top Solder Mask     (green coating)
Top Copper          (F_Cu) - traces and pads
------------------------------------
Inner Layer 1       (In1_Cu) ⚠️ FLAG HERE
Inner Layer 2       (In2_Cu) ⚠️ FLAG HERE
------------------------------------
Bottom Copper       (B_Cu) - traces and pads
Bottom Solder Mask  (green coating)
Bottom Silkscreen   (white text/graphics)
```

### **Gerber File Extensions:**
- `.gbr` - Gerber file
- `.gbl` - Bottom copper layer
- `.gtl` - Top copper layer
- `.g1`, `.g2` - Inner layers
- `.gbs`, `.gts` - Solder mask
- `.gbo`, `.gto` - Silkscreen
- `.gm1` - Board outline

---

## Alternative Solutions

### **Method 1: Command-line Text Search**

```bash
# Search for text patterns
strings *.gbr | grep -i "HTB"

# Look for ASCII art patterns
cat HadesMicro-In1_Cu.gbr | less
```

**Note:** This usually won't work because the flag is rendered as copper traces (coordinates), not text strings.

---

### **Method 2: Python Gerber Parser**

```python
import gerber
from gerber.render import RenderSettings, theme

# Parse Gerber file
layer = gerber.load_layer('HadesMicro-In1_Cu.gbr')

# Render to image
ctx = GerberCairoContext()
layer.render(ctx)
ctx.dump('output.png')
```

---

### **Method 3: Online Viewers**

Upload files to online Gerber viewers:
- https://www.pcbway.com/project/OnlineGerberViewer.html
- https://gerber-viewer.easyeda.com/
- https://gerblook.org/

**Warning:** Don't upload sensitive/real PCB files to public sites!

---

## Common Mistakes

1. **❌ Only viewing outer layers** → Inner layers are where secrets hide
2. **❌ Low DPI export** → Flag might be unreadable, use `--dpi=600` or higher
3. **❌ Not viewing all inner layers** → Flag is split across In1 and In2
4. **❌ Using text search** → Flag is copper traces, not text strings
5. **❌ Viewing layers separately** → View both inner layers together to see complete flag

---

## Tools & Resources

### **Essential Tools:**
- **gerbv** - Lightweight Linux Gerber viewer
- **KiCad** - Full PCB design suite (includes viewer)
- **ViewMate** - Free Windows Gerber viewer
- **CAM350** - Professional PCB CAM software

### **Installation:**
```bash
# Debian/Ubuntu/Kali
sudo apt install gerbv kicad

# Arch Linux
sudo pacman -S gerbv kicad

# macOS
brew install gerbv
```

---

## Detection & Prevention

### **How to Detect PCB Sabotage:**

1. **Visual Inspection**
   - Compare against reference design
   - Look for extra components
   - Check for unusual traces or pads

2. **X-Ray Imaging**
   - See internal layers without destructive testing
   - Detect hidden chips or traces
   - Industry standard for high-security hardware

3. **Bill of Materials (BOM) Verification**
   - Cross-check all components
   - Verify part numbers and manufacturers
   - Check for substitutions

4. **Electrical Testing**
   - Continuity tests
   - Power consumption analysis
   - Signal integrity measurements

5. **Gerber File Comparison**
   - Diff original vs production files
   - Automated checking tools
   - Hash verification of design files

### **Prevention Measures:**

- **Trusted suppliers only**
- **Design file encryption and signing**
- **Manufacturing oversight**
- **Random sample testing**
- **Secure supply chain**
- **In-house manufacturing for critical systems**

---

## Real-World Context

### **Famous Hardware Backdoor Cases:**

1. **SuperMicro "Spy Chip" Allegations (2018)**
   - Bloomberg reported Chinese spy chips on server motherboards
   - Tiny chips allegedly inserted during manufacturing
   - Companies denied, but raised awareness

2. **NSA ANT Catalog**
   - Leaked documents showing hardware implants
   - Modified cables, USB devices, hard drives
   - Intercepting equipment in supply chain

3. **Counterfeit Cisco Equipment**
   - Fake network switches with backdoors
   - Imported from unauthorized manufacturers
   - Sold as legitimate products

4. **Automotive Hacks**
   - Modified ECUs (Engine Control Units)
   - Cheat devices for emissions tests
   - Safety-critical systems compromised

---

## Learning Objectives

This challenge teaches:
- ✅ PCB structure and layer composition
- ✅ Gerber file format and viewing
- ✅ Hardware reverse engineering basics
- ✅ Supply chain security awareness
- ✅ Hidden data in manufacturing files
- ✅ Importance of design file verification

---

## Quick Reference

### **One-Line Solution:**
```bash
gerbv --export=png --output=flag.png --dpi=600 HadesMicro-In1_Cu.gbr HadesMicro-In2_Cu.gbr && xdg-open flag.png
```

### **Flag:**
```
HTB{533_7h3_1nn32_w02k1n95_0f_313c720n1c5#$@}
```

### **Flag Translation:**
```
"See the inner workings of electronics"
```

---

## Summary Checklist

- [ ] Extract challenge files
- [ ] Install Gerber viewer (gerbv or KiCad)
- [ ] Identify inner copper layers (In1_Cu.gbr and In2_Cu.gbr)
- [ ] Export layers to PNG with high DPI
- [ ] View both inner layers together
- [ ] Locate flag text etched in copper traces
- [ ] Combine both halves of the flag
- [ ] Submit flag

---

## Practice Similar Challenges

1. **HackTheBox Hardware Challenges:**
   - BlinkerFluids
   - Debug
   - Wrong Spooky Season

2. **Other CTF Hardware Challenges:**
   - PicoCTF Hardware challenges
   - CSAW Hardware challenges
   - DEF CON Hardware Hacking Village

3. **Learn More:**
   - KiCad tutorials (design your own PCB)
   - PCB manufacturing process videos
   - Hardware hacking workshops
   - Embedded systems security courses

---

## Troubleshooting

**Q: gerbv won't open?**
- Install dependencies: `sudo apt install gerbv`
- Try alternative: KiCad, online viewers

**Q: Can't see the flag in the image?**
- Increase DPI: `--dpi=1200`
- View both inner layers together
- Zoom in on the image
- Adjust colors/contrast

**Q: Flag is incomplete?**
- Make sure you view BOTH inner layers
- First half is on In1_Cu
- Second half is on In2_Cu

**Q: Images are inverted/wrong colors?**
- This is normal for negative layers
- The flag should still be readable
- Try different render settings in gerbv

---

## Additional Notes

**Industry Implications:**
- PCB inspection is critical for high-security applications
- Military, aerospace, and financial systems use X-ray inspection
- Trusted foundries are essential for sensitive hardware
- Open-source hardware helps with verification

**Career Relevance:**
- Hardware security engineer
- PCB design verification
- Supply chain security analyst
- Embedded systems security researcher

---

**Last Updated:** November 2025
**Challenge Solved By:** Viewing inner copper layers in Gerber files
**Difficulty Rating:** Very Easy (with right tools)
**Time Required:** 10-15 minutes
