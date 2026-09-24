import math
import tkinter as tk
from tkinter import messagebox
import webbrowser

# ==========================================
# SERVICE DATA
# ==========================================
SOLUTIONS = {
    "puncture": {
        "title": "🛞 Tyre Puncture Repair",
        "description": "Your description indicates a possible tyre or wheel problem. Find the nearest puncture repair shop.",
        "url": "https://www.google.com/maps/search/puncture+shop+near+me",
    },
    "fuel": {
        "title": "⛽ Fuel Emergency",
        "description": "Your vehicle may have run out of fuel. Find the nearest petrol/diesel station.",
        "url": "https://www.google.com/maps/search/petrol+pump+near+me",
    },
    "mechanic": {
        "title": "🔧 Engine Breakdown & Mechanical",
        "description": "A mechanical or engine problem may require professional inspection. Find a nearby mechanic.",
        "url": "https://www.google.com/maps/search/auto+mechanic+near+me",
    },
    "towing": {
        "title": "🚛 Flatbed Towing Service",
        "description": "Your vehicle may require recovery or towing. Find a nearby towing service.",
        "url": "https://www.google.com/maps/search/towing+service+near+me",
    },
}

# ==========================================
# MOCK SERVICE PROVIDER DATA
# ==========================================
VENDORS = [
    {
        "name": "Express 24/7 Tyre Care",
        "type": "puncture",
        "latOffset": 0.008,
        "lonOffset": 0.005,
        "rating": 4.8,
        "phone": "+919876543210",
    },
    {
        "name": "Apex Roadside Mechanic",
        "type": "mechanic",
        "latOffset": -0.012,
        "lonOffset": 0.009,
        "rating": 4.6,
        "phone": "+919876543211",
    },
    {
        "name": "Highway Fuel & Petrol Outlet",
        "type": "fuel",
        "latOffset": 0.015,
        "lonOffset": -0.010,
        "rating": 4.3,
        "phone": "+919876543212",
    },
    {
        "name": "QuickLift Recovery Towing",
        "type": "towing",
        "latOffset": -0.020,
        "lonOffset": -0.015,
        "rating": 4.9,
        "phone": "+919876543213",
    },
]

# Default Fallback Coordinates (Visakhapatnam, AP)
USER_COORDS = {"lat": 17.6868, "lon": 83.2185}


# ==========================================
# HAVERSINE DISTANCE CALCULATOR
# ==========================================
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)

    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(
        math.radians(lat2)
    ) * math.sin(d_lon / 2) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


