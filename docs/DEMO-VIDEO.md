# Munim demo video: shot list and captions

About 3 minutes. Every shot uses a **recording** (`?replay=…`), except the last one. A recording runs the same way every take, needs no network and spends no credits. All names and ids are fictional demo data.

## Before recording
- Run `.\run.ps1`. Open `http://127.0.0.1:8000/` in a clean browser window at 1440×900 or larger, zoom 100%, bookmarks bar hidden.
- Record the window with **Win + Alt + R** (Xbox Game Bar), or any screen recorder. Record each shot as its own clip; that makes the edit easier.
- In a recording, **Space** pauses and the sidebar's **1× / 2× / 4×** button changes speed. Record at 1×.
- Recordings can't approve or send. Shots that need **Approve** or **Send** must be live (shot 11). A live case spends credits.
- Captions: put them at the bottom, 1–2 lines, on screen for at least 3 s. The exact text is below and in `demo-video-captions.srt`.

## Shots

| # | time | open / click | caption (on screen) | voice-over (optional) |
|---|---|---|---|---|
| 1 | 0:00–0:10 | `/` (the **Inbox**) | Money complaints reach support by call, ticket and email, in many languages. | Support teams get money complaints every day, in many languages. |
| 2 | 0:10–0:30 | `/?replay=s1_zombie_rent`, let it play | A shop owner says, in Hindi, that rent is still cut after the Soundbox went back. Munim follows the money: ledger, mandate, device, pickup. | Munim reads the complaint and checks every record behind it. |
| 3 | 0:30–0:50 | **How Munim decided → Decision** | The AI asked for ₹1,497. The rules recomputed ₹998 from the ledger and refunded that. | The AI proposes, but code decides the amount. |
| 4 | 0:50–1:00 | close the panel, point at the draft reply | The reply is in Hindi and waits as a draft. Nothing reaches the merchant until a person presses Send. | |
| 5 | 1:00–1:12 | the line **Same bug found in 36 more merchants** → **Review** | Same bug found in 36 more merchants (₹32,029) before they complain. A person reviews each one. | One complaint finds every merchant with the same bug. |
| 6 | 1:12–1:30 | `/?replay=s2_double_billing`, then **Needs you** | Charged twice for one device: ₹2,495. That's over the ₹2,000 auto-limit, so a person approves. | Big refunds always go to a person. |
| 7 | 1:30–1:45 | `/?replay=s7_prompt_injection` → **Decision** | Fake admin demands ₹50,000. No evidence, so it is blocked. | Typed instructions can't move money. |
| 8 | 1:45–2:00 | `/?replay=s8_cold_case` → **Proof** | No known cause fits. The AI writes read-only SQL and finds a chargeback, then hands it to the payments team. | When nothing fits, it digs, but it doesn't guess. |
| 9 | 2:00–2:25 | `/?replay=s10_bus_turned_back` → **How Munim decided → Proof** | A bus turned back at km 38, but the operator never marked it cancelled. GPS and the driver's report prove it. The ₹1,640 fare is refunded. | The same engine works for travel refunds. |
| 10 | 2:25–2:45 | `/?replay=s11_flight_refund`, then **Needs you** | The airline paid the ₹21,860 refund on 3 Oct, but it was never matched to the booking. A person approves it. 8 more passengers are found. | |
| 11 | 2:45–3:05 | **live**: **Merchant app** → **Gupta General Store** → OTP 123456 → chip **Why was ₹499 cut?** | Shop owners can ask Munim directly. It can book a pickup, but it never moves money from the app. | The merchant side sees only their own shop. |
| 12 | 3:05–3:12 | back to the **Inbox** | AI proposes. Code decides. A person signs off on big money. | |

## Tips
- To leave a recording, press **✕** next to the replay controls in the sidebar.
- If shot 11 can't be live, record shots 1–10 only. The video still covers the full flow.
- S10's complaint is in Telugu, and Munim shows its English reading under it. Pause there for a second.
- The travel start chips sit under **New chat → More** (*Bus turned back, no refund*, *Airline refund never arrived*). These run live.
