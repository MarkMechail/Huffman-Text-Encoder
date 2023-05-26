import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import heapq
import pickle


def browse_input_file():
    input_file_path.set(filedialog.askopenfilename())


def browse_output_file():
    output_file_path.set(filedialog.asksaveasfilename())


def compress():
    input_text = input_data_textbox.get("1.0", tk.END)
    encoded_text = huffman_encode_text(input_text)
    output_data_textbox.delete("1.0", tk.END)
    output_data_textbox.insert(tk.END, encoded_text.hex())

    # Get input and output data sizes
    input_data_size = len(input_text)
    output_data_size = len(encoded_text)

    # Update size labels
    input_data_size_label.config(text=f"Input Data Size: {input_data_size} bytes")
    output_data_size_label.config(text=f"Output Data Size: {output_data_size} bytes")

    input_filepath = input_file_path.get()
    output_filepath = output_file_path.get()
    if input_filepath and output_filepath:
        huffman_encode_file(input_filepath, output_filepath)


def decompress():
    encoded_text_hex = output_data_textbox.get("1.0", tk.END)
    encoded_text = bytes.fromhex(encoded_text_hex.strip())
    decoded_text = huffman_decode_text(encoded_text)
    input_data_textbox.delete("1.0", tk.END)
    input_data_textbox.insert(tk.END, decoded_text)

    # Get input and output datasizes
    input_data_size = len(encoded_text)
    output_data_size = len(decoded_text)

    # Update size labels
    input_data_size_label.config(text=f"Input Data Size: {input_data_size} bytes")
    output_data_size_label.config(text=f"Output Data Size: {output_data_size} bytes")

    input_filepath = input_file_path.get()
    output_filepath = output_file_path.get()
    if input_filepath and output_filepath:
        huffman_decode_file(input_filepath, output_filepath)


class Node:
    def __init__(self, char=None, freq=None, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq


def build_huffman_tree(freqs):
    heap = [Node(char=byte, freq=freq) for byte, freq in freqs.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        parent = Node(freq=left.freq + right.freq, left=left, right=right)
        heapq.heappush(heap, parent)

    return heap[0]


def build_huffman_codes(tree, prefix='', codes=None):
    if codes is None:
        codes = {}

    if tree.char is not None:
        codes[tree.char] = prefix
    else:
        build_huffman_codes(tree.left, prefix + '0', codes)
        build_huffman_codes(tree.right, prefix + '1', codes)

    return codes


def huffman_encode_text(text):
    data = text.encode()

    freqs = {}
    for byte in data:
        if byte not in freqs:
            freqs[byte] = 0
        freqs[byte] += 1

    huffman_tree = build_huffman_tree(freqs)
    huffman_codes = build_huffman_codes(huffman_tree)

    encoded_data = ''.join(huffman_codes[byte] for byte in data)
    padding_len = 8 - len(encoded_data) % 8
    padded_encoded_data = encoded_data + ('0' * padding_len)

    freqs_pickle = pickle.dumps(freqs)
    freqs_pickle_len = len(freqs_pickle).to_bytes(4, 'big')
    padding_len_byte = padding_len.to_bytes(1, 'big')

    encoded_bytes = bytearray()
    for i in range(0, len(padded_encoded_data), 8):
        byte = int(padded_encoded_data[i:i + 8], 2)
        encoded_bytes.append(byte)

    return freqs_pickle_len + freqs_pickle + padding_len_byte + bytes(encoded_bytes)


def huffman_decode_text(encoded_text):
    encoded_bytes = bytearray(encoded_text)

    freqs_pickle_len = int.from_bytes(encoded_bytes[:4], 'big')
    freqs_pickle = bytes(encoded_bytes[4:4 + freqs_pickle_len])
    freqs = pickle.loads(freqs_pickle)

    padding_len = int.from_bytes(encoded_bytes[4 + freqs_pickle_len:4 + freqs_pickle_len + 1], 'big')
    encoded_data = ''.join(f'{byte:08b}' for byte in encoded_bytes[4 + freqs_pickle_len + 1:])

    huffman_tree = build_huffman_tree(freqs)
    decoded_data = []
    current_node = huffman_tree

    for bit in encoded_data[:-padding_len]:
        current_node = current_node.left if bit == '0' else current_node.right

        if current_node.char is not None:
            decoded_data.append(current_node.char)
            current_node = huffman_tree

    return bytearray(decoded_data).decode()


def huffman_encode_file(input_file_path, output_file_path):
    with open(input_file_path, 'r') as input_file, open(output_file_path, 'wb') as output_file:
        text = input_file.read()
        encoded_text = huffman_encode_text(text)
        output_file.write(encoded_text)


def huffman_decode_file(input_file_path, output_file_path):
    with open(input_file_path, 'rb') as input_file, open(output_file_path, 'w') as output_file:
        encoded_text = input_file.read()
        decoded_text = huffman_decode_text(encoded_text)
        output_file.write(decoded_text)


app = tk.Tk()
app.title("Huffman Text Encoder & Decoder")

input_file_path = tk.StringVar()
output_file_path = tk.StringVar()

# Input File
input_label = tk.Label(app, text="Input File:")
input_label.grid(row=0, column=0, padx=5, pady=5)

input_entry = tk.Entry(app, textvariable=input_file_path)
input_entry.grid(row=0, column=1, padx=5, pady=5)

input_browse_button = tk.Button(app, text="Browse", command=browse_input_file)
input_browse_button.grid(row=0, column=2, padx=5, pady=5)

# Output File
output_label = tk.Label(app, text="Output File:")
output_label.grid(row=1, column=0, padx=5, pady=5)

output_entry = tk.Entry(app, textvariable=output_file_path)
output_entry.grid(row=1, column=1, padx=5, pady=5)

output_browse_button = tk.Button(app, text="Browse", command=browse_output_file)
output_browse_button.grid(row=1, column=2, padx=5, pady=5)

# Separator
separator = ttk.Separator(app, orient='horizontal')
separator.grid(row=2, column=0, columnspan=3, sticky='ew', padx=5, pady=10)

# Input Data
input_data_label = tk.Label(app, text="Input Data")
input_data_label.grid(row=3, column=0, padx=5, pady=5)

input_data_textbox = tk.Text(app, wrap=tk.WORD, width=40, height=10)
input_data_textbox.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

# Output Data
output_data_label = tk.Label(app, text="Output Data")
output_data_label.grid(row=6, column=0, padx=5, pady=5)

output_data_textbox = tk.Text(app, wrap=tk.WORD, width=40, height=10)
output_data_textbox.grid(row=7, column=0, columnspan=3, padx=5, pady=5)

# Compress and Decompress Buttons
compress_button = tk.Button(app, text="Compress", width=15, command=compress)
compress_button.grid(row=9, column=1, padx=5, pady=5)

decompress_button = tk.Button(app, text="Decompress", width=15, command=decompress)
decompress_button.grid(row=9, column=2, padx=5, pady=5)

# Input Data Size Label
input_data_size_label = tk.Label(app, text="Input Data Size: 0 bytes")
input_data_size_label.grid(row=5, column=1, padx=5, pady=5, sticky='w')

# Output Data Size Label
output_data_size_label = tk.Label(app, text="Output Data Size: 0 bytes")
output_data_size_label.grid(row=8, column=1, padx=5, pady=5, sticky='w')

app.mainloop()
