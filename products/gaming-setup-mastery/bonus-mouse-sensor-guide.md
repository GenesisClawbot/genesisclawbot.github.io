# Mouse Sensor Guide — PixArt, DPI, and What Actually Matters for Competitive Gaming

*A no-nonsense technical guide to gaming mouse sensors: what matters, what doesn't, and how to cut through the marketing.*

---

## DPI Explained: The Most Misunderstood Spec

DPI (dots per inch) measures how far your cursor moves on screen relative to physical mouse movement. A higher DPI means the cursor moves further per inch of mouse travel. Most gaming mice range from 100 DPI to 25,600 DPI.

**The myth:** Higher DPI = more precision = better aim.

**The reality:** This is almost entirely backwards for competitive gaming.

In competitive FPS games, the vast majority of players use DPI settings between 400 and 3200. The most common professional settings are 800 DPI and 1600 DPI. Why? Because high DPI amplifies every tiny tremor in your hand. At 8000+ DPI, even a subtle jitter from resting your mouse hand on the pad creates massive on-screen cursor movement. At 400 or 800 DPI, you have fine control over small movements because the amplification factor is lower.

Think of it like steering a car: low DPI is like power steering at low speed — small inputs give you small, precise outputs. High DPI is like a very sensitive steering wheel — tiny hand movements cause big turns. For most gamers, lower DPI with more physical mouse movement gives you better control.

**What DPI should you use?**
- Competitive FPS (Valorant, CS2, Apex): 400–1600 DPI. Most pros land at 800.
- Strategy / MOBAs: 800–1600 DPI. Enough sensitivity for quick camera pans.
- General desktop use: Whatever feels natural. Most people default to 800–1200.

The only situation where very high DPI makes sense is if you have an exceptionally precise, steady hand and you play games where you need both very fast sweeps and very fine aiming adjustments. Even then, software-based "sensitivity" multipliers in games give you more granular control than raw DPI changes.

---

## PixArt Sensors: The Standard in Gaming Mice

PixArt Technologies is the manufacturer of the sensors found in the majority of gaming mice. Their sensors power everything from £30 budget mice to £150 flagships. Understanding PixArt's naming scheme helps you evaluate sensor quality quickly.

### PixArt PAW Series (Current Generation)

**PAW3395**
- Maximum DPI: 26,000
- Typical mice: Pulsar X2V2, Lamzu Maya, various mid-range wireless mice
- Assessment: Excellent mid-range sensor. Near-zero smoothing, no acceleration, accurate tracking at all speeds. The standard for quality mice under £100.

**PAW3950**
- Maximum DPI: 30,000
- Typical mice: Finalmouse UltralightX, some proprietary implementations
- Assessment: Top-tier sensor found in ultra-premium mice. Essentially the PAW3395 with higher maximum DPI and slightly improved tracking at extreme speeds. Practically indistinguishable from PAW3395 in real-world use.

**PAW3392**
- Maximum DPI: 25,600
- Typical mice: Older (2022-2023) flagship mice like Logitech G Pro X Superlight (original)
- Assessment: Excellent sensor, slightly older generation. Still perfectly competitive.

**PAW3311**
- Maximum DPI: 12,000
- Typical mice: Budget gaming mice (£20-50 range)
- Assessment: Perfectly adequate for casual gaming. No meaningful smoothing at normal DPI settings. Not ideal for competitive but doesn't disqualify you.

### Non-PixArt Sensors

**Logitech Hero 2**
- Found in: Logitech G Pro X Superlight 2, G502 X Plus
- Maximum DPI: 32,000
- Assessment: Logitech's proprietary sensor. Excellent — near-zero smoothing, no acceleration, smooth tracking at all speeds. Logitech's sensor development has been top-tier since 2020.

**Razer Focus Pro 30K / Razer 5G**
- Found in: Razer Viper V3 Pro, DeathAdder V3
- Maximum DPI: 30,000
- Assessment: Razer's best sensor. Based on a PixArt architecture but with Razer-specific tuning. Excellent tracking, no meaningful issues.

**SteelSeries TrueMove**
- Found in: SteelSeries mice
- Maximum DPI: 18,000–25,600 depending on generation
- Assessment: Solid sensors. TrueMove Pro (18K) is good but not the latest PixArt generation. TrueMove Air is adequate. Not the reason to buy or avoid SteelSeries.

---

## Polling Rate: 125Hz vs 1000Hz vs 8000Hz

The polling rate is how many times per second the mouse reports its position to your PC. Higher polling rate = faster data transmission = potentially faster response to your inputs.

| Polling Rate | Reports per Second | Latency |
|---|---|---|
| 125Hz | 125 | 8ms |
| 500Hz | 500 | 2ms |
| 1000Hz | 1,000 | 1ms |
| 4000Hz | 4,000 | 0.25ms |
| 8000Hz | 8,000 | 0.125ms |

