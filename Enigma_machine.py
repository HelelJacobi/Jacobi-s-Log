import tkinter as tk
from tkinter import ttk

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# ------------------ ENIGMA CORE ------------------

ROTOR_WIRINGS = {
    "I":   ("EKMFLGDQVZNTOWYHXUSPAIBRCJ", "Q"),
    "II":  ("AJDKSIRUXBLHWTMCQGZNPYFVOE", "E"),
    "III": ("BDFHJLCPRTXVZNYEIWGAKMUSQO", "V"),
    "IV":  ("ESOVPZJAYQUIRHXLNFTGKDCMWB", "J"),
    "V":   ("VZBRGITYUPSDNHLXAWMJQOFECK", "Z"),
}

REFLECTOR_B = "YRUHQSLDPXNGOKMIEBFZCWVJAT"

def char_to_index(c):
    return ord(c) - 65

def index_to_char(i):
    return chr(i + 65)

class Rotor:
    def __init__(self, wiring, notch, ring=0, position=0):
        self.wiring = wiring
        self.inverse = [wiring.index(c) for c in ALPHABET]
        self.notch = char_to_index(notch)
        self.ring = ring
        self.position = position

    def step(self):
        self.position = (self.position + 1) % 26

    def at_notch(self):
        return self.position == self.notch

    def encode_forward(self, c):
        offset = (c + self.position - self.ring) % 26
        return (char_to_index(self.wiring[offset]) - self.position + self.ring) % 26

    def encode_backward(self, c):
        offset = (c + self.position - self.ring) % 26
        return (self.inverse[offset] - self.position + self.ring) % 26

class EnigmaMachine:
    def __init__(self, rotors):
        self.rotors = rotors
        self.reflector = [char_to_index(c) for c in REFLECTOR_B]

    def step_rotors(self):
        # Double stepping mechanism
        if self.rotors[1].at_notch():
            self.rotors[0].step()
            self.rotors[1].step()
        if self.rotors[2].at_notch():
            self.rotors[1].step()
        self.rotors[2].step()

    def encrypt_char(self, char):
        if char not in ALPHABET:
            return char
        self.step_rotors()
        c = char_to_index(char)
        for r in reversed(self.rotors):
            c = r.encode_forward(c)
        c = self.reflector[c]
        for r in self.rotors:
            c = r.encode_backward(c)
        return index_to_char(c)

    def encrypt_text(self, text):
        return "".join(self.encrypt_char(c.upper()) if c.upper() in ALPHABET else c for c in text)

# ------------------ GUI ------------------

class EnigmaGUI:
    def __init__(self, root):
        self.root = root
        root.title("Enigma Machine")
        root.configure(bg="#111")

        # Labels
        tk.Label(root, text="Input Text", bg="#111", fg="white").pack(anchor="w", padx=10)
        self.text_in = tk.Text(root, height=4, bg="#222", fg="white", insertbackground="white")
        self.text_in.pack(fill="x", padx=10, pady=2)

        tk.Label(root, text="Output Text", bg="#111", fg="white").pack(anchor="w", padx=10)
        self.text_out = tk.Text(root, height=4, bg="#222", fg="lime")
        self.text_out.pack(fill="x", padx=10, pady=2)

        # Rotor Controls
        control_frame = tk.Frame(root, bg="#111")
        control_frame.pack(pady=5)

        tk.Label(control_frame, text="Rotor", bg="#111", fg="white").grid(row=0, column=0)
        tk.Label(control_frame, text="Start Pos", bg="#111", fg="white").grid(row=1, column=0)
        tk.Label(control_frame, text="Ring", bg="#111", fg="white").grid(row=2, column=0)

        self.rotor_vars = []
        self.pos_vars = []
        self.ring_vars = []

        LETTER_OPTIONS = list(ALPHABET)
        ROTOR_OPTIONS = list(ROTOR_WIRINGS.keys())

        for i in range(3):
            rv = tk.StringVar(value=ROTOR_OPTIONS[i])
            pv = tk.StringVar(value='A')
            rg = tk.IntVar(value=0)
            self.rotor_vars.append(rv)
            self.pos_vars.append(pv)
            self.ring_vars.append(rg)

            ttk.Combobox(control_frame, textvariable=rv,
                         values=ROTOR_OPTIONS, width=5).grid(row=0, column=i+1)
            ttk.Combobox(control_frame, textvariable=pv,
                         values=LETTER_OPTIONS, width=4).grid(row=1, column=i+1)
            tk.Spinbox(control_frame, from_=0, to=25, width=4,
                       textvariable=rg).grid(row=2, column=i+1)

        # Buttons
        button_frame = tk.Frame(root, bg="#111")
        button_frame.pack(pady=5)
        tk.Button(button_frame, text="Process", command=self.process_text).pack(side="left", padx=5)
        tk.Button(button_frame, text="Reset", command=self.reset_text).pack(side="left", padx=5)

        # Lampboard
        self.lamps = {}
        lamp_frame = tk.Frame(root, bg="#111")
        lamp_frame.pack(pady=10)
        for i, c in enumerate(ALPHABET):
            lbl = tk.Label(lamp_frame, text=c, width=3,
                           bg="#333", fg="white", relief="ridge")
            lbl.grid(row=i//13, column=i%13, padx=2, pady=2)
            self.lamps[c] = lbl

        root.bind("<Key>", self.keypress)

    def build_machine(self):
        rotors = []
        for i in range(3):
            name = self.rotor_vars[i].get()
            wiring, notch = ROTOR_WIRINGS[name]
            position = ALPHABET.index(self.pos_vars[i].get())
            rotors.append(Rotor(wiring, notch,
                                 ring=self.ring_vars[i].get(),
                                 position=position))
        return EnigmaMachine(rotors)

    def light_lamp(self, c):
        for lamp in self.lamps.values():
            lamp.configure(bg="#333")
        if c in self.lamps:
            self.lamps[c].configure(bg="yellow")

    # GUI Actions
    def keypress(self, event):
        if not event.char.isalpha():
            return
        self.root.after(1, self.process_text)
        # char = event.char.upper()
        # self.text_in.insert("end", char)
        # self.process_text(live_char=char)

    def process_text(self, live_char=None):
        machine = self.build_machine()
        plaintext = self.text_in.get("1.0", "end").strip()
        if not plaintext:
            return
        ciphertext = machine.encrypt_text(plaintext)
        self.text_out.delete("1.0", "end")
        self.text_out.insert("1.0", ciphertext)
        if live_char:
            self.light_lamp(ciphertext[-1])

    def reset_text(self):
        self.text_in.delete("1.0", "end")
        self.text_out.delete("1.0", "end")
        self.light_lamp("")

# ------------------ RUN ------------------

if __name__ == "__main__":
    root = tk.Tk()
    EnigmaGUI(root)
    root.mainloop()
