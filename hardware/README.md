# MCP2515 and Linux SocketCAN bring-up

My [`mcp2515.dts`](../config/hardware/mcp2515.dts) Device Tree overlay source is stored in the root `config/hardware/` directory alongside other deployment configuration. This folder contains setup and troubleshooting documentation. In my project I used an **MCP2515 CAN controller connected over SPI** and accessed CAN from Linux user space through **SocketCAN**.

![CAN to Linux gateway interface chain](../docs/diagrams/linux-can-stack.png)

## Communication chain

```text
CAN-H / CAN-L bus
        |
MCP2515 CAN controller
        |
SPI + interrupt GPIO
        |
Linux Device Tree / kernel driver
        |
SocketCAN interface (usually can0)
        |
Gateway CAN Connector / local application
```

A kernel-visible `can0` interface is a prerequisite for the CAN connector and the parallel SocketCAN prototype. This directory does **not** replace the need for a compatible transceiver, correct pin wiring, and bus termination.

## What my overlay declares

My [`config/hardware/mcp2515.dts`](../config/hardware/mcp2515.dts) is specific to an Orange Pi Zero 3 / H616-style Device Tree. It defines an **8 MHz fixed oscillator**, uses **PC7** for the controller interrupt, and attempts to create a CAN device under **`&spi1`** with chip-select register `1`.

**Important discrepancy:** during my SPI debugging I used **SPI0** and encountered an Armbian pin assignment conflict, whereas the included overlay source refers to `spi1`. I preserve this discrepancy instead of guessing which controller and mapping a different board revision needs. Verify the actual SPI controller, chip select, clock, IRQ polarity, and kernel overlays on your board.

## Bring-up checklist

1. Inspect the board schematic and confirm MOSI/MISO/SCLK/CS, interrupt pin, CAN-H/CAN-L, transceiver, common ground, and required termination.
2. Install a suitable kernel and Device Tree overlay mechanism. I resolved an Armbian pinmux conflict on my setup by moving to **Ubuntu Noble**; that result is specific to the tested environment.
3. Install utilities such as `device-tree-compiler`, `iproute2`, and `can-utils` using your distribution's package manager.
4. Compile the provided DTS **only after confirming and correcting its hardware mappings**:

   ```bash
   # Run from the repository root; adjust output location as needed.
   dtc -@ -I dts -O dtb -o mcp2515.dtbo config/hardware/mcp2515.dts
   ```

5. Install/enable the overlay using the mechanism documented for your kernel image (installation directories and bootloader settings depend on the target Linux image). Reboot and check kernel logs and `ip link` for a CAN network interface.
6. Bring up the interface with the **actual bus bitrate**, not an assumed default:

   ```bash
   # Set this to the speed configured on every other node of your bus.
   CAN_BITRATE=250000  # EXAMPLE ONLY — replace with your actual bitrate
   sudo ip link set can0 down || true
   sudo ip link set can0 up type can bitrate "$CAN_BITRATE"
   ip -details link show can0
   candump can0
   ```

7. For controlled tests, use `cansend` and `candump` with an appropriate test device or safe isolated bus. Do not send arbitrary CAN frames to live actuators.

## What I learned during hardware bring-up

I encountered two separate faults during initial bring-up: an SPI/pin initialization conflict and swapped **CAN-H**/**CAN-L** connections at one end of the physical bus. A successful software loopback test did not establish that physical CAN communication worked. Verify kernel driver registration, SPI wiring, bitrate, electrical connectivity, and actual traffic independently.

For software architecture discussions, return to the [project README](../README.md).