**Does it matter?** For most gamers, no — and here's why:

Human reaction time averages around 250ms (visual processing + motor response). Even at 125Hz, the 8ms polling latency is invisible relative to your reaction time. The difference between 1ms (1000Hz) and 0.125ms (8000Hz) is 0.875ms — a fraction of a human reaction increment.

The one situation where 8000Hz does matter is high-speed flick shots in competitive FPS games, where the total time between seeing a target and completing your flick might be 150-200ms. In that window, the difference between 1ms and 0.125ms input latency is a small but potentially meaningful percentage improvement. Competitive esports players at the top tier can perceive this difference.

For everyone else: 1000Hz is more than sufficient. Don't pay a premium specifically for 8000Hz unless you know you need it.

---

## What Actually Matters: The Competitive Checklist

### No. 1: No Sensor Flaws

The critical sensor flaws to avoid:
- **Acceleration:** The mouse reports faster movement than you're physically making, above a certain speed threshold. This destroys muscle memory. Test: move the mouse slowly across the pad, then move the same distance quickly. Your cursor should end up in the same position. If it doesn't, you have acceleration.
- **Jitter:** At rest, the cursor should not move on its own. If it jitters or "踉" — the sensor has a rest precision problem.
- **Smoothing:** Some sensors average multiple samples, which introduces input lag and makes movement feel "floaty." The PixArt PAW3395 and Logitech Hero 2 have essentially zero smoothing. Budget sensors sometimes do.

### No. 2: Low Weight

Weight matters more than most people think. A lighter mouse requires less force to move, which means faster micro-adjustments and less fatigue over long sessions. The performance difference between a 60g mouse and an 80g mouse is noticeable within an hour.

Current generation ultra-lightweight mice achieve their low weight through honeycomb shell construction (removing unnecessary material from the shell) without compromising structural rigidity. The Logitech G Pro X Superlight 2 (60g), Razer Viper V3 Pro (55g), and Pulsar X2V2 Mini (48g) are all excellent examples.

Weight below ~50g starts to feel unstable if you use a palm grip — the mouse can feel like it's floating rather than planted. Aim for 50-70g for the best balance of light weight and stability.

### No. 3: Shape

Shape is deeply personal. A mouse that works perfectly for one person can be completely wrong for another. The three main grip styles:

- **Palm grip:** Your entire palm rests on the mouse. Larger, fuller mice work best (Logitech G Pro X Superlight 2, DeathAdder V3).
- **Claw grip:** Your palm touches the back, fingers arch over the buttons. Medium-sized mice work well (Razer Viper V3 Pro, Finalmouse).
- **Fingertip grip:** Only your fingertips control the mouse. Smaller, lighter mice work best (Pulsar X2V2 Mini).

Try before you buy if possible. If buying online, measure your hand (palm length from wrist to fingertip) and compare against the mouse dimensions listed in reviews.

### No. 4: Switch Quality

Mouse switches (the buttons you click) matter more than most buyers realise. Quality switches have:
- Crisp, consistent actuation — no "mushy" feeling
- High durability (50+ million clicks for premium switches)
- No pre-travel (play before the click registers)
- No post-travel (wobble after the click)

Optical switches (like Razer's Gen-3 or Logitech's optical switches) use an infrared beam to register clicks rather than a physical metal contact. This eliminates debounce delay (the tiny pause between clicks where the switch "settles" before registering again) and increases click speed. They're in most premium mice in 2026.

---

## Quick Reference: Best Sensors by Category

| Sensor | DPI Max | Key Feature | Found In | Tier |
|--------|---------|-------------|----------|------|
| PixArt PAW3395 | 26,000 | Near-zero smoothing, no acceleration | Pulsar X2V2, Lamzu | Mid-premium |
| PixArt PAW3950 | 30,000 | Best-in-class tracking at speed | Finalmouse, premium | Top |
| Logitech Hero 2 | 32,000 | Zero smoothing, excellent wireless | Logitech GPXS2 | Top |
| Razer Focus Pro 30K | 30,000 | Fast, reliable optical | Razer Viper V3 Pro | Top |
| PixArt PAW3311 | 12,000 | Adequate, no-frills | Budget mice | Budget |

---

## The Bottom Line

Don't obsess over DPI numbers. Set your mouse to 800 DPI and use in-game sensitivity to tune your effective sensitivity. Higher is not better.

Do care about: sensor flaws (acceleration, jitter), weight (sub-80g is the target), shape (matches your grip), and switch quality (optical is now standard at mid-range and above).

For most gamers: a mouse with a PixArt PAW3395 or equivalent sensor, weighing 55-70g, at 800-1600 DPI, with 1000Hz polling, will perform identically to a £150 flagship in everything except feel and build quality.

---

*Affiliation notice: This guide contains affiliate links. Purchasing through links marked with tag genesis01-20 may earn a small commission at no extra cost to you.*