# ==========================================
# SMART ASSIST GUI APPLICATION
# ==========================================
class SmartAssistApp(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("SmartAssist AI - Road SOS")
        self.geometry("520x760")
        self.configure(bg="#0b0f19")

        # System State
        self.current_solution_url = ""

        # UI Initialization
        self.build_ui()
        self.rank_and_render_vendors()

    def build_ui(self):
        # Container setup
        main_frame = tk.Frame(self, bg="#0b0f19")
        main_frame.pack(fill="both", expand=True, padx=14, pady=14)

        # Title Block
        badge = tk.Label(
            main_frame,
            text="🤖 AI & DATA SCIENCE POWERED",
            bg="#1e1e38",
            fg="#818cf8",
            font=("Segoe UI", 8, "bold"),
            padx=8,
            pady=3,
        )
        badge.pack(anchor="w", pady=(0, 4))

        title = tk.Label(
            main_frame,
            text="SmartAssist Road SOS",
            bg="#0b0f19",
            fg="#38bdf8",
            font=("Segoe UI", 16, "bold"),
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            main_frame,
            text="Real-time incident classification & smart roadside solution.",
            bg="#0b0f19",
            fg="#94a3b8",
            font=("Segoe UI", 9),
        )
        subtitle.pack(anchor="w", pady=(0, 12))

        # NLP Triage Section
        ai_box = tk.Frame(
            main_frame, bg="#1a243d", bd=1, relief="solid", highlightthickness=0
        )
        ai_box.pack(fill="x", pady=(0, 12), ipadx=10, ipady=10)

        lbl_symptom = tk.Label(
            ai_box,
            text="Describe what happened:",
            bg="#1a243d",
            fg="#cbd5e1",
            font=("Segoe UI", 9, "bold"),
        )
        lbl_symptom.pack(anchor="w", pady=(0, 6))

        input_frame = tk.Frame(ai_box, bg="#1a243d")
        input_frame.pack(fill="x")

        self.symptom_entry = tk.Entry(
            input_frame,
            bg="#0b0f19",
            fg="#ffffff",
            insertbackground="white",
            relief="flat",
            font=("Segoe UI", 9),
        )
        self.symptom_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=6)
        self.symptom_entry.bind("<Return>", lambda event: self.analyze_symptom())

        btn_classify = tk.Button(
            input_frame,
            text="Classify",
            bg="#6366f1",
            fg="#ffffff",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.analyze_symptom,
        )
        btn_classify.pack(side="right", padx=(8, 0), ipadx=10, ipady=3)

        # AI Diagnosis Result Area (Hidden initially)
        self.diag_box = tk.Frame(ai_box, bg="#0b0f19", bd=1, relief="solid")

        self.lbl_diag_issue = tk.Label(
            self.diag_box,
            text="🤖 Predicted Issue: -",
            bg="#0b0f19",
            fg="#ffffff",
            font=("Segoe UI", 8, "bold"),
            anchor="w",
        )
        self.lbl_diag_issue.pack(fill="x", padx=8, pady=(8, 2))

        self.lbl_diag_risk = tk.Label(
            self.diag_box,
            text="⚠️ Risk Level: -",
            bg="#0b0f19",
            fg="#ffffff",
            font=("Segoe UI", 8),
            anchor="w",
        )
        self.lbl_diag_risk.pack(fill="x", padx=8, pady=2)

        self.lbl_diag_conf = tk.Label(
            self.diag_box,
            text="🎯 Confidence: -",
            bg="#0b0f19",
            fg="#ffffff",
            font=("Segoe UI", 8),
            anchor="w",
        )
        self.lbl_diag_conf.pack(fill="x", padx=8, pady=2)

        self.lbl_diag_action = tk.Label(
            self.diag_box,
            text="-",
            bg="#0b0f19",
            fg="#94a3b8",
            font=("Segoe UI", 8),
            wraplength=440,
            justify="left",
        )
        self.lbl_diag_action.pack(fill="x", padx=8, pady=(4, 8))

        # Recommended Solution Box
        sol_box = tk.Frame(self.diag_box, bg="#172554", bd=1, relief="solid")
        sol_box.pack(fill="x", padx=8, pady=(0, 8), ipadx=6, ipady=6)

        tk.Label(
            sol_box,
            text="🛠️ Recommended Solution",
            bg="#172554",
            fg="#60a5fa",
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w")

        self.lbl_sol_desc = tk.Label(
            sol_box,
            text="-",
            bg="#172554",
            fg="#cbd5e1",
            font=("Segoe UI", 8),
            wraplength=420,
            justify="left",
        )
        self.lbl_sol_desc.pack(anchor="w", pady=4)

        self.btn_solve = tk.Button(
            sol_box,
            text="🚨 Solve Now",
            bg="#10b981",
            fg="#ffffff",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            cursor="hand2",
            command=self.open_solution_url,
        )
        self.btn_solve.pack(fill="x", pady=(4, 0))

        # Standard Service Buttons
        grid_frame = tk.Frame(main_frame, bg="#0b0f19")
        grid_frame.pack(fill="x", pady=(0, 12))

        services = [
            ("🛞 Tyre Puncture Repair", "#ef4444", SOLUTIONS["puncture"]["url"]),
            ("⛽ Fuel Emergency", "#0284c7", SOLUTIONS["fuel"]["url"]),
            ("🔧 Engine Breakdown & Mechanical", "#10b981", SOLUTIONS["mechanic"]["url"]),
            ("🚛 Flatbed Towing Service", "#8b5cf6", SOLUTIONS["towing"]["url"]),
        ]

        for label, color, url in services:
            btn = tk.Button(
                grid_frame,
                text=f"{label}   ➔",
                bg=color,
                fg="#ffffff",
                font=("Segoe UI", 9, "bold"),
                relief="flat",
                anchor="w",
                cursor="hand2",
                command=lambda u=url: webbrowser.open(u),
            )
            btn.pack(fill="x", pady=3, ipady=4, padx=2)

        # Ranked Responders Section
        ranked_hdr = tk.Frame(main_frame, bg="#0b0f19")
        ranked_hdr.pack(fill="x", pady=(6, 4))

        tk.Label(
            ranked_hdr,
            text="Smart-Ranked Local Responders",
            bg="#0b0f19",
            fg="#cbd5e1",
            font=("Segoe UI", 10, "bold"),
        ).pack(side="left")

        btn_sync = tk.Label(
            ranked_hdr,
            text="📍 Sync GPS",
            bg="#0b0f19",
            fg="#38bdf8",
            font=("Segoe UI", 8, "bold"),
            cursor="hand2",
        )
        btn_sync.pack(side="right")
        btn_sync.bind("<Button-1>", lambda e: self.rank_and_render_vendors())

        self.vendor_container = tk.Frame(main_frame, bg="#0b0f19")
        self.vendor_container.pack(fill="x")

        # Telemetry Bar
        self.lbl_telemetry = tk.Label(
            main_frame,
            text="Telemetry: Lat/Lon: Acquiring... | Vector Confidence: Null",
            bg="#0b0f19",
            fg="#64748b",
            font=("Consolas", 8),
            anchor="w",
        )
        self.lbl_telemetry.pack(fill="x", pady=(12, 0))

    # ==========================================
    # SYMPTOM CLASSIFICATION LOGIC
    # ==========================================
    def analyze_symptom(self):
        text = self.symptom_entry.get().lower().strip()

        if not text:
            messagebox.showwarning(
                "Input Required", "Please describe what happened."
            )
            return

        self.diag_box.pack(fill="x", pady=(10, 0))

        classes = [
            {
                "key": "puncture",
                "words": [
                    "puncture",
                    "flat tyre",
                    "flat tire",
                    "tyre",
                    "tire",
                    "wheel",
                    "tube",
                    "air leak",
                ],
                "risk": "Low",
                "action": "Park safely, switch on hazard lights and avoid driving on the damaged tyre.",
            },
            {
                "key": "fuel",
                "words": [
                    "fuel",
                    "petrol",
                    "diesel",
                    "empty",
                    "gas",
                    "ran out",
                    "no fuel",
                ],
                "risk": "Medium",
                "action": "Move the vehicle to a safe location and avoid repeated engine cranking.",
            },
            {
                "key": "mechanic",
                "words": [
                    "smoke",
                    "engine",
                    "heat",
                    "overheating",
                    "noise",
                    "clutch",
                    "brake",
                    "oil",
                    "battery",
                ],
                "risk": "High",
                "action": "Switch off the engine if it is overheating, smoking or behaving abnormally.",
            },
            {
                "key": "towing",
                "words": [
                    "accident",
                    "towing",
                    "stuck",
                    "dead battery",
                    "wont start",
                    "won't start",
                    "transmission",
                    "crash",
                ],
                "risk": "Critical",
                "action": "Move away from traffic when safe and request roadside recovery assistance.",
            },
        ]

        max_matches = 0
        predicted = None

        for c in classes:
            matches = sum(1 for word in c["words"] if word in text)
            if matches > max_matches:
                max_matches = matches
                predicted = c

        if not predicted:
            predicted = {
                "key": "mechanic",
                "risk": "Moderate",
                "action": "The problem could not be classified confidently. A professional mechanic should inspect the vehicle.",
            }
            max_matches = 1

        confidence = f"{min(96, max(65, max_matches * 28))}%"

        # Update Display Labels
        solution_info = SOLUTIONS[predicted["key"]]
        self.lbl_diag_issue.config(
            text=f"🤖 Predicted Issue: {solution_info['title']}"
        )
        self.lbl_diag_risk.config(text=f"⚠️ Risk Level: {predicted['risk']}")
        self.lbl_diag_conf.config(text=f"🎯 Confidence: {confidence}")
        self.lbl_diag_action.config(
            text=f"💡 Recommendation: {predicted['action']}"
        )

        self.lbl_sol_desc.config(text=solution_info["description"])
        self.btn_solve.config(text=f"🚨 {solution_info['title']} - Find Nearby")
        self.current_solution_url = solution_info["url"]

        self.update_telemetry(
            USER_COORDS["lat"], USER_COORDS["lon"], predicted["key"], confidence
        )

    def open_solution_url(self):
        if self.current_solution_url:
            webbrowser.open(self.current_solution_url)

    # ==========================================
    # VENDOR RANKING ENGINE
    # ==========================================
    def rank_and_render_vendors(self):
        for widget in self.vendor_container.winfo_children():
            widget.destroy()

        ranked = []
        for v in VENDORS:
            v_lat = USER_COORDS["lat"] + v["latOffset"]
            v_lon = USER_COORDS["lon"] + v["lonOffset"]

            distance = calculate_distance(
                USER_COORDS["lat"], USER_COORDS["lon"], v_lat, v_lon
            )
            ai_score = round((v["rating"] * 1.5) - (distance * 0.4), 2)
            eta = round(distance * 3.5 + 4)

            ranked.append(
                {
                    **v,
                    "distance": distance,
                    "aiScore": ai_score,
                    "eta": eta,
                }
            )

        ranked.sort(key=lambda x: x["aiScore"], reverse=True)

        for v in ranked:
            card = tk.Frame(
                self.vendor_container,
                bg="#1a243d",
                bd=1,
                relief="solid",
                highlightthickness=0,
            )
            card.pack(fill="x", pady=3, ipadx=8, ipady=6)

            info_frame = tk.Frame(card, bg="#1a243d")
            info_frame.pack(side="left", fill="x", expand=True)

            tk.Label(
                info_frame,
                text=v["name"],
                bg="#1a243d",
                fg="#f8fafc",
                font=("Segoe UI", 9, "bold"),
            ).pack(anchor="w")

            meta = f"⭐ {v['rating']} • 📍 {v['distance']} km away • ⏱️ ETA: ~{v['eta']} mins"
            tk.Label(
                info_frame,
                text=meta,
                bg="#1a243d",
                fg="#94a3b8",
                font=("Segoe UI", 7),
            ).pack(anchor="w")

            tk.Label(
                info_frame,
                text=f"AI Match Score: {v['aiScore']}",
                bg="#1a243d",
                fg="#38bdf8",
                font=("Segoe UI", 7, "bold"),
            ).pack(anchor="w")

            btn_call = tk.Button(
                card,
                text="Call",
                bg="#10b981",
                fg="#ffffff",
                font=("Segoe UI", 8, "bold"),
                relief="flat",
                cursor="hand2",
                command=lambda p=v["phone"]: webbrowser.open(f"tel:{p}"),
            )
            btn_call.pack(side="right", padx=4)

        self.update_telemetry(
            USER_COORDS["lat"], USER_COORDS["lon"], "Ready", "N/A"
        )

    def update_telemetry(self, lat, lon, intent, conf):
        self.lbl_telemetry.config(
            text=f"Telemetry: Lat: {lat:.4f}, Lon: {lon:.4f} | Intent: {intent} | Conf: {conf}"
        )


if __name__ == "__main__":
    app = SmartAssistApp()
    app.mainloop()